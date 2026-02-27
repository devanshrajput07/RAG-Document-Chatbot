import streamlit as st
from firebase_config import auth, db

def login_ui():
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is not None:
        st.sidebar.markdown(f"**Logged in as:**\n`{st.session_state.user['email']}`")
        if st.sidebar.button("Logout", type="primary"):
            st.session_state.user = None
            if "vectorstore" in st.session_state:
                st.session_state.vectorstore = None
            st.rerun()
        return True

    st.title("🤖 Welcome to RAG Chatbot")
    st.markdown("Please log in or create an account to start chatting with your documents.")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login")
        email_login = st.text_input("Email", key="login_email")
        password_login = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if not email_login or not password_login:
                st.warning("Please enter both email and password.")
            else:
                try:
                    user = auth.sign_in_with_email_and_password(email_login, password_login)
                    st.session_state.user = user
                    st.rerun()
                except Exception as e:
                    error_msg = str(e).upper()
                    if "INVALID" in error_msg or "NOT_FOUND" in error_msg:
                        st.error("Invalid email or password.")
                    else:
                        st.error("Login failed. Please check your credentials.")

    with tab2:
        st.subheader("Sign Up")
        email_signup = st.text_input("Email", key="signup_email")
        password_signup = st.text_input("Password", type="password", key="signup_password")
        if st.button("Create Account"):
            if not email_signup or not password_signup:
                st.warning("Please enter both email and password.")
            elif len(password_signup) < 6:
                st.warning("Password must be at least 6 characters long.")
            else:
                try:
                    auth.create_user_with_email_and_password(email_signup, password_signup)
                    st.success("Account created successfully! You can now switch to the Login tab.")
                except Exception as e:
                    error_msg = str(e).upper()
                    if "EMAIL_EXISTS" in error_msg:
                        st.error("An account with this email already exists.")
                    elif "INVALID_EMAIL" in error_msg:
                        st.error("Invalid email format.")
                    else:
                        st.error("Signup failed. Please try again.")

    return False
