# ✈️ Assistant IA réglementaire — aéronautique

<div align="center">

![Assistant RAG aéronautique](assets/portfolio-cover.png)

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.2-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1-F55036?style=for-the-badge)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-FF6B35?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)

<br/>

**Interrogez des documents réglementaires aéronautiques en langage naturel et obtenez des réponses accompagnées de leurs sources.**

Prototype RAG · Index vectoriel ChromaDB · Inférence Groq · Interface Streamlit

<br/>

[🚀 Démonstration](#-démonstration) · [📦 Installation](#-installation) · [🏗️ Architecture](#️-architecture) · [📊 Résultats](#-résultats)

</div>

---

## 🇫🇷 Contexte & Motivation

Ce projet est né d'un constat simple : les agents de la DSAC (Direction de la Sécurité de l'Aviation Civile) passent des heures à chercher une information précise dans des centaines de pages de rapports annuels, circulaires EASA et règlements OACI.

Le prototype associe une indexation vectorielle locale avec ChromaDB à une inférence réalisée via l’API Groq. Les extraits nécessaires à la génération sont donc transmis au fournisseur d’inférence lors d’une requête.

> Développé de façon autonome et présenté en démonstration live lors d'un entretien à la DSAC en mars 2026. Le recruteur a pu interroger en temps réel le Rapport Annuel de Sécurité Aérienne 2024.

---

## ⚡ Performances mesurées

| Indicateur | Résultat |
|-----------|---------|
| ⏱️ Temps de réponse moyen | **0.3 seconde** |
| 📄 Chunks indexés | **835** |
| 🎯 Score de pertinence | **100%** |
| ⚡ Requêtes depuis le cache | **36%** |
| 💸 Coût d'infrastructure | **0 €** |
| 🔒 Index et embeddings | **Stockés localement** |

> **Comparaison** : solution précédente avec Ollama local → 168 secondes par réponse. Le choix architectural a multiplié la vitesse par **560**.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   PIPELINE RAG SOUVERAIN                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📄 PDF DGAC                                                │
│  (Rapport DSAC, circulaire EASA, règlement OACI)            │
│       │                                                     │
│       ▼                                                     │
│  ① INGESTION                                               │
│  LangChain + PyPDF → nettoyage + découpage                  │
│  RecursiveCharacterTextSplitter (800 chars, overlap 100)    │
│       │                                                     │
│       ▼                                                     │
│  ② VECTORISATION  (100% LOCAL)                             │
│  Sentence-Transformers all-MiniLM-L6-v2                     │
│  → vecteurs de dimension 384                                │
│  → persistés dans ChromaDB sur disque                       │
│       │                                                     │
│       ▼                                                     │
│  ③ RETRIEVAL                                               │
│  Question utilisateur → encodage → similarité cosinus       │
│  → Top-6 passages les plus pertinents                       │
│       │                                                     │
│       ▼                                                     │
│  ④ GÉNÉRATION                                              │
│  Groq API (llama-3.1-8b-instant)                            │
│  Prompt structuré → réponse + source + page                 │
│  Anti-hallucination : "non trouvé" si absent                │
│       │                                                     │
│       ▼                                                     │
│  ⑤ INTERFACE STREAMLIT                                     │
│  Dark theme glassmorphisme · Export PDF · Dashboard         │
│  Cache intelligent · Feedback utilisateur · Analytics       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔒 Architecture et traitement des données

Dans l'aéronautique, la confidentialité des documents doit être prise en compte dès la conception. Ce prototype conserve localement les embeddings et l'index vectoriel, puis transmet à Groq les extraits nécessaires pour générer chaque réponse.

| Composant | Solution | Traitement |
|-----------|---------|-------------|
| LLM | Groq API (llama-3.1-8b-instant) | Inférence via un service externe |
| Embeddings | Sentence-Transformers | Local — aucun appel API |
| Base vectorielle | ChromaDB | Sur disque local |
| Interface | Streamlit | Exécution locale |

> Pour un usage avec des documents sensibles, une version entièrement locale du modèle ou une infrastructure approuvée par l'organisation serait nécessaire.
✅ Recommandations **DINUM** (programme Albert)
✅ Bonnes pratiques **ANSSI**

---

## 🚀 Installation

### Prérequis

