import streamlit as st
import uuid
import os
from dotenv import load_dotenv
from graph.graph import app
from utils.email_sender_tool import send_email

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Agent Mailer - Split View", page_icon="🌗", layout="wide")

# Session State Initialization
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "generated" not in st.session_state:
    st.session_state.generated = False
if "gen_count" not in st.session_state:
    st.session_state.gen_count = 0

def get_config():
    return {"configurable": {"thread_id": st.session_state.thread_id}}

def reset_session():
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.generated = False
    st.session_state.gen_count = 0
    st.rerun()

# Layout
col_left, col_right = st.columns([1, 1], gap="large")

# --- LEFT COLUMN: INPUTS ---
with col_left:
    st.header("Context & Config")
    st.markdown("---")
    
    output_type = st.selectbox("Output Type", ["Email", "LinkedIn Message", "Cover Letter"])
    
    st.markdown("#### Job Description")
    job_description = st.text_area("Paste JD here", height=400, label_visibility="collapsed")
    
    col_act1, col_act2 = st.columns([2, 1])
    with col_act1:
        generate_btn = st.button("Generate Output ⏩", type="primary", use_container_width=True)
    with col_act2:
        if st.button("Reset 🔄", use_container_width=True):
            reset_session()
            
    if generate_btn and job_description:
        with st.status("Thinking...", expanded=True):
            st.write(" analyzing job description...")
            type_mapping = {"Email": "email", "LinkedIn Message": "linkedin_message", "Cover Letter": "cover_letter"}
            initial_state = {"job_description": job_description, "type": type_mapping[output_type]}
            config = get_config()
            app.invoke(initial_state, config=config)
            st.session_state.generated = True
            st.session_state.gen_count += 1
            st.write(" done!")
            st.rerun()

# --- RIGHT COLUMN: OUTPUT ---
with col_right:
    st.header("Draft & Actions")
    st.markdown("---")
    
    config = get_config()
    current_state = app.get_state(config)
    
    if st.session_state.generated and current_state.values:
        state_values = current_state.values
        task_type = state_values.get("type", "email")
        k_suffix = st.session_state.gen_count
        edited_content = {}
        
        tab_preview, tab_refine = st.tabs(["📄 Preview", "⚙️ Refine"])
        
        with tab_preview:
            if task_type == 'email':
                email_data = state_values.get('email', {})
                rcp = st.text_input("To", value=email_data.get('recipient', ''), key=f"to_{k_suffix}")
                sub = st.text_input("Subject", value=email_data.get('subject', ''), key=f"sub_{k_suffix}")
                body = st.text_area("Content", value=email_data.get('body', ''), height=500, key=f"body_{k_suffix}")
                
                uploaded_file = st.file_uploader("Attach File", key=f"up_{k_suffix}")
                default_cv_path = r"C:\Users\rahul\work_space\LLM\langchain_deep_agents\draft_mail\agent-data\RAHUL_Y_S_CV.pdf"
                final_attachment_path = None
                
                if uploaded_file:
                    upload_dir = "temp_uploads"
                    os.makedirs(upload_dir, exist_ok=True)
                    file_path = os.path.join(upload_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    final_attachment_path = os.path.abspath(file_path)
                elif os.path.exists(default_cv_path):
                    final_attachment_path = default_cv_path
                    st.caption(f"Using Default CV: {os.path.basename(default_cv_path)}")
                
                edited_content = {"recipient": rcp, "subject": sub, "body": body, "attachment_path": final_attachment_path}
                
                st.markdown("---")
                if st.button("📤 Send Email", type="primary", use_container_width=True):
                     with st.spinner("Sending..."):
                        try:
                            atts = [edited_content.get('attachment_path')] if edited_content.get('attachment_path') else []
                            res = send_email.invoke({
                                "recipient": edited_content['recipient'],
                                "subject": edited_content['subject'],
                                "body": edited_content['body'],
                                "attachments": atts
                            })
                            st.success(f"Sent: {res}")
                            app.update_state(config, {"feedback": "send"})
                            app.invoke(None, config=config)
                        except Exception as e:
                            st.error(str(e))

            elif task_type == 'linkedin_message':
                linkedin_data = state_values.get('linkedin_message', {})
                rcp = st.text_input("Profile", value=linkedin_data.get('recipient', ''), key=f"li_to_{k_suffix}")
                body = st.text_area("Message", value=linkedin_data.get('body', ''), height=400, key=f"li_body_{k_suffix}")
                st.markdown("---")
                if st.button("Approve & Finish", type="primary", use_container_width=True):
                    app.update_state(config, {"feedback": "send"})
                    app.invoke(None, config=config)
                    st.success("Draft Saved.")

            elif task_type == 'cover_letter':
                cl_data = state_values.get('cover_letter', {})
                body = st.text_area("Letter", value=cl_data.get('body', ''), height=600, key=f"cl_body_{k_suffix}")
                st.markdown("---")
                if st.button("Approve & Finish", type="primary", use_container_width=True):
                    app.update_state(config, {"feedback": "send"})
                    app.invoke(None, config=config)
                    st.success("Draft Saved.")

        with tab_refine:
            st.markdown("#### Give Feedback")
            feedback = st.text_area("Instructions", placeholder="Make it more formal...", key=f"feed_{k_suffix}")
            if st.button("Refine Draft", use_container_width=True):
                if feedback:
                    app.update_state(config, {"feedback": feedback})
                    app.invoke(None, config=config)
                    st.session_state.gen_count += 1
                    st.rerun()
    else:
        st.info("👈 Waiting for input...")
