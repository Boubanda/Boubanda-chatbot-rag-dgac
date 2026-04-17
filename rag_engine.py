import os
import shutil
import hashlib
import logging
import time
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

from config import (
    GROQ_API_KEY, GROQ_MODEL, EMBEDDING_MODEL,
    CHROMA_PATH, CHUNK_SIZE, CHUNK_OVERLAP,
    TOP_K_RESULTS, SYSTEM_PROMPT,
    CACHE_ENABLED, CACHE_SIZE,
    ENABLE_LOGGING, LOG_FILE
)

if ENABLE_LOGGING:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


class RAGEngine:
    def __init__(self):
        print("Initialisation RAG — Groq + Embeddings locaux...")

        self.response_cache = {} if CACHE_ENABLED else None
        self.cache_max_size = CACHE_SIZE
        self.stats = {
            "total_queries": 0,
            "cache_hits": 0,
            "avg_response_time": 0,
            "total_time": 0
        }

        # Embeddings 100% locaux — rapides et gratuits
        print("Chargement embeddings locaux...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )

        # Groq LLM — ultra rapide
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model_name=GROQ_MODEL,
            temperature=0.1,
            max_tokens=1500
        )

        self.vectorstore = None
        self._load_existing_vectorstore()
        print(f"Modèle LLM : {GROQ_MODEL}")
        print("RAG prêt !")

    def _get_cache_key(self, question: str) -> str:
        return hashlib.md5(question.lower().strip().encode()).hexdigest()

    def _update_stats(self, response_time: float, cache_hit: bool = False):
        self.stats["total_queries"] += 1
        if cache_hit:
            self.stats["cache_hits"] += 1
        self.stats["total_time"] += response_time
        self.stats["avg_response_time"] = (
            self.stats["total_time"] / self.stats["total_queries"]
        )

    def _load_existing_vectorstore(self):
        if os.path.exists(CHROMA_PATH) and os.listdir(CHROMA_PATH):
            try:
                self.vectorstore = Chroma(
                    persist_directory=CHROMA_PATH,
                    embedding_function=self.embeddings,
                    collection_name="dgac_documents"
                )
                count = self.vectorstore._collection.count()
                if count == 0:
                    self.vectorstore = None
                else:
                    print(f"Base chargée : {count} chunks")
            except Exception as e:
                print(f"Base non chargeable : {e}")
                self.vectorstore = None

    def load_documents(self, pdf_paths: List[str]) -> int:
        print("Indexation des documents...")
        start_time = time.time()
        all_docs = []

        for pdf_path in pdf_paths:
            if not os.path.exists(pdf_path):
                continue
            try:
                loader = PyPDFLoader(pdf_path)
                docs = loader.load()
                for doc in docs:
                    doc.metadata["source_file"] = Path(pdf_path).name
                    doc.metadata["indexed_at"] = datetime.now().isoformat()
                all_docs.extend(docs)
                print(f"{Path(pdf_path).name} ({len(docs)} pages)")
            except Exception as e:
                print(f"Erreur : {e}")

        if not all_docs:
            return 0

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", " "]
        )
        chunks = splitter.split_documents(all_docs)
        print(f"{len(chunks)} chunks créés")

        if self.vectorstore is None:
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=CHROMA_PATH,
                collection_name="dgac_documents"
            )
        else:
            self.vectorstore.add_documents(chunks)

        elapsed = time.time() - start_time
        print(f"Indexation terminée en {elapsed:.1f}s")
        return len(chunks)

    def query(self, question: str) -> Dict[str, Any]:
        start_time = time.time()

        # Cache
        if CACHE_ENABLED and self.response_cache is not None:
            cache_key = self._get_cache_key(question)
            if cache_key in self.response_cache:
                self._update_stats(time.time() - start_time, cache_hit=True)
                print("Réponse du cache")
                return self.response_cache[cache_key]

        if self.vectorstore is None:
            return {
                "answer": "Aucun document chargé. Uploadez un PDF dans la barre latérale.",
                "sources": [], "confidence": 0, "response_time": 0
            }

        try:
            retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": TOP_K_RESULTS}
            )
            relevant_docs = retriever.invoke(question)

            if not relevant_docs:
                return {
                    "answer": "Information non trouvée dans les documents.",
                    "sources": [], "confidence": 0,
                    "response_time": round(time.time() - start_time, 1)
                }

            context = "\n\n---\n\n".join([
                f"[{doc.metadata.get('source_file', '?')} "
                f"p.{doc.metadata.get('page', 0) + 1}]\n"
                f"{doc.page_content[:600]}"
                for doc in relevant_docs
            ])

            prompt = f"""{SYSTEM_PROMPT}

DOCUMENTS :
{context}

QUESTION : {question}

RÉPONSE :"""

            response = self.llm.invoke(prompt)
            answer = response.content
            elapsed = round(time.time() - start_time, 1)

            sources = []
            seen = set()
            for doc in relevant_docs:
                key = (f"{doc.metadata.get('source_file', '?')}"
                       f"-p{doc.metadata.get('page', 0)}")
                if key not in seen:
                    seen.add(key)
                    sources.append({
                        "file": doc.metadata.get("source_file", "Inconnu"),
                        "page": doc.metadata.get("page", 0) + 1,
                        "excerpt": doc.page_content[:200] + "..."
                    })

            confidence = min(len(relevant_docs) / TOP_K_RESULTS * 100, 100)

            result = {
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "response_time": elapsed
            }

            # Sauvegarder dans le cache
            if CACHE_ENABLED and self.response_cache is not None:
                cache_key = self._get_cache_key(question)
                if len(self.response_cache) >= self.cache_max_size:
                    oldest = next(iter(self.response_cache))
                    del self.response_cache[oldest]
                self.response_cache[cache_key] = result

            self._update_stats(elapsed)
            if ENABLE_LOGGING:
                logging.info(
                    f"Question: {question[:80]} | "
                    f"Temps: {elapsed}s | Sources: {len(sources)}"
                )
            return result

        except Exception as e:
            print(f"Erreur query : {e}")
            return {
                "answer": f"Erreur : {str(e)}",
                "sources": [], "confidence": 0,
                "response_time": round(time.time() - start_time, 1)
            }

    def get_stats(self) -> dict:
        stats = {"chunks": 0, "status": "Aucun document"}
        if self.vectorstore is not None:
            try:
                count = self.vectorstore._collection.count()
                stats = {"chunks": count, "status": "Actif"}
            except Exception:
                pass
        stats.update({
            "total_queries": self.stats["total_queries"],
            "cache_hits": self.stats["cache_hits"],
            "cache_ratio": (
                self.stats["cache_hits"] /
                self.stats["total_queries"] * 100
                if self.stats["total_queries"] > 0 else 0
            ),
            "avg_response_time": self.stats["avg_response_time"]
        })
        return stats

    def clear_cache(self):
        if self.response_cache is not None:
            self.response_cache.clear()

    def clear(self):
        if os.path.exists(CHROMA_PATH):
            shutil.rmtree(CHROMA_PATH)
            self.vectorstore = None
        if ENABLE_LOGGING:
            logging.info("Vectorstore cleared")
