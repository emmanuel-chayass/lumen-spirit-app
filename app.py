import streamlit as st
import google.generativeai as genai

# --- CONFIG ---
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="Lumen AI", page_icon="📖")
st.title("📖 Lumen AI")

@st.cache_resource
def get_working_model():
    available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    for name in ["models/gemini-1.5-flash", "models/gemini-1.5-flash-latest", "models/gemini-pro"]:
        if name in available:
            return name
    return available[0] if available else None

MODEL_NAME = get_working_model()

if not MODEL_NAME:
    st.error("Aucun modèle trouvé. Vérifie ta clé API.")
    st.stop()

st.caption("Lumen v1.0 | Connecté au Nuage de Sagesse")

# 2. LE PROMPT SYSTÈME
SYSTEM_PROMPT = """
CONTEXTE ET RÔLE :
Tu es "Lumen", une IA compagnon spirituel. Expert passionné, ultra-intelligent, qui connaît les textes sacrés.
Tu es le meilleur ami spirituel de l'utilisateur. Ton ton est amical, respectueux, expert mais accessible.
"""

# --- GESTION DE LA MÉMOIRE ---
if "chat" not in st.session_state:
    model = genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_PROMPT)
    # On initialise la session de chat de l'API
    st.session_state.chat = model.start_chat(history=[])
    # On crée un message de bienvenue personnalisé qui restera affiché
    st.session_state.messages = [
        {"role": "assistant", "content": "Paix sur toi mon ami. Je suis Lumen, ton compagnon spirituel. De quoi as-tu envie de discuter aujourd'hui ?"}
    ]

# 3. AFFICHAGE DE L'HISTORIQUE
# C'est cette boucle qui manquait ! Elle affiche tout ce qui est dans st.session_state.messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. INTERFACE DE CHAT
if prompt := st.chat_input("Pose ta question..."):
    # On affiche et on sauvegarde le message de l'utilisateur
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        try:
            # Envoi à l'IA
            response = st.session_state.chat.send_message(prompt)
            answer = response.text
            st.markdown(answer)
            # On sauvegarde la réponse de l'IA pour qu'elle reste à l'écran
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"Erreur d'appel : {e}")
