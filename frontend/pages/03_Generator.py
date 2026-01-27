import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api import api
import json
from auth_utils import restore_session

restore_session()

# Page Header
st.markdown("""
<div style="margin-bottom: 24px;">
    <h1>🚀 Draft Generator</h1>
    <p style="opacity: 0.6; margin-top: -8px;">Create personalized emails and messages in 3 simple steps</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.get("access_token"):
    st.warning("⚠️ Please login to generate drafts.")
    st.stop()

# Handle Dashboard redirect
if "dashboard_draft_type" in st.session_state and st.session_state.dashboard_draft_type:
    st.session_state.selected_type = st.session_state.dashboard_draft_type
    st.session_state.gen_step = 2
    st.session_state.dashboard_draft_type = None
    st.rerun()

# Initialize session state
if "gen_step" not in st.session_state:
    st.session_state.gen_step = 1
if "current_jd_id" not in st.session_state:
    st.session_state.current_jd_id = None
if "generated_draft" not in st.session_state:
    st.session_state.generated_draft = None

# Progress Indicator
steps = ["Analyze JD", "Select Type", "Review & Send", "Complete"]
progress_cols = st.columns(len(steps))
for i, (col, step) in enumerate(zip(progress_cols, steps)):
    with col:
        if i + 1 < st.session_state.gen_step:
            st.markdown(f"<div style='text-align: center; color: #22c55e;'>✅<br><small>{step}</small></div>", unsafe_allow_html=True)
        elif i + 1 == st.session_state.gen_step:
            st.markdown(f"<div style='text-align: center; color: #6366f1; font-weight: 600;'>●<br><small>{step}</small></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align: center; opacity: 0.4;'>○<br><small>{step}</small></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# STEP 1: Job Description
# ──────────────────────────────────────────────────────────────────────────────
if st.session_state.gen_step == 1:
    st.markdown("""
    <div class="premium-card">
        <h3>Step 1: Analyze Job Description</h3>
        <p style="opacity: 0.6;">Paste the job posting below. Our AI will extract key requirements and match them to your profile.</p>
    </div>
    """, unsafe_allow_html=True)
    
    jd_text = st.text_area(
        "Job Description",
        height=250,
        placeholder="Paste the full job description here...",
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Analyze & Continue →", type="primary", use_container_width=True):
        if jd_text:
            with st.spinner("Analyzing job description..."):
                response = api.generate_context(jd_text)
                if "job_title" in response or "raw_content" in response:
                    jobs = api.get_jobs()
                    if jobs:
                        latest_job = jobs[-1] 
                        st.session_state.current_jd_id = latest_job['id']
                        st.success("✅ Analysis complete!")
                        st.session_state.gen_step = 2
                        st.rerun()
                    else:
                        st.error("Failed to save job context.")
                else:
                    st.error(f"Error: {response}")
        else:
            st.warning("Please paste a job description first.")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 2: Choose Output Type
# ──────────────────────────────────────────────────────────────────────────────
if st.session_state.gen_step == 2:
    st.markdown("""
    <div class="premium-card">
        <h3>Step 2: Select Output Type</h3>
        <p style="opacity: 0.6;">Choose what type of content you want to generate.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        email_selected = st.button("📧 Cold Email", use_container_width=True, type="primary" if st.session_state.get("selected_type") == "email" else "secondary")
        if email_selected:
            st.session_state.selected_type = "email"
    
    with col2:
        linkedin_selected = st.button("💼 LinkedIn Message", use_container_width=True, type="primary" if st.session_state.get("selected_type") == "linkedin_message" else "secondary")
        if linkedin_selected:
            st.session_state.selected_type = "linkedin_message"
    
    with col3:
        cover_selected = st.button("📝 Cover Letter", use_container_width=True, type="primary" if st.session_state.get("selected_type") == "cover_letter" else "secondary")
        if cover_selected:
            st.session_state.selected_type = "cover_letter"
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    selected = st.session_state.get("selected_type", "email")
    draft_type = st.radio("Selected type:", ["email", "linkedin_message", "cover_letter"], index=["email", "linkedin_message", "cover_letter"].index(selected), horizontal=True, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    feedback = st.text_area("Additional Instructions (Optional)", placeholder="E.g. Focus on my Python skills, keep it casual, etc.", help="Add specific instructions for the AI to follow when generating the draft.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_back, col_next = st.columns([1, 3])
    with col_back:
        if st.button("← Back"):
            st.session_state.gen_step = 1
            st.rerun()
    with col_next:
        if st.button("Generate Draft →", type="primary", use_container_width=True):
            if st.session_state.current_jd_id:
                with st.spinner(f"Generating {draft_type}..."):
                    response = api.draft_context(st.session_state.current_jd_id, draft_type, feedback)
                    if "body" in response:
                        st.session_state.generated_draft = response
                        st.session_state.generated_draft['type'] = draft_type
                        st.session_state.gen_step = 3
                        st.rerun()
                    else:
                        st.error(f"Error: {response}")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 3: Edit & Send
# ──────────────────────────────────────────────────────────────────────────────
if st.session_state.gen_step == 3:
    st.markdown("""
    <div class="premium-card">
        <h3>Step 3: Review & Send</h3>
        <p style="opacity: 0.6;">Review the generated content, make edits, and send when ready.</p>
    </div>
    """, unsafe_allow_html=True)
    
    draft = st.session_state.generated_draft
    draft_type = draft.get('type', 'email')
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            recipient = st.text_input("📬 Recipient", value=draft.get('recipient', ''), placeholder="recipient@company.com")
        with col2:
            subject = st.text_input("📋 Subject", value=draft.get('subject', ''))
        
        body = st.text_area("✏️ Content", value=draft.get('body', ''), height=350)

        # --- PDF Download (Cover Letter Only) ---
        if draft_type == "cover_letter":
            # Generate PDF on the fly based on current body content
            # We use a unique key based on content hash or length to allow re-generation if text changes
            # Actually st.download_button is simpler: it will use the current 'body' when clicked if we generate the data
            
            with st.spinner("Generating PDF..."):
                # Note: generating on every rerun might be expensive. 
                # Ideally we generate only when needed, but download_button needs 'data' upfront.
                # Optimization: Cache the PDF if body hasn't changed.
                
                pdf_bytes = api.generate_pdf(body)
                if pdf_bytes:
                    st.download_button(
                        label="📄 Download as PDF",
                        data=pdf_bytes,
                        file_name="cover_letter.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.error("Failed to generate PDF")
        
        files = None
        if draft_type == 'email':
            st.markdown("**📎 Attachments**")
            files = st.file_uploader("Upload files", accept_multiple_files=True, label_visibility="collapsed", key="email_attachments")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_back, col_send = st.columns([1, 3])
        with col_back:
            back_btn = st.button("← Back")
        with col_send:
            send_btn = st.button("Send Email 📨", type="primary", use_container_width=True)
        
        if back_btn:
            st.session_state.gen_step = 2
            st.rerun()
        
        if send_btn:
            if not recipient or not body:
                st.error("Recipient and content are required.")
            else:
                with st.spinner("Sending..."):
                    result = api.send_email(recipient, subject, body, files)
                    if "message" in result and "success" in result["message"].lower():
                        st.balloons()
                        st.session_state.gen_step = 4
                        st.rerun()
                    else:
                        st.error(f"Failed: {result}")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 4: Success
# ──────────────────────────────────────────────────────────────────────────────
if st.session_state.gen_step == 4:
    st.markdown("""
    <div class="premium-card" style="text-align: center; padding: 64px;">
        <div style="font-size: 4rem; margin-bottom: 16px;">🎉</div>
        <h2 style="color: #22c55e;">Successfully Sent!</h2>
        <p style="opacity: 0.6; margin-bottom: 24px;">Your message has been delivered.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Create Another Draft →", type="primary", use_container_width=True):
        st.session_state.gen_step = 1
        st.session_state.current_jd_id = None
        st.session_state.generated_draft = None
        st.rerun()
