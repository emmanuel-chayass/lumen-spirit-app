import streamlit as st
import google.generativeai as genai

# --- 1. CONFIG ---
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="Lumen AI", page_icon="📖", layout="wide")

@st.cache_resource
def get_working_model():
    return "models/gemini-1.5-flash"

MODEL_NAME = get_working_model()
SYSTEM_PROMPT = "Tu es Lumen, un expert théologique geek et amical. Ton but est d'aider spirituellement l'utilisateur."

# --- 2. GESTION DU MULTI-CHAT ---
# Initialisation du dictionnaire des conversations
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {} # Format: {"Nom du chat": {"messages": [], "chat_obj": obj}}

# Initialisation du chat actuel
if "current_chat_name" not in st.session_state:
    st.session_state.current_chat_name = None

# --- 3. BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.title("📚 Tes Échanges")
    
    if st.button("➕ Nouvelle Discussion", use_container_width=True):
        new_id = f"Discussion {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[new_id] = {
            "messages": [{"role": "assistant", "content": "Paix sur toi ! Prêt pour une nouvelle exploration ?"}],
            "chat_obj": genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_PROMPT).start_chat(history=[])
        }
        st.session_state.current_chat_name = new_id
        st.rerun()

    st.divider()
    
    # Liste des conversations existantes
    for chat_name in list(st.session_state.all_chats.keys()):
        if st.button(chat_name, use_container_width=True):
            st.session_state.current_chat_name = chat_name
            st.rerun()

# --- 4. AFFICHAGE DU CHAT SÉLECTIONNÉ ---
if st.session_state.current_chat_name:
    current_name = st.session_state.current_chat_name
    chat_data = st.session_state.all_chats[current_name]
    
    st.title(f"📖 {current_name}")
    st.caption("Lumen AI | Ton guide spirituel")

    # Affichage de l'historique du chat sélectionné
    for msg in chat_data["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Zone de saisie
    if prompt := st.chat_input("Écris ici..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        chat_data["messages"].append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            try:
                response = chat_data["chat_obj"].send_message(prompt)
                answer = response.text
                st.markdown(answer)
                chat_data["messages"].append({"role": "assistant", "content": answer})
                
                # Optionnel : Renommer le chat automatiquement après le premier message
                if current_name.startswith("Discussion"):
                    new_name = prompt[:20] + "..." if len(prompt) > 20 else prompt
                    st.session_state.all_chats[new_name] = st.session_state.all_chats.pop(current_name)
                    st.session_state.current_chat_name = new_name
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Erreur : {e}")
else:
    st.info("👋 Clique sur 'Nouvelle Discussion' à gauche pour commencer à parler avec Lumen.")
