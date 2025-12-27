import streamlit as st
import extra_streamlit_components as stx
from api import api

import os

# Singleton manager
@st.cache_resource
def get_cookie_manager():
    return stx.CookieManager()

cookie_manager = get_cookie_manager()

def load_global_css():
    css_path = os.path.join(os.path.dirname(__file__), 'styles.css')
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def restore_session():
    """Checks for cookie and restores session if valid"""
    # Load CSS on every page load/auth check
    load_global_css()
    
    # Initialize defaults if not present
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "user" not in st.session_state:
        st.session_state.user = None

    # If already logged in, do nothing
    if st.session_state.get("access_token"):
        return

    # Check cookie
    token = cookie_manager.get("access_token")
    if token:
        st.session_state.access_token = token
        # Validate/Fetch user info
        user_info = api.get_user_me()
        if user_info and isinstance(user_info, dict) and "username" in user_info:
            st.session_state.user = user_info
        else:
            # Token invalid/expired or user fetch failed
            st.session_state.access_token = None
            cookie_manager.delete("access_token")

def login_user(token_response):
    """Sets session and cookie"""
    token = token_response["access_token"]
    st.session_state.access_token = token
    cookie_manager.set("access_token", token, key="set_auth_token")
    
    # Fetch user info
    user_info = api.get_user_me()
    if user_info:
        st.session_state.user = user_info

def logout_user():
    """Clears session and cookie"""
    st.session_state.access_token = None
    st.session_state.user = None
    cookie_manager.delete("access_token", key="del_auth_token")
