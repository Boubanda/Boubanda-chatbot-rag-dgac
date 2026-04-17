import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Groq API ──────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("MISTRAL_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"

# ── Alias compatibilité app.py ────────────────────────────────────────────────
MISTRAL_MODEL = GROQ_MODEL
OLLAMA_MODEL = GROQ_MODEL

# ── Embeddings locaux ─────────────────────────────────────────────────────────
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ── Chemins ───────────────────────────────────────────────────────────────────
CHROMA_PATH = "chroma_db"
DOCS_PATH = "docs"

Path(CHROMA_PATH).mkdir(exist_ok=True)
Path(DOCS_PATH).mkdir(exist_ok=True)

# ── Paramètres RAG ────────────────────────────────────────────────────────────
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
TOP_K_RESULTS = 6  
MAX_RESPONSE_TOKENS = 1500

# ── Interface ─────────────────────────────────────────────────────────────────
THEME = "dark"
ANIMATIONS = True
EXPORT_ENABLED = True
SHOW_CONFIDENCE = True
CACHE_ENABLED = True
CACHE_SIZE = 100
ENABLE_LOGGING = True
LOG_FILE = "dgac_audit.log"

# ── Prompt système amélioré ───────────────────────────────────────────────────
SYSTEM_PROMPT = """Tu es un assistant expert DGAC — Direction Générale de l'Aviation Civile.

RÈGLES ABSOLUES :
1. Réponds UNIQUEMENT en français
2. Base-toi EXCLUSIVEMENT sur les documents fournis
3. Si l'information n'est pas dans les documents, réponds : "Information non trouvée dans les documents fournis"
4. NE JAMAIS inventer, extrapoler ou compléter des données non présentes dans le contexte
5. NE JAMAIS générer des listes ou tableaux non présents explicitement dans le document
6. Cite toujours la source : nom du fichier + numéro de page
7. Maximum 5 phrases par réponse — sois concis et factuel

INTERDIT :
- Inventer des catégories ou des chiffres
- Compléter une liste au-delà de ce qui est dans le document
- Extrapoler à partir de données partielles

Solution souveraine 🇫🇷 — Données traitées localement."""

def validate_config():
    print("=" * 50)
    print("CONFIGURATION — ASSISTANT DGAC")
    print("=" * 50)
    print(f"LLM        : Groq ({GROQ_MODEL}) ⚡")
    print(f"Embeddings : Local (sentence-transformers)")
    print(f"Clé Groq   : {'✅ OK' if GROQ_API_KEY else '❌ MANQUANTE'}")
    print("=" * 50)

if __name__ != "__main__":
    validate_config()
