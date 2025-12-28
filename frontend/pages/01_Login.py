import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api import api
import time
from auth_utils import login_user, logout_user, restore_session

restore_session()

# Page Header
st.markdown("""
<div style="text-align: center; padding: 40px 0 20px;">
    <h1>🔐 Authentication</h1>
    <p style="opacity: 0.6;">Sign in to access your AI-powered email assistant</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.get("access_token"):
    st.markdown("""
    <div class="premium-card" style="text-align: center;">
        <h3>✅ Already Logged In</h3>
        <p>You're signed in. Navigate to Dashboard or Generator from the sidebar.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Logout", type="primary", use_container_width=True):
        logout_user()
        st.success("Logged out successfully!")
        time.sleep(1)
        st.rerun()
else:
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

    with tab1:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        
        login_username = st.text_input("Username", key="login_user", placeholder="Enter your username")
        login_password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Sign In →", type="primary", use_container_width=True):
            if login_username and login_password:
                with st.spinner("Signing in..."):
                    result = api.login(login_username, login_password)
                    if "access_token" in result:
                        login_user(result)
                        st.success("Welcome back! Redirecting...")
                        time.sleep(1)
                        st.switch_page("pages/02_Dashboard.py")
                    else:
                        st.error(result.get("detail", "Login failed. Please check your credentials."))
            else:
                st.warning("Please enter both username and password.")
        
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        
        reg_username = st.text_input("Username", key="reg_user", placeholder="Choose a username")
        reg_email = st.text_input("Email", key="reg_email", placeholder="your@email.com")
        reg_password = st.text_input("Password", type="password", key="reg_pass", placeholder="Create a secure password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Create Account →", use_container_width=True):
            if reg_username and reg_email and reg_password:
                with st.spinner("Creating your account..."):
                    response = api.register(reg_username, reg_email, reg_password)
                    if response is True:
                        st.success("🎉 Account created! Please sign in.")
                    else:
                        st.error(response.get("error", "Registration failed."))
            else:
                st.warning("All fields are required.")
        
        st.markdown('</div>', unsafe_allow_html=True)
