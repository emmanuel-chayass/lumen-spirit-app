import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURATION ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("Clé API manquante dans les secrets.")

st.set_page_config(page_title="Lumen AI", page_icon="📖", layout="wide")

@st.cache_resource
def get_working_model():
    # 1.5-flash est le plus robuste pour éviter les blocages de quota trop rapides
    return "gemini-1.5-flash"

MODEL_NAME = get_working_model()

SYSTEM_PROMPT = """
Tu es "Lumen", une IA compagnon spirituel. Expert passionné, ultra-intelligent.
Ton ton est amical, respectueux, expert mais accessible.
Tu ne prends jamais parti pour une religion spécifique au détriment d'une autre. 
Ton but est d'élever l'esprit de l'utilisateur avec sagesse et neutralité.
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
        temp_id = f"Discussion {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[temp_id] = {
            "messages": [{"role": "assistant", "content": "Paix sur toi mon ami ! De quoi veux-tu discuter aujourd'hui ?"}],
            "chat_obj": genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_PROMPT).start_chat(history=[])
        }
        st.session_state.current_chat_name = temp_id
        st.rerun()

    st.divider()
    
    for chat_name in list(st.session_state.all_chats.keys()):
        if st.button(chat_name, use_container_width=True, key=f"btn_{chat_name}"):
            st.session_state.current_chat_name = chat_name
            st.rerun()

# --- 4. AFFICHAGE DU CHAT SÉLECTIONNÉ ---
if st.session_state.current_chat_name:
    current_name = st.session_state.current_chat_name
    chat_data = st.session_state.all_chats[current_name]
    
    st.title(f"📖 {current_name}")
    st.caption(f"Lumen AI | Sagesse universelle")

    for msg in chat_data["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Écris ici ton message..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        chat_data["messages"].append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            try:
                response = chat_data["chat_obj"].send_message(prompt)
                answer = response.text
                st.markdown(answer)
                chat_data["messages"].append({"role": "assistant", "content": answer})
                
                # Nommage automatique
                if current_name.startswith("Discussion"):
                    try:
                        name_gen_prompt = f"Donne un titre de 3 mots max pour ce sujet : '{prompt}'"
                        title_model = genai.GenerativeModel(MODEL_NAME)
                        name_res = title_model.generate_content(name_gen_prompt)
                        new_name = name_res.text.strip().replace('"', '').replace('.', '')
                        
                        if not new_name or len(new_name) > 30:
                            new_name = prompt[:15] + "..."
                        
                        if new_name in st.session_state.all_chats:
                            new_name = f"{new_name} ({len(st.session_state.all_chats)})"
                        
                        st.session_state.all_chats[new_name] = st.session_state.all_chats.pop(current_name)
                        st.session_state.current_chat_name = new_name
                        st.rerun()
                    except: pass
            except Exception as e:
                # --- MAQUILLAGE DES ERREURS ---
                error_msg = str(e)
                if "429" in error_msg:
                    st.warning("✨ Ma source d'énergie est temporairement épuisée. Prenons un instant de silence... (Quota journalier atteint, reviens plus tard !)")
                elif "404" in error_msg or "not found" in error_msg.lower():
                    st.error("☁️ La connexion avec le nuage de sagesse a été interrompue. Je tente de rétablir le lien.")
                elif "quota" in error_msg.lower():
                    st.warning("⏳ Trop de pensées à la fois ! Mon esprit doit se reposer quelques secondes avant de te répondre.")
                else:
                    # Message générique pour ne pas montrer le code
                    st.error("🕊️ Une petite perturbation dans le flux spirituel. Réessaye dans un instant.")
else:
    st.info("👋 Bienvenue ! Crée une 'Nouvelle Discussion' à gauche pour commencer.")