- Python 3.11+
- Compte Groq gratuit → [console.groq.com](https://console.groq.com)

### Étapes

```bash
# 1. Cloner le dépôt
git clone https://github.com/Boubanda/Boubanda-chatbot-rag-dgac.git
cd Boubanda-chatbot-rag-dgac

# 2. Créer l'environnement virtuel
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / Mac
source .venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer la clé API
cp .env.example .env
# Éditer .env et renseigner votre clé Groq :
# GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 5. Lancer l'application
streamlit run app.py --server.fileWatcherType none
```

L'application s'ouvre automatiquement sur `http://localhost:8501`

---

## 📦 Structure du projet

```
chatbot-rag-dgac/
│
├── app.py                  # Interface Streamlit principale
├── rag_engine.py           # Pipeline RAG (cœur du système)
├── config.py               # Configuration centralisée
├── export_utils.py         # Export PDF des conversations
│
├── assets/
│   ├── logo_dgac.webp      # Logo DGAC sidebar
│   └── bg_aviation.webp    # Fond d'écran aéronautique
│
├── chroma_db/              # Base vectorielle persistante (gitignored)
├── docs/                   # Dossier PDFs à indexer (gitignored)
│
├── .env                    # Clés API (gitignored)
├── .env.example            # Template de configuration
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🎛️ Fonctionnalités

### 📤 Gestion des documents
- Upload de PDFs directement dans l'interface (limite 200 Mo)
- Indexation automatique avec barre de progression
- Support multi-documents (plusieurs PDFs simultanément)
- Persistance de la base vectorielle entre les sessions

### 💬 Chat intelligent
- Questions en langage naturel en français
- Réponses sourcées avec **nom du fichier + numéro de page**
- Score de pertinence affiché pour chaque réponse
- Suggestions de questions contextuelles
- Anti-hallucination : refus explicite si l'information est absente

### ⚡ Optimisations
- Cache intelligent (MD5) — 36% des requêtes servies instantanément
- Modèle `llama-3.1-8b-instant` optimisé pour la vitesse
- Paramètres ajustables (température, top-k, modèle)

### 📊 Analytics & Export
- Dashboard Plotly avec statistiques de session
- Temps de réponse moyen, taux de cache, requêtes totales
- Export PDF de la conversation complète
- Export Markdown / Texte brut
- Feedback utilisateur 👍👎 sauvegardé en JSON
- Logs d'audit horodatés (dgac_audit.log)

---

## 🛠️ Stack technique

```
Backend
├── Python 3.11
├── LangChain + LangChain-Community    # Orchestration RAG
├── ChromaDB                           # Base vectorielle persistante
├── Sentence-Transformers              # Embeddings locaux (all-MiniLM-L6-v2)
├── Groq SDK                           # LLM ultra-rapide
└── PyPDF                              # Extraction de texte PDF

Frontend
├── Streamlit                          # Interface web
├── Plotly                             # Dashboard analytics
└── fpdf2                              # Export PDF

Infrastructure
├── python-dotenv                      # Gestion des secrets
└── ChromaDB persistence               # Stockage local des vecteurs
```

---

## 🎯 Cas d'usage

Ce système répond directement aux besoins documentaires des organisations aéronautiques :

| Organisation | Besoin | Application |
|-------------|--------|-------------|
| DSAC / DGAC | Interrogation rapports sécurité | ✅ Testé en production |
| Airbus | Documentation technique A320/A380 | Manuels d'ingénierie 2000+ pages |
| Safran | Manuels moteurs CFM/LEAP | Maintenance & certification |
| Thales | Règlements avionique | Conformité réglementaire |
| Air France Industries | MEL / AMM | Maintenance en ligne |
| ATR / Dassault | Documentation certification | EASA Part 21 |

---

## ⚙️ Configuration

Paramètres disponibles dans `config.py` :

```python
GROQ_MODEL       = "llama-3.1-8b-instant"                   # Modèle LLM
EMBEDDING_MODEL  = "sentence-transformers/all-MiniLM-L6-v2" # Embeddings
CHUNK_SIZE       = 800                                        # Taille chunks
CHUNK_OVERLAP    = 100                                        # Chevauchement
TOP_K_RESULTS    = 6                                          # Passages récupérés
CACHE_ENABLED    = True                                       # Cache intelligent
CACHE_SIZE       = 100                                        # Taille du cache
```

---

## 📈 Roadmap

- [x] Pipeline RAG opérationnel avec index vectoriel local
- [x] Interface Streamlit glassmorphisme dark theme
- [x] Cache intelligent + dashboard analytics
- [x] Export PDF + feedback utilisateur
- [x] Anti-hallucination
- [ ] Mémoire conversationnelle multi-tours
- [ ] API REST FastAPI pour intégration externe
- [ ] Authentification utilisateurs
- [ ] Déploiement Docker
- [ ] Évaluation RAGAS (faithfulness, relevancy)
- [ ] Mode audit avec traçabilité complète

---

## 👨‍💻 Auteur

**Levi Junior BOUBANDA**

Étudiant Bac+5 IA & Data Science — Aivancity School for Technology, Business & Society (n°1 Eduniversal)

Disponible en alternance **Data Scientist · Data Engineer · Data Analyst**
Rythme : 3 semaines entreprise / 1 semaine école · Septembre 2026 · Île-de-France

[![Email](https://img.shields.io/badge/Email-leviboubanda07@gmail.com-D14836?style=flat&logo=gmail&logoColor=white)](mailto:leviboubanda07@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-lévi--junior016-0077B5?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/lévi-junior016)
[![Portfolio](https://img.shields.io/badge/Portfolio-mon--portfolio-FF6B35?style=flat&logo=vercel&logoColor=white)](https://mon-portfolio-nine-lime.vercel.app)
[![GitHub](https://img.shields.io/badge/GitHub-Boubanda-181717?style=flat&logo=github&logoColor=white)](https://github.com/Boubanda)

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

<div align="center">

⭐ **Si ce projet vous a été utile, n'hésitez pas à lui mettre une étoile !**

*Développé avec ❤️ pour faciliter l'accès à l'information réglementaire aéronautique.*

</div>
