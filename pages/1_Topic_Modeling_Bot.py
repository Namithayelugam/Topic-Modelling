import streamlit as st
from langchain_bot import predict_mlp_topic, refine_with_groq

from auth.auth_handler import (
    save_user_prediction,
    get_user_history,
    clear_user_history
)

st.set_page_config(page_title="MLP + Groq + Streamlit", page_icon="🧠", layout="wide")
# --- Theme Handling ---
if st.query_params.get("theme_switched") == "1":
    st.query_params.clear()
    st.rerun()

if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

def toggle_theme():
    st.session_state.theme = "Light" if st.session_state.theme == "Dark" else "Dark"
    st.query_params["theme_switched"] = "1"
    st.rerun()

def apply_theme():
    if st.session_state.theme == "Dark":
        st.markdown("""
            <style>
                body, .stApp { background-color: #0e1117; color: white; }
                .big-title { font-size: 2.2em; font-weight: bold; color: #4B8BBE; }
                .section-title { font-size: 1.3em; font-weight: 600; color: #fff; }
                .result-box {
                    background-color: #1e1e1e;
                    padding: 1.2rem;
                    border-radius: 12px;
                    color: #ffffff;
                    margin-top: 1.2rem;
                }
                .blue-label { color: #3b82f6; font-weight: 600; }
                .stButton>button {
                    background-color: #1f2937;
                    color: white;
                    border-radius: 10px;
                    padding: 0.5em 1em;
                }
                .stTextInput > label, .stTextArea > label, .stExpanderHeader {
                    color: #fff !important;
                }
                textarea, input[type="text"] {
                    background-color: #1e1e1e !important;
                    color: white !important;
                    caret-color: white !important;
                }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
                body, .stApp { background-color: #ffffff; color: #000000; }
                .big-title { font-size: 2.2em; font-weight: bold; color: #4B8BBE; }
                .section-title { font-size: 1.3em; font-weight: 600; color: #333; }
                .result-box {
                    background-color: #f0f0f0;
                    padding: 1.2rem;
                    border-radius: 12px;
                    color: #000000;
                    margin-top: 1.2rem;
                }
                .blue-label { color: #1e40af; font-weight: 600; }
                .stTextInput > label, .stTextArea > label, .stExpanderHeader {
                    color: #111 !important;
                }
                ::placeholder {
                    color: #444 !important;
                    opacity: 1 !important;
                }
                .stButton>button {
                    background-color: #ffffff;
                    color: black;
                    border: 1px solid #333;
                    border-radius: 10px;
                    padding: 0.5em 1em;
                }
                textarea, input[type="text"] {
                    background-color: #ffffff !important;
                    color: black !important;
                    caret-color: black !important;
                }
            </style>
        """, unsafe_allow_html=True)

apply_theme()

# --- Render toggle icon at top-right ---
toggle_icon = "🌞" if st.session_state.theme == "Dark" else "🌙"
with st.container():
    col1, col2, col3 = st.columns([3, 1, 0.5])
    with col3:
        if st.button(toggle_icon, on_click=toggle_theme, key="theme_button"):
            pass

# Hides the file name like "app" or "streamlit_ui" from the sidebar
st.markdown("""
    <style>
    /* Hide entire sidebar nav page list */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# --- Auth Gate ---
if not st.session_state.get("authenticated", False):
    st.warning("🔒 You must log in first from the main page.")
    st.stop()

email = st.session_state.get("email", "")
st.title("Topic Modeling Bot")

# --- Sidebar: User Info, History, Account Settings ---
with st.sidebar:
    st.markdown("### 👤 Logged in as")
    st.markdown(f"**{email}**")

    st.markdown("### 📄 Prediction History")
    history = get_user_history(email)

    if history:
        for i, item in enumerate(reversed(history[-5:])):  # show last 5 entries
            if st.button(f"{i + 1}. {item['refined_topic']}"):
                st.session_state.question = item["question"]
                st.session_state.answer = item["answer"]
                st.session_state.user_prompt = item.get("user_prompt", "Refine the topic")
                st.session_state.mlp_topic = item["mlp_topic"]
                st.session_state.refined_topic = item["refined_topic"]
                st.session_state.show_result = True
    else:
        st.info("No predictions yet.")

    if st.button("🗑️ Clear History"):
        clear_user_history(email)
        st.success("History cleared.")



    st.markdown("---")
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("streamlit_ui.py")

# --- Initialize session defaults ---
def reset_fields():
    for key in ["question", "answer", "user_prompt", "mlp_topic", "refined_topic", "show_result"]:
        st.session_state[key] = "" if isinstance(st.session_state.get(key, ""), str) else False

for key, default in {
    "question": "", "answer": "", "user_prompt": "Refine the topic",
    "mlp_topic": "", "refined_topic": "", "show_result": False
}.items():
    st.session_state.setdefault(key, default)

# --- Input UI ---
question = st.text_area("Enter your question:", key="question")
answer = st.text_area("Provide an answer:", key="answer")
user_prompt = st.text_input("Instruction (e.g., 'Make it more specific')", key="user_prompt")

col1, col2 = st.columns([12, 1])
with col1:
    if st.button("🔍 Predict Topic"):
        if not question.strip() or not answer.strip():
            st.warning("⚠️ Please fill in both question and answer.")
        else:
            st.session_state.mlp_topic = predict_mlp_topic(question, answer)
            st.session_state.refined_topic = refine_with_groq(
    question, answer, st.session_state.mlp_topic, user_prompt
)

            st.session_state.show_result = True

            save_user_prediction(
                email=email,
                question=question,
                answer=answer,
                mlp_topic=st.session_state.mlp_topic,
                refined_topic=st.session_state.refined_topic,
                user_prompt=user_prompt
            )

with col2:
    st.button("🔄 Reset", on_click=reset_fields)

# --- Result Display ---
if st.session_state.show_result:
    st.markdown("### 🔍 Prediction Result")
    st.markdown(f"🧠 **MLP Topic:** `{st.session_state.mlp_topic}`")
    st.markdown(f"🧙‍♀️ **Refined Topic (via Llama):** `{st.session_state.refined_topic}`")
