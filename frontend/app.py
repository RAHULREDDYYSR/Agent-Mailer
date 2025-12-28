import streamlit as st
import os

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

from auth_utils import restore_session, logout_user

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
        <div style="text-align: center; padding: 80px 20px;">
            <h1 style="font-size: 3rem; margin-bottom: 24px;">✉️ Agent Mailer</h1>
            <p style="font-size: 1.25rem; opacity: 0.7; max-width: 600px; margin: 0 auto 32px;">
                AI-powered email generation tailored to your job applications. 
                Craft perfect cold emails, LinkedIn messages, and cover letters.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.warning("👆 Navigate to **Login** page to get started")

if __name__ == "__main__":
    main()
