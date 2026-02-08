import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURATION ---
# Utilisation de la clé API stockée dans les secrets Streamlit
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

# Configuration de la page pour un look moderne et large
st.set_page_config(page_title="Lumen AI", page_icon="📖", layout="wide")

@st.cache_resource
def get_working_model():
    # Utilisation du modèle de dernière génération comme suggéré
    # gemini-2.0-flash est actuellement le plus rapide et performant
   return "gemini-1.5-flash"

MODEL_NAME = get_working_model()

# Le prompt système qui définit la personnalité de Lumen
SYSTEM_PROMPT = """
CONTEXTE ET RÔLE :
Tu es "Lumen", une IA compagnon spirituel. Tu es un "Geek de la Théologie" : un expert passionné, ultra-intelligent, qui connaît les textes sacrés sur le bout des doigts. Ton but est d'être le meilleur ami spirituel de l'utilisateur.

TON :
1. Amical et Respectueux : Tu parles d'égal à égal, comme un frère bienveillant.
2. Expert mais Accessible : Tu simplifies les concepts complexes sans les dénaturer.
3. Métaphorique : Utilise des images modernes (tech, réseau, énergie) pour expliquer la foi.

CONSIGNES :
- Ne juge jamais.
- Refuse poliment de dénigrer d'autres religions.
- Adapte ton langage à celui de l'utilisateur (solennel ou relax).
"""

# --- 2. GESTION DU MULTI-CHAT (ÉTAT DE LA SESSION) ---
# Stockage de toutes les discussions
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {} 

# Référence de la discussion actuellement affichée
if "current_chat_name" not in st.session_state:
    st.session_state.current_chat_name = None

# --- 3. BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.title("📚 Tes Échanges")
    
    # Bouton pour créer une nouvelle discussion
    if st.button("➕ Nouvelle Discussion", use_container_width=True):
        temp_id = f"Discussion {len(st.session_state.all_chats) + 1}"
        # On initialise l'objet de chat Gemini avec l'instruction système
        st.session_state.all_chats[temp_id] = {
            "messages": [{"role": "assistant", "content": "Paix sur toi mon ami ! De quoi veux-tu discuter aujourd'hui ?"}],
            "chat_obj": genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_PROMPT).start_chat(history=[])
        }
        st.session_state.current_chat_name = temp_id
        st.rerun()

    st.divider()
    
    # Affichage de la liste des discussions existantes
    for chat_name in list(st.session_state.all_chats.keys()):
        if st.button(chat_name, use_container_width=True, key=f"btn_{chat_name}"):
            st.session_state.current_chat_name = chat_name
            st.rerun()

# --- 4. AFFICHAGE DU CHAT SÉLECTIONNÉ ---
if st.session_state.current_chat_name:
    current_name = st.session_state.current_chat_name
    chat_data = st.session_state.all_chats[current_name]
    
    st.title(f"📖 {current_name}")
    st.caption(f"Lumen AI | Propulsé par Gemini 2.0 Flash")

    # Affichage de l'historique des messages
    for msg in chat_data["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Zone de saisie utilisateur
    if prompt := st.chat_input("Écris ici ton message..."):
        # Affichage immédiat du message utilisateur
        with st.chat_message("user"):
            st.markdown(prompt)
        chat_data["messages"].append({"role": "user", "content": prompt})

        # Génération de la réponse de Lumen
        with st.chat_message("assistant"):
            try:
                # Envoi du message via l'objet de chat qui gère l'historique
                response = chat_data["chat_obj"].send_message(prompt)
                answer = response.text
                st.markdown(answer)
                chat_data["messages"].append({"role": "assistant", "content": answer})
                
                # --- LOGIQUE DE NOMMAGE AUTOMATIQUE ---
                # Si le chat porte encore un nom générique, on demande à l'IA de le renommer
                if current_name.startswith("Discussion"):
                    try:
                        name_gen_prompt = f"Donne un titre très court (max 3 mots) sans ponctuation pour résumer ce sujet : '{prompt}'"
                        # Utilisation d'un modèle temporaire pour le titre
                        title_model = genai.GenerativeModel(MODEL_NAME)
                        name_res = title_model.generate_content(name_gen_prompt)
                        new_name = name_res.text.strip().replace('"', '').replace('.', '').replace('*', '')
                        
                        # Fallback si le titre généré est vide ou trop long
                        if not new_name or len(new_name) > 30:
                            new_name = prompt[:15] + "..."
                        
                        # Éviter les doublons de noms
                        if new_name in st.session_state.all_chats:
                            new_name = f"{new_name} ({len(st.session_state.all_chats)})"
                        
                        # Mise à jour du nom de la discussion
                        st.session_state.all_chats[new_name] = st.session_state.all_chats.pop(current_name)
                        st.session_state.current_chat_name = new_name
                        st.rerun()
                    except:
                        # En cas d'erreur de nommage, on continue sans bloquer
                        pass
                    
            except Exception as e:
                st.error(f"Une petite interférence réseau : {e}")
else:
    # État par défaut : accueil
    st.info("👋 Bienvenue ! Clique sur 'Nouvelle Discussion' à gauche pour commencer notre voyage spirituel.")
    st.image("https://images.unsplash.com/photo-1519817650390-64a93db51149?q=80&w=1000&auto=format&fit=crop", caption="La connaissance est une lumière.")
