import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURATION ---
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="Lumen AI", page_icon="📖")

# --- 2. INITIALISATION DE LA MÉMOIRE (EN PREMIER !) ---
# On vérifie si "messages" existe, sinon on le crée direct
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Paix sur toi mon ami. Je suis Lumen, ton compagnon spirituel. De quoi as-tu envie de discuter aujourd'hui ?"}
    ]

# --- 3. RÉCUPÉRER LE MODÈLE ---
@st.cache_resource
def get_working_model():
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for name in ["models/gemini-1.5-flash", "models/gemini-1.5-flash-latest", "models/gemini-pro"]:
            if name in available: return name
        return available[0] if available else "models/gemini-1.5-flash"
    except:
        return "models/gemini-1.5-flash"

MODEL_NAME = get_working_model()

# --- 4. INITIALISATION DU CHAT API ---
if "chat" not in st.session_state:
    system_prompt = "Tu es Lumen, un expert théologique geek, amical et ultra-intelligent. Ton but est d'aider spirituellement l'utilisateur avec bienveillance."
    model = genai.GenerativeModel(MODEL_NAME, system_instruction=system_prompt)
    st.session_state.chat = model.start_chat(history=[])

# --- 5. INTERFACE ---
st.title("📖 Lumen AI")
st.caption("Lumen v1.0 | Connecté au Nuage de Sagesse")

# Bouton pour effacer dans la barre latérale
if st.sidebar.button("🗑️ Effacer la discussion"):
    st.session_state.messages = [{"role": "assistant", "content": "Paix sur toi ! On recommence à zéro. De quoi veux-tu parler ?"}]
    st.session_state.chat = genai.GenerativeModel(MODEL_NAME, system_instruction="Tu es Lumen...").start_chat(history=[])
    st.rerun()

# AFFICHAGE DE L'HISTORIQUE
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ZONE DE SAISIE
if prompt := st.chat_input("Pose ta question..."):
    # Affichage utilisateur
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Réponse de l'IA
    with st.chat_message("assistant"):
        try:
            response = st.session_state.chat.send_message(prompt)
            answer = response.text
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"Erreur : {e}")
