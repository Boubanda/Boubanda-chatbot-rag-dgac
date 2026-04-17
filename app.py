from datetime import datetime
from export_utils import export_conversation_pdf
import streamlit as st
import time
import os
import tempfile
import shutil
import base64
import json
from pathlib import Path
from datetime import datetime

from rag_engine import RAGEngine
from config import OLLAMA_MODEL as MISTRAL_MODEL

# Valeurs par défaut si non présentes dans config
try:
    from config import THEME, ANIMATIONS, EXPORT_ENABLED
except ImportError:
    THEME = "dark"
    ANIMATIONS = True
    EXPORT_ENABLED = True
    print(" Utilisation des valeurs par défaut pour THEME, ANIMATIONS, EXPORT_ENABLED")



def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_image = get_base64_image("assets/bg_aviation.webp")


# ── Configuration de la page ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Assistant IA Souverain — DGAC",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ... le reste du code reste identique ...

# ── CSS GLASSMORPHISME MODERNE ─────────────────────────────────────────────────
st.markdown("""
<style>
    /* ========== DESIGN GLASSMORPHISME MODERNE ========== */
    
    /* Fond image aéronautique */
.stApp {
    background-image: url("data:image/webp;base64,""" + bg_image + """");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Overlay sombre pour lisibilité */
.stApp::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(10, 22, 40, 0.82);
    z-index: 0;
}

.main .block-container {
    position: relative;
    z-index: 1;
}
    
    /* Effet verre pour la sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(15, 41, 66, 0.4);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(0, 180, 216, 0.3);
    }
    
    /* Cartes en verre */
    .glass-card {
        background: rgba(15, 41, 66, 0.3);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 180, 216, 0.3);
        border-radius: 24px;
        padding: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .glass-card:hover {
        background: rgba(15, 41, 66, 0.45);
        border-color: #00B4D8;
        transform: translateY(-4px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    /* Messages chat en verre */
    .user-message {
        background: linear-gradient(135deg, rgba(30, 58, 95, 0.5), rgba(15, 41, 66, 0.4));
        backdrop-filter: blur(8px);
        border-radius: 20px 20px 4px 20px;
        padding: 12px 18px;
        margin: 8px 0;
        border-left: 3px solid #00B4D8;
        transition: all 0.2s;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, rgba(10, 37, 64, 0.5), rgba(10, 26, 47, 0.4));
        backdrop-filter: blur(8px);
        border-radius: 20px 20px 20px 4px;
        padding: 12px 18px;
        margin: 8px 0;
        border-left: 3px solid #22C55E;
        transition: all 0.2s;
    }
    
    /* Animation de pulsation pour le badge souverain */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
        70% { box-shadow: 0 0 0 12px rgba(34, 197, 94, 0); }
        100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }
    
    .sovereign-badge {
        background: linear-gradient(135deg, #0F2942, #1E3A5F);
        border: 1px solid #22C55E;
        border-radius: 16px;
        padding: 12px;
        text-align: center;
        animation: pulse 2s infinite;
    }
    
    /* Effet de brillance sur les boutons */
    .stButton button {
        background: linear-gradient(135deg, #1E3A5F, #0F2942);
        border: 1px solid #00B4D8;
        border-radius: 12px;
        transition: all 0.3s;
        position: relative;
        overflow: hidden;
    }
    
    .stButton button::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(0,180,216,0.1), transparent);
        transform: rotate(45deg);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) rotate(45deg); }
        100% { transform: translateX(100%) rotate(45deg); }
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #00B4D8, #1E3A5F);
        transform: scale(0.98);
        border-color: #22C55E;
    }
    
        /* ── Input chat premium ── */
    .stChatInput {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 16px 24px;
        background: linear-gradient(to top, rgba(10,22,40,0.98) 80%, transparent);
        backdrop-filter: blur(20px);
        z-index: 999;
    }

    .stChatInput > div {
        max-width: 900px;
        margin: 0 auto;
        background: rgba(15, 41, 66, 0.8) !important;
        border: 1px solid rgba(0, 180, 216, 0.6) !important;
        border-radius: 32px !important;
        box-shadow: 0 0 30px rgba(0, 180, 216, 0.15),
                    0 8px 32px rgba(0, 0, 0, 0.4) !important;
        transition: all 0.3s ease !important;
    }

    .stChatInput > div:hover {
        border-color: rgba(0, 180, 216, 0.9) !important;
        box-shadow: 0 0 40px rgba(0, 180, 216, 0.25),
                    0 8px 32px rgba(0, 0, 0, 0.4) !important;
    }

    .stChatInput textarea {
        background: transparent !important;
        border: none !important;
        color: #E2E8F0 !important;
        font-size: 15px !important;
        padding: 14px 20px !important;
        caret-color: #00B4D8 !important;
    }

    .stChatInput textarea::placeholder {
        color: #475569 !important;
        font-style: italic;
    }

    .stChatInput button {
        background: linear-gradient(135deg, #00B4D8, #0077A8) !important;
        border: none !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        margin: 6px !important;
        transition: all 0.3s !important;
        box-shadow: 0 4px 15px rgba(0, 180, 216, 0.4) !important;
    }

    .stChatInput button:hover {
        background: linear-gradient(135deg, #22C55E, #15803D) !important;
        transform: scale(1.1) !important;
        box-shadow: 0 6px 20px rgba(34, 197, 94, 0.5) !important;
    }

    .stChatInput button svg {
        fill: white !important;
    }

    /* Supprime l'ancien style input */
    .stChatInput input {
        background: transparent !important;
        border: none !important;
    }
    
    .stChatInput input:focus {
        border-color: #22C55E !important;
        box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2) !important;
    }
    
    /* Titres avec gradient */
    h1, h2, h3 {
        background: linear-gradient(135deg, #CADCFC, #93C5FD);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    
    /* Statistiques en verre */
    [data-testid="metric-container"] {
        background: rgba(15, 41, 66, 0.4);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(0, 180, 216, 0.3);
        border-radius: 16px;
        padding: 12px;
        transition: all 0.3s;
    }
    
    [data-testid="metric-container"]:hover {
        border-color: #00B4D8;
        transform: translateY(-2px);
    }
    
    /* Badge source */
    .source-badge {
        background: rgba(30, 58, 95, 0.6);
        backdrop-filter: blur(4px);
        border: 1px solid #00B4D8;
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 11px;
        color: #00B4D8;
        display: inline-block;
        margin: 2px;
    }
    
    /* Barre de confiance */
    .confidence-bar {
        background: #1E3A5F;
        border-radius: 4px;
        height: 6px;
        margin-top: 6px;
    }
    
    /* Texte général */
    p, li, span, div {
        color: #CBD5E1;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(15, 41, 66, 0.6);
        backdrop-filter: blur(4px);
        border-radius: 12px;
    }
    
    /* Alertes */
    .stAlert {
        background: rgba(15, 41, 66, 0.6) !important;
        backdrop-filter: blur(8px);
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Fonctions utilitaires ─────────────────────────────────────────────────────
def export_conversation(messages):
    """Exporte la conversation au format Markdown"""
    if not EXPORT_ENABLED:
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_dgac_{timestamp}.md"
    
    content = f"""# Conversation Assistant DGAC
**Date**: {datetime.now().strftime("%d/%m/%Y %H:%M")}
**Modèle**: {MISTRAL_MODEL}

---
"""
    for msg in messages:
        role = "**Utilisateur**" if msg["role"] == "user" else "**Assistant**"
        content += f"\n\n### {role}\n{msg['content']}\n"
        if "sources" in msg and msg["sources"]:
            content += "\n*Sources:*\n"
            for src in msg["sources"]:
                content += f"- {src['file']} (page {src['page']})\n"
    
    return filename, content


def save_feedback(response, rating):
    """Sauvegarde le feedback utilisateur"""
    feedback_file = Path("feedback.json")
    feedback_data = []
    
    if feedback_file.exists():
        with open(feedback_file, 'r', encoding='utf-8') as f:
            feedback_data = json.load(f)
    
    feedback_data.append({
        "timestamp": datetime.now().isoformat(),
        "rating": rating,
        "response_preview": response[:100]
    })
    
    with open(feedback_file, 'w', encoding='utf-8') as f:
        json.dump(feedback_data, f, ensure_ascii=False, indent=2)


# ── Initialisation du moteur RAG ──────────────────────────────────────────────
@st.cache_resource
def init_rag():
    """Initialise le moteur RAG avec cache"""
    try:
        return RAGEngine()
    except Exception as e:
        st.error(f" Erreur d'initialisation: {str(e)}")
        return None


# ── State management ──────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "docs_loaded" not in st.session_state:
    st.session_state.docs_loaded = False
if "total_chunks" not in st.session_state:
    st.session_state.total_chunks = 0
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = set()


# ── Sidebar avec design premium ───────────────────────────────────────────────
with st.sidebar:
    # Header
    with st.sidebar:
     col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("assets/logo_dgac.webp", width=110)
    st.markdown("<div style='text-align:center;color:#CADCFC;font-size:18px;font-weight:600'>Assistant IA DSAC</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;color:#64748B;font-size:11px'>Direction de la Sécurité de l'Aviation Civile</div>", unsafe_allow_html=True)

    st.divider()
        # ========== EXPORT PDF ==========
    if st.session_state.messages:
        st.divider()
        st.markdown("###  Export")
        
        pdf_bytes = export_conversation_pdf(st.session_state.messages)
        st.download_button(
            label=" Exporter en PDF",
            data=pdf_bytes,
            file_name=f"conversation_DGAC_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )



    # Badge souveraineté animé
    st.markdown("""
    <div class="sovereign-badge">
        <div style="font-size:11px;color:#22C55E;font-weight:500">🇫🇷 IA SOUVERAINE</div>
        <div style="font-size:10px;color:#64748B;margin-top:3px">Mistral AI · 100% local</div>
        <div style="font-size:9px;color:#475569">Aucune donnée transmise à l'étranger</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Upload de documents
    st.markdown("###  Documents")
    uploaded_files = st.file_uploader(
        "Charger des PDFs DGAC",
        type=["pdf"],
        accept_multiple_files=True,
        help="Circulaires, rapports de sécurité, règlements EASA..."
    )

    if uploaded_files:
        if st.button(" Indexer les documents", use_container_width=True, type="primary"):
            rag = init_rag()
            if rag is None:
                st.error(" Le moteur RAG n'a pas pu être initialisé")
            else:
                with st.spinner(" Indexation en cours... (peut prendre 1-2 minutes)"):
                    temp_dir = Path("temp_pdfs")
                    temp_dir.mkdir(exist_ok=True)
                    
                    temp_paths = []
                    progress_bar = st.progress(0)
                    
                    try:
                        for i, uploaded_file in enumerate(uploaded_files):
                            temp_path = temp_dir / uploaded_file.name
                            with open(temp_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            temp_paths.append(str(temp_path))
                            progress_bar.progress((i + 1) / len(uploaded_files))
                            st.write(f" {uploaded_file.name} sauvegardé")

                        n_chunks = rag.load_documents(temp_paths)
                        st.session_state.total_chunks = n_chunks
                        st.session_state.docs_loaded = True
                        
                        st.success(f" {len(uploaded_files)} document(s) · {n_chunks} chunks indexés")
                        
                    except Exception as e:
                        st.error(f" Erreur: {str(e)}")
                    
                    finally:
                        if temp_dir.exists():
                            shutil.rmtree(temp_dir, ignore_errors=True)
                        progress_bar.empty()

    st.divider()

    # Statistiques avancées
    st.markdown("###  Statistiques")
    rag = init_rag()
    if rag:
        stats = rag.get_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(" Chunks", stats["chunks"])
        with col2:
            st.metric(" Statut", stats["status"])
        
        # Statistiques supplémentaires
        if "total_queries" in stats and stats["total_queries"] > 0:
            with st.expander(" Performance"):
                st.metric("Requêtes totales", stats["total_queries"])
                st.metric("Cache hits", f"{stats['cache_hits']} ({stats['cache_ratio']:.0f}%)")
                st.metric("Temps moyen", f"{stats['avg_response_time']:.1f}s")
    else:
        st.warning(" Moteur RAG non disponible")

    st.divider()

        # ========== PARAMÈTRES IA ==========
    st.markdown("###  Paramètres IA")
    
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.1
    if "model_choice" not in st.session_state:
        st.session_state.model_choice = "mistral:7b-instruct-q4_0"
    if "k_results" not in st.session_state:
        st.session_state.k_results = 2
    
    temperature = st.slider(
        " Créativité",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.temperature,
        step=0.05,
        help="Plus bas = plus précis"
    )
    st.session_state.temperature = temperature
    
    model_choice = st.selectbox(
        " Modèle IA",
        ["mistral:7b-instruct-q4_0", "mistral:latest"],
        index=0
    )
    st.session_state.model_choice = model_choice
    
    k_results = st.slider(
        " Précision",
        min_value=1,
        max_value=5,
        value=st.session_state.k_results,
        step=1
    )
    st.session_state.k_results = k_results
    
    st.divider()

        # ========== DASHBOARD ==========
    with st.expander(" Dashboard", expanded=False):
        st.markdown("### Statistiques")
        
        questions_total = len(st.session_state.messages) // 2
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(" Questions", questions_total)
        with col2:
            st.metric(" Chunks", stats["chunks"] if rag else 0)
        
        try:
            import plotly.express as px
            topics = ['Sécurité', 'Accidents', 'Certification']
            counts = [10, 8, 5]
            fig = px.pie(values=counts, names=topics, title="Questions par thème")
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Installez plotly")

    # Actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button(" Effacer", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button(" Reset base", use_container_width=True):
            if rag:
                rag.clear()
                st.session_state.docs_loaded = False
                st.session_state.total_chunks = 0
                st.success("Base réinitialisée")
                st.rerun()

        # ========== EXPORT CONVERSATION ==========
    if EXPORT_ENABLED and st.session_state.messages:
        with st.expander(" Exporter", expanded=False):
            export_format = st.radio("Format", ["Markdown", "Texte"], horizontal=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if export_format == "Markdown":
                content = f"# Conversation DGAC\nDate: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                for msg in st.session_state.messages:
                    role = "**Utilisateur**" if msg["role"] == "user" else "**Assistant**"
                    content += f"\n### {role}\n{msg['content']}\n"
                file_ext = "md"
            else:
                content = ""
                for msg in st.session_state.messages:
                    role = "Utilisateur" if msg["role"] == "user" else "Assistant"
                    content += f"{role}: {msg['content']}\n\n"
                file_ext = "txt"
            
            st.download_button(
                label=f" Télécharger",
                data=content,
                file_name=f"conversation_{timestamp}.{file_ext}",
                use_container_width=True
            )

            

    # Info modèle
    st.markdown(f"""
    <div style="font-size:10px;color:#475569;text-align:center">
        <div> Modèle: {MISTRAL_MODEL}</div>
        <div> Optimisé pour rapidité</div>
        <div> 100% local</div>
        <div style="margin-top:8px">Développé par: <strong>Levi Junior BOUBANDA</strong></div>
        <div>Aivancity School — Bac+5 IA & Data</div>
    </div>
    """, unsafe_allow_html=True)


# ── Zone principale avec design premium ───────────────────────────────────────
st.markdown("""
<div style="padding:20px 0 10px; text-align:center">
    <h1 style="margin:0; font-size:2.5em; background:linear-gradient(135deg, #CADCFC, #93C5FD); -webkit-background-clip:text; -webkit-text-fill-color:transparent">
         Assistant IA Souverain — DGAC
    </h1>
    <p style="color:#64748B; margin-top:8px">
        Interrogez vos documents réglementaires en langage naturel · Propulsé par Mistral AI 🇫🇷
    </p>
    <div style="display:flex; justify-content:center; gap:12px; margin-top:16px">
        <span style="background:#1E3A5F; padding:4px 12px; border-radius:20px; font-size:12px">🇫🇷 100% Souverain</span>
        <span style="background:#1E3A5F; padding:4px 12px; border-radius:20px; font-size:12px">🔒 Données locales</span>
        <span style="background:#1E3A5F; padding:4px 12px; border-radius:20px; font-size:12px">⚡ RAG optimisé</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Vérifier l'état des documents
rag = init_rag()
if rag:
    stats = rag.get_stats() if rag else {"chunks": 0, "status": "Non initialisé"}
else:
    stats = {"chunks": 0, "status": "Erreur"}

# Bannière d'état
if not st.session_state.docs_loaded and stats["chunks"] == 0:
    st.info(" **Commencez par charger vos documents PDF** dans la barre latérale, puis cliquez sur 'Indexer les documents'.")
else:
    st.success(f" Base vectorielle active — {stats['chunks']} chunks disponibles — Réponses optimisées ⚡")

# ========== SUGGESTIONS INTELLIGENTES ==========
if not st.session_state.messages:
    st.markdown("###  Questions suggérées")
    
    suggestions = [
        "Quel est le bilan des accidents en France en 2024 ?",
        "Quelles sont les principales causes d'accidents ?",
        "Comment la France se compare-t-elle aux autres pays ?",
        "Quels sont les accidents majeurs dans le monde ?",
        "Quelles sont les recommandations de sécurité ?",
        "Combien d'accidents en instruction double commande ?",
        "Qu'est-ce que le pilotage simultané ?",
        "Quel est le rôle du BEA ?"
    ]
    
    cols = st.columns(2)
    for i, suggestion in enumerate(suggestions[:4]):
        with cols[i % 2]:
            if st.button(f" {suggestion}", use_container_width=True, key=f"sug_{i}"):
                st.session_state.messages.append({"role": "user", "content": suggestion})
                st.rerun()
    
    cols2 = st.columns(2)
    for i, suggestion in enumerate(suggestions[4:8]):
        with cols2[i % 2]:
            if st.button(f" {suggestion}", use_container_width=True, key=f"sug2_{i}"):
                st.session_state.messages.append({"role": "user", "content": suggestion})
                st.rerun()
    
    st.divider()

# Historique de la conversation
for msg in st.session_state.messages:
    # ✅ APRÈS
    with st.chat_message(msg["role"], avatar="🧑‍✈️" if msg["role"] == "user" else "🤖"):
        st.write(msg["content"])
        
        if msg["role"] == "assistant" and "sources" in msg and msg["sources"]:
            with st.expander(f"📎 Sources consultées ({len(msg['sources'])} passages)", expanded=False):
                for src in msg["sources"]:
                    st.markdown(f"""
                    <div style="background:#0F2942;border:1px solid #1E3A5F;border-radius:8px;padding:10px;margin:6px 0">
                        <div style="color:#00B4D8;font-size:11px;font-weight:500"> {src['file']} — Page {src['page']}</div>
                        <div style="color:#94A3B8;font-size:11px;margin-top:4px">{src['excerpt']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        if msg["role"] == "assistant" and "confidence" in msg:
            conf = msg["confidence"]
            color = "#22C55E" if conf > 70 else "#F59E0B" if conf > 40 else "#EF4444"
            st.markdown(f"""
            <div style="margin-top:8px">
                <div style="font-size:10px;color:#64748B">🎯 Score de pertinence : {conf:.0f}%</div>
                <div style="background:#1E3A5F;border-radius:4px;height:5px;margin-top:3px">
                    <div style="background:{color};width:{conf}%;height:5px;border-radius:4px"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Input utilisateur
if question := st.chat_input("Posez votre question sur la documentation DGAC..."):
    if not st.session_state.docs_loaded and stats["chunks"] == 0:
        st.warning(" Veuillez d'abord charger et indexer des documents PDF.")
    else:
        st.session_state.messages.append({"role": "user", "content": question})

        with st.chat_message("user", avatar="🧑‍✈️"):
            st.write(question)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner(" Recherche dans les documents..."):
                try:
                    rag = init_rag()
                    if rag is None:
                        st.error(" Moteur RAG non disponible")
                    else:
                        result = rag.query(question)
                        
                        # Temps de réponse
                        if "response_time" in result:
                            st.caption(f" Réponse générée en {result['response_time']:.1f} secondes")
                        
                        st.write(result["answer"])
                        
                        if result["sources"]:
                            with st.expander(f"📎 Sources consultées ({len(result['sources'])} passages)", expanded=False):
                                for src in result["sources"]:
                                    st.markdown(f"""
                                    <div style="background:#0F2942;border:1px solid #1E3A5F;border-radius:8px;padding:10px;margin:6px 0">
                                        <div style="color:#00B4D8;font-size:11px;font-weight:500">📄 {src['file']} — Page {src['page']}</div>
                                        <div style="color:#94A3B8;font-size:11px;margin-top:4px">{src['excerpt']}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        conf = result["confidence"]
                        color = "#22C55E" if conf > 70 else "#F59E0B" if conf > 40 else "#EF4444"
                        st.markdown(f"""
                        <div style="margin-top:8px">
                            <div style="font-size:10px;color:#64748B">🎯 Score de pertinence : {conf:.0f}%</div>
                            <div style="background:#1E3A5F;border-radius:4px;height:5px;margin-top:3px">
                                <div style="background:{color};width:{conf}%;height:5px;border-radius:4px"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Feedback utilisateur
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("👍 Utile", key=f"feedback_pos_{len(st.session_state.messages)}"):
                                save_feedback(result["answer"], "positive")
                                st.success("Merci pour votre retour !")
                        with col2:
                            if st.button("👎 Peu utile", key=f"feedback_neg_{len(st.session_state.messages)}"):
                                save_feedback(result["answer"], "negative")
                                st.warning("Merci, cela nous aide à nous améliorer.")
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": result["answer"],
                            "sources": result["sources"],
                            "confidence": result["confidence"]
                        })
                        
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}") 