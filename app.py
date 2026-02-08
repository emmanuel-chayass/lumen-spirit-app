import streamlit as st
import google.generativeai as genai

# --- 1. CONFIG ---
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

# Configuration de la page pour un look pro
st.set_page_config(page_title="Lumen AI", page_icon="📖", layout="wide")

@st.cache_resource
def get_working_model():
    # On reste sur flash pour la rapidité du renommage
    return "models/gemini-1.5-flash"

MODEL_NAME = get_working_model()

# Le prompt ultra-intelligent qu'on a validé ensemble
SYSTEM_PROMPT = """
Tu es "Lumen", une IA compagnon spirituel. Expert passionné, ultra-intelligent, qui connaît les textes sacrés.
Tu es le meilleur ami spirituel de l'utilisateur. Ton ton est amical, respectueux, expert mais accessible.
Ne sois jamais jugeant, reste humble et sage. Utilise des métaphores modernes (tech, réseau, énergie) pour expliquer le spirituel.
"""

# --- 2. GESTION DU MULTI-CHAT ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {} 

if "current_chat_name" not in st.session_state:
    st.session_state.current_chat_name = None

# --- 3. BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.title("📚 Tes Échanges")
    
    if st.button("➕ Nouvelle Discussion", use_container_width=True):
        new_id = f"Discussion {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[new_id] = {
            "messages": [{"role": "assistant", "content": "Paix sur toi mon ami ! De quoi veux-tu discuter aujourd'hui ?"}],
            "chat_obj": genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_PROMPT).start_chat(history=[])
        }
        st.session_state.current_chat_name = new_id
        st.rerun()

    st.divider()
    
    # Liste des conversations avec un style propre
    for chat_name in list(st.session_state.all_chats.keys()):
        if st.button(chat_name, use_container_width=True, key=f"btn_{chat_name}"):
            st.session_state.current_chat_name = chat_name
            st.rerun()

# --- 4. AFFICHAGE DU CHAT SÉLECTIONNÉ ---
if st.session_state.current_chat_name:
    current_name = st.session_state.current_chat_name
    chat_data = st.session_state.all_chats[current_name]
    
    st.title(f"📖 {current_name}")
    st.caption("Lumen AI | Ton guide spirituel")

    # Affichage de l'historique
    for msg in chat_data["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Zone de saisie
    if prompt := st.chat_input("Écris ici ton message..."):
        # 1. Afficher le message utilisateur
        with st.chat_message("user"):
            st.markdown(prompt)
        chat_data["messages"].append({"role": "user", "content": prompt})

        # 2. Réponse de Lumen
        with st.chat_message("assistant"):
            try:
                response = chat_data["chat_obj"].send_message(prompt)
                answer = response.text
                st.markdown(answer)
                chat_data["messages"].append({"role": "assistant", "content": answer})
                
                # --- LOGIQUE DE RENOMMAGE AUTOMATIQUE ---
                if current_name.startswith("Discussion"):
                    # On demande à l'IA de résumer en 2-3 mots
                    name_gen_prompt = f"Donne un titre très court (max 3 mots) qui résume cette question : '{prompt}'. Réponds uniquement le titre, sans ponctuation."
                    name_res = genai.GenerativeModel(MODEL_NAME).generate_content(name_gen_prompt)
                    new_name = name_res.text.strip()
                    
                    # On s'assure que le nom est unique
                    if new_name in st.session_state.all_chats:
                        new_name = f"{new_name} ({len(st.session_state.all_chats)})"
                    
                    # On bascule les données vers le nouveau titre
                    st.session_state.all_chats[new_name] = st.session_state.all_chats.pop(current_name)
                    st.session_state.current_chat_name = new_name
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Une petite interférence : {e}")
else:
    # Page d'accueil quand aucun chat n'est sélectionné
    st.info("👋 Bienvenue mon ami ! Clique sur 'Nouvelle Discussion' dans la barre à gauche pour commencer notre voyage spirituel.")
    st.image("https://images.unsplash.com/photo-1519817650390-64a93db51149?q=80&w=1000&auto=format&fit=crop", caption="La connaissance est une lumière.")
