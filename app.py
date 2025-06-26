import streamlit as st
from auth.auth_handler import signup_user, login_user

# Page config
st.set_page_config(
    page_title="Login | Topic Bot",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 💡 Hide sidebar and page nav
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }
    header { visibility: hidden; }  /* hides the Streamlit header if needed */
    .login-box {
        max-width: 400px;
        margin: auto;
        padding: 2rem;
        border: 1px solid #ccc;
        border-radius: 10px;
        background-color: #f9f9f9;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- Auth State ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "auth_mode" not in st.session_state:
    st.session_state["auth_mode"] = "login"

def switch_mode():
    st.session_state["auth_mode"] = "signup" if st.session_state["auth_mode"] == "login" else "login"

# --- Auth UI ---
#st.markdown("<div class='login-box'>", unsafe_allow_html=True)
st.markdown(
    f"<h2 style='text-align:center;'>{'Login to TopicBOT' if st.session_state.auth_mode == 'login' else 'Sign Up for TopicBOT'}</h2>",
    unsafe_allow_html=True,
)

email = st.text_input("📧 Email", placeholder="Enter your email")
password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")

if st.session_state.auth_mode == "login":
    if st.button("Login"):
        user = login_user(email, password)
        if user:
            st.session_state["authenticated"] = True
            st.session_state["email"] = email
            st.success("✅ Login successful! Redirecting to the bot...")
            st.switch_page("pages/1_Topic_Modeling_Bot.py")
        else:
            st.error("❌ Invalid email or password.")
    st.markdown("Don't have an account?")
    if st.button("Create New Account"):
        switch_mode()
else:
    if st.button("✅ Sign Up"):
        user = signup_user(email, password)
        if isinstance(user, dict):
            st.success("✅ Signup successful. Please login now.")
            switch_mode()
        else:
            st.error(f"❌ Signup failed: {user}")
    st.markdown("Already have an account?")
    if st.button("🚪 Go to Login"):
        switch_mode()

st.markdown("</div>", unsafe_allow_html=True)

# 🛡️ Show warning if not logged in
if not st.session_state["authenticated"]:
    st.warning("🔐 Please log in to continue. Topic Modeling Bot is disabled until login.")
