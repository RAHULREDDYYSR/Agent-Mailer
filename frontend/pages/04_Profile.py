import streamlit as st
import sys
import os
import time
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
if st.session_state.get("access_token"):
    user = api.get_user_me()
    if user:
        st.session_state.user = user
    else:
        user = st.session_state.get("user")
else:
    user = None

# ──────────────────────────────────────────────────────────────────────────────
# PROFILE SECTION
# ──────────────────────────────────────────────────────────────────────────────
if user:
    # Main Profile Card
    st.markdown(f"""
    <div class="premium-card">
        <div style="display: flex; align-items: center; gap: 20px;">
            <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #6366f1, #818cf8); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2rem; color: white; box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.4);">
                {user.get('username', 'U')[0].upper()}
            </div>
            <div>
                <h3 style="margin: 0; font-size: 1.5rem;">{user.get('first_name') or ''} {user.get('last_name') or user.get('username')}</h3>
                <p style="margin: 4px 0 0 0; opacity: 0.8;">{user.get('email', '')}</p>
                <span style="display: inline-block; background: rgba(99, 102, 241, 0.1); color: #818cf8; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin-top: 8px;">
                    {user.get('role', 'User').title()}
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Details Grid
    st.markdown("### Personal Details")

    c1, c2 = st.columns(2)

    with c1:
        phone = user.get('phone') or 'Not provided'
        linkedin = user.get('linkedin') or 'Not provided'

        st.markdown(f"""
        <div class="premium-card" style="height: 100%;">
            <div style="margin-bottom: 16px;">
                <p style="opacity: 0.6; font-size: 0.85rem; margin: 0;">📱 Phone</p>
                <p style="font-weight: 500; margin: 4px 0 0 0;">{phone}</p>
            </div>
            <div>
                <p style="opacity: 0.6; font-size: 0.85rem; margin: 0;">💼 LinkedIn</p>
                <p style="font-weight: 500; margin: 4px 0 0 0;">
                    {'<a href="' + linkedin + '" target="_blank" style="text-decoration:none;">View Profile ↗</a>' if linkedin.startswith('http') else linkedin}
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        github = user.get('github') or 'Not provided'
        portfolio = user.get('portfolio') or 'Not provided'

        st.markdown(f"""
        <div class="premium-card" style="height: 100%;">
            <div style="margin-bottom: 16px;">
                <p style="opacity: 0.6; font-size: 0.85rem; margin: 0;">💻 GitHub</p>
                <p style="font-weight: 500; margin: 4px 0 0 0;">
                    {'<a href="' + github + '" target="_blank" style="text-decoration:none;">View Profile ↗</a>' if github.startswith('http') else github}
                </p>
            </div>
            <div>
                <p style="opacity: 0.6; font-size: 0.85rem; margin: 0;">🌐 Portfolio</p>
                <p style="font-weight: 500; margin: 4px 0 0 0;">
                    {'<a href="' + portfolio + '" target="_blank" style="text-decoration:none;">Visit Site ↗</a>' if portfolio.startswith('http') else portfolio}
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    created = user.get('created_at', '')
    st.caption(f"Member since: {created[:10] if created else 'Unknown'}")
else:
    st.error("Unable to load profile data.")
    st.stop()

st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# GITHUB CONTEXT STATUS PANEL
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("### 🐙 GitHub Project Context")

github_status = api.get_github_context_status()
has_github = github_status.get("has_github", False)
context_ready = github_status.get("context_ready", False)
repos_count = github_status.get("repos_summarised", 0)
github_url = github_status.get("github_url", "")

if not has_github:
    st.markdown("""
    <div class="premium-card" style="border-left: 4px solid #f59e0b;">
        <p style="margin: 0; opacity: 0.9;">⚠️ No GitHub URL found on your profile. Add one to enable automatic project context scraping.</p>
    </div>
    """, unsafe_allow_html=True)
elif context_ready:
    st.markdown(f"""
    <div class="premium-card" style="border-left: 4px solid #10b981;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <p style="margin: 0; font-weight: 600; color: #10b981;">✅ GitHub context is ready</p>
                <p style="margin: 4px 0 0 0; opacity: 0.7; font-size: 0.9rem;">
                    {repos_count} project{'s' if repos_count != 1 else ''} summarised from
                    <a href="{github_url}" target="_blank" style="color: #818cf8;">{github_url}</a>
                </p>
                <p style="margin: 4px 0 0 0; opacity: 0.6; font-size: 0.8rem;">
                    This context is automatically used when generating outreach emails and messages.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="premium-card" style="border-left: 4px solid #6366f1;">
        <p style="margin: 0; font-weight: 600; color: #818cf8;">⏳ GitHub scrape in progress...</p>
        <p style="margin: 4px 0 0 0; opacity: 0.7; font-size: 0.9rem;">
            Your repositories are being analysed in the background.
            This page will update automatically.
        </p>
    </div>
    """, unsafe_allow_html=True)
    # Auto-refresh while pending
    time.sleep(4)
    st.rerun()

# Re-scrape button (always visible if GitHub URL exists)
if has_github:
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        if st.button("🔄 Re-scrape GitHub", use_container_width=True):
            with st.spinner("Triggering GitHub scrape..."):
                result = api.scrape_github()
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.success(f"✅ {result.get('message', 'Scrape complete!')}")
                    time.sleep(1)
                    st.rerun()
    with col_info:
        st.caption(
            "Re-scraping fetches the latest READMEs from your GitHub profile, "
            "replaces the old project summaries, and updates your context."
        )

st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# CONTEXT UPLOAD SECTION
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="premium-card">
    <h3>📂 Additional Context (Optional)</h3>
    <p style="opacity: 0.6;">Upload your resume or bio to supplement the GitHub-sourced context. GitHub projects are auto-populated — you only need to upload extra files if needed.</p>
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
    st.info("No context yet. GitHub projects will appear here automatically after scraping completes.")
