import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api import api
from auth_utils import restore_session

restore_session()

# Page Header
st.markdown("""
<div style="margin-bottom: 24px;">
    <h1>👤 Profile & Context</h1>
    <p style="opacity: 0.6; margin-top: -8px;">Manage your account and personal context for better AI generations</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.get("access_token"):
    st.warning("⚠️ Please login to manage your profile.")
    st.stop()

# Get user data
user = st.session_state.user

if not user and st.session_state.access_token:
    user = api.get_user_me()
    if user:
        st.session_state.user = user

# ──────────────────────────────────────────────────────────────────────────────
# PROFILE SECTION
# ──────────────────────────────────────────────────────────────────────────────
if user:
    st.markdown(f"""
    <div class="premium-card">
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="width: 64px; height: 64px; background: linear-gradient(135deg, #6366f1, #818cf8); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; color: white;">
                {user.get('username', 'U')[0].upper()}
            </div>
            <div>
                <h3 style="margin: 0;">{user.get('username', 'Unknown')}</h3>
                <p style="margin: 0; opacity: 0.6;">{user.get('email', '')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="premium-card">
            <p style="opacity: 0.6; font-size: 0.85rem; margin: 0;">Role</p>
            <p style="font-weight: 600; margin: 4px 0 0 0;">{user.get('role', 'User').title()}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        created = user.get('created_at', '')
        st.markdown(f"""
        <div class="premium-card">
            <p style="opacity: 0.6; font-size: 0.85rem; margin: 0;">Member Since</p>
            <p style="font-weight: 600; margin: 4px 0 0 0;">{created[:10] if created else 'N/A'}</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.error("Unable to load profile data.")
    st.stop()

st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# CONTEXT UPLOAD SECTION
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="premium-card">
    <h3>📂 Personal Context</h3>
    <p style="opacity: 0.6;">Upload your resume, portfolio, or bio to personalize AI-generated content.</p>
</div>
""", unsafe_allow_html=True)

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

uploaded_files = st.file_uploader(
    "Upload documents",
    type=['pdf', 'txt', 'md', 'docx'],
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_key}",
    label_visibility="collapsed"
)

if st.button("📤 Upload & Process", type="primary", use_container_width=True):
    if uploaded_files:
        with st.spinner("Processing files..."):
            result = api.upload_context(uploaded_files)
            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                st.success(f"✅ Context updated! ({len(uploaded_files)} files processed)")
                st.session_state.uploader_key += 1
                updated_user = api.get_user_me()
                if updated_user:
                    st.session_state.user = updated_user
                    st.rerun()
    else:
        st.warning("Please select files first.")

st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# CONTEXT DISPLAY
# ──────────────────────────────────────────────────────────────────────────────
user = st.session_state.user
context_length = len(user.get('user_context', '') or '') if user else 0

st.markdown(f"""
<div class="premium-card stat-card">
    <div class="stat-value">{context_length:,}</div>
    <div class="stat-label">Characters in Context</div>
</div>
""", unsafe_allow_html=True)

if user and user.get('user_context'):
    with st.expander("📄 View Stored Context"):
        st.text(user.get('user_context', 'No context found.'))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🗑️ Clear All Context", type="secondary", use_container_width=True):
        with st.spinner("Deleting context..."):
            res = api.delete_context()
            if "error" in res:
                st.error(res['error'])
            else:
                st.success("Context cleared successfully.")
                updated_user = api.get_user_me()
                if updated_user:
                    st.session_state.user = updated_user
                    st.rerun()
else:
    st.info("No context uploaded yet. Upload your documents above to get started.")
