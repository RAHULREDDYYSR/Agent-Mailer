import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api import api
from auth_utils import restore_session

restore_session()

if not st.session_state.get("access_token"):
    st.warning("⚠️ Please login to access job details.")
    st.stop()

if "selected_job_id" not in st.session_state:
    st.warning("No job selected. Redirecting to Dashboard...")
    st.switch_page("pages/02_Dashboard.py")

jd_id = st.session_state.selected_job_id

# Fetch job details
jobs = api.get_jobs()
job = next((j for j in jobs if j.get("id") == jd_id), None)

if not job:
    st.error("Job not found.")
    if st.button("Back to Dashboard"):
        st.switch_page("pages/02_Dashboard.py")
    st.stop()

# Fetch contents
all_contents = api.get_all_generated_contents()
job_contents = [c for c in all_contents if c.get('jd_id') == jd_id] if all_contents else []

# Page Header
st.markdown(f"""
<div style="margin-bottom: 24px;">
    <h1>💼 {job.get('title', 'Untitled')}</h1>
    <p style="opacity: 0.6; margin-top: -8px;">at {job.get('company', 'Unknown Company')}</p>
</div>
""", unsafe_allow_html=True)

if st.button("⬅️ Back to Dashboard"):
    st.switch_page("pages/02_Dashboard.py")
st.markdown("---")

# Main page navigation
tab_jd, tab_context, tab_content, tab_draft = st.tabs(["📄 Job Description", "🧩 Context", "📝 Generated Content", "✍️ Draft"])

with tab_jd:
    st.markdown("### Job Description")
    st.text_area("", job.get('jd_text', ''), height=400, disabled=True)

with tab_context:
    st.markdown("### Analyzed Context")
    if job.get('generated_context'):
        st.json(job.get('generated_context'))
    else:
        st.info("No generated context available.")

with tab_content:
    st.markdown("### Generated Content")
    if job_contents:
        for c in job_contents:
            st.markdown(f"**{str(c.get('content_type', 'Document')).replace('_', ' ').title()}**")
            if c.get('subject'):
                st.caption(f"Subject: {c.get('subject')}")
            st.text_area("Content", c.get('body', ''), height=200, disabled=True, key=f"content_{c.get('id')}")
            st.markdown("---")
    else:
        st.info("No content generated for this job yet.")

with tab_draft:
    st.markdown("### Create New Draft")
    st.markdown("Select a type of content to generate for this job:")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📧 Generate Email", use_container_width=True):
            st.session_state.current_jd_id = jd_id
            st.session_state.dashboard_draft_type = "email"
            st.switch_page("pages/03_Generator.py")
    with col2:
        if st.button("💼 Generate LinkedIn", use_container_width=True):
            st.session_state.current_jd_id = jd_id
            st.session_state.dashboard_draft_type = "linkedin_message"
            st.switch_page("pages/03_Generator.py")
    with col3:
        if st.button("📝 Generate Cover Letter", use_container_width=True):
            st.session_state.current_jd_id = jd_id
            st.session_state.dashboard_draft_type = "cover_letter"
            st.switch_page("pages/03_Generator.py")
