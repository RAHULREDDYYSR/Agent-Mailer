import streamlit as st
import os
import time

# Set page config once at the top level
st.set_page_config(
    page_title="Agent Mailer",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Global Styles
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), 'styles.css')
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

from api import api
from auth_utils import restore_session, logout_user, login_user

def main():
    # Attempt to restore session from cookie
    restore_session()

    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    
    if "user" not in st.session_state:
        st.session_state.user = None

    # Sidebar
    with st.sidebar:
        st.markdown("# ✉️ Agent Mailer")
        st.markdown("---")
        
        if st.session_state.user:
            st.markdown(f"**👤 {st.session_state.user.get('username')}**")
            st.caption(st.session_state.user.get('email', ''))
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                logout_user()
                st.rerun()
        else:
            st.info("Please login to continue")

    # Main Content
    if st.session_state.access_token:
        st.markdown("""
        <div class="premium-card" style="text-align: center; padding: 48px;">
            <h1 style="margin-bottom: 16px;">Welcome Back! 👋</h1>
            <p style="font-size: 1.1rem; opacity: 0.7; max-width: 500px; margin: 0 auto;">
                Use the sidebar to navigate between Dashboard, Generator, and Profile.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="premium-card stat-card">
                <div class="stat-value">📊</div>
                <div class="stat-label">Dashboard</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="premium-card stat-card">
                <div class="stat-value">🚀</div>
                <div class="stat-label">Generator</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="premium-card stat-card">
                <div class="stat-value">👤</div>
                <div class="stat-label">Profile</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 40px 20px 20px;">
            <h1 style="font-size: 3rem; margin-bottom: 24px;">✉️ Agent Mailer</h1>
            <p style="font-size: 1.25rem; opacity: 0.7; max-width: 600px; margin: 0 auto 32px;">
                AI-powered email generation tailored to your job applications. 
                Craft perfect cold emails, LinkedIn messages, and cover letters.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login / Register Forms
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

        with tab1:
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
                            st.rerun()
                        else:
                            st.error(result.get("detail", "Login failed. Please check your credentials."))
                else:
                    st.warning("Please enter both username and password.")

        with tab2:
            with st.form("register_form"):
                col1, col2 = st.columns(2)
                with col1:
                    first_name = st.text_input("First Name", key="reg_fname", placeholder="John")
                with col2:
                    last_name = st.text_input("Last Name", key="reg_lname", placeholder="Doe")
                    
                reg_username = st.text_input("Username", key="reg_user", placeholder="Choose a username")
                reg_email = st.text_input("Email", key="reg_email", placeholder="your@email.com")
                reg_password = st.text_input("Password", type="password", key="reg_pass", placeholder="Create a secure password")
                
                col3, col4 = st.columns(2)
                with col3:
                    phone = st.text_input("Phone Number", key="reg_phone", placeholder="+1234567890")
                with col4:
                    linkedin = st.text_input("LinkedIn URL", key="reg_linkedin", placeholder="https://linkedin.com/in/...")
                    
                col5, col6 = st.columns(2)
                with col5:
                    github = st.text_input("GitHub URL", key="reg_github", placeholder="https://github.com/...")
                with col6:
                    portfolio = st.text_input("Portfolio URL", key="reg_portfolio", placeholder="https://myportfolio.com")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                submitted = st.form_submit_button("Create Account →", use_container_width=True)
                
                if submitted:
                    if reg_username and reg_email and reg_password:
                        with st.spinner("Creating your account..."):
                            response = api.register(reg_username, reg_email, reg_password, first_name, last_name, phone, linkedin, github, portfolio)
                            if response is True:
                                st.success("🎉 Account created! Please sign in using the Login tab.")
                                if github and github.strip():
                                    st.info(
                                        "🐙 **GitHub context is being built in the background.** "
                                        "Your project READMEs are being scraped and summarised automatically — "
                                        "check the Profile page after logging in to see the status."
                                    )
                            else:
                                st.error(response.get("error", "Registration failed."))
                    else:
                        st.warning("Username, Email, and Password are required.")

if __name__ == "__main__":
    main()
