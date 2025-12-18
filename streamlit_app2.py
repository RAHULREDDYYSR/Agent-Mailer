import streamlit as st
import uuid
import os
from dotenv import load_dotenv
from graph.graph import app
from utils.email_sender_tool import send_email

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Agent Mailer - Wizard", page_icon="🪄", layout="wide")

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

st.title("🪄 Application Wizard")

# --- STEP 1: CONFIGURATION ---
step1_expanded = not st.session_state.generated
with st.expander("Step 1: Input Details", expanded=step1_expanded):
    st.markdown("Provide the job details to get started.")
    
    col_jd, col_opt = st.columns([2, 1])
    with col_jd:
        job_description = st.text_area("Job Description", height=200, placeholder="Paste JD here...")
    
    with col_opt:
        output_type = st.radio("I want to write a:", ["Email", "LinkedIn Message", "Cover Letter"])
        st.write("")
        if st.button("Generate Draft ➡️", type="primary"):
            if job_description:
                with st.spinner("consulting the agents..."):
                    type_mapping = {"Email": "email", "LinkedIn Message": "linkedin_message", "Cover Letter": "cover_letter"}
                    initial_state = {"job_description": job_description, "type": type_mapping[output_type]}
                    config = get_config()
                    app.invoke(initial_state, config=config)
                    st.session_state.generated = True
                    st.session_state.gen_count += 1
                    st.rerun()
            else:
                st.error("Please provide a Job Description.")

# --- STEP 2: REVIEW & REFINE ---
if st.session_state.generated:
    st.markdown("---")
    st.subheader("Step 2: Review & Send")
    
    config = get_config()
    current_state = app.get_state(config)
    
    if current_state.values:
        state_values = current_state.values
        task_type = state_values.get("type", "email")
        k_suffix = st.session_state.gen_count
        edited_content = {}
        
        # Two-column layout for editing
        col_preview, col_controls = st.columns([2, 1])
        
        with col_preview:
            st.caption("Draft Preview (Editable)")
            if task_type == 'email':
                email_data = state_values.get('email', {})
                recipient = st.text_input("To", value=email_data.get('recipient', ''), key=f"to_{k_suffix}")
                subject = st.text_input("Subject", value=email_data.get('subject', ''), key=f"sub_{k_suffix}")
                body = st.text_area("Body", value=email_data.get('body', ''), height=450, key=f"body_{k_suffix}")
                
                 # Attachments
                uploaded_file = st.file_uploader("Add Attachment", type=['pdf', 'docx', 'txt'], key=f"up_{k_suffix}")
                default_cv_path = r"C:\Users\rahul\work_space\LLM\langchain_deep_agents\draft_mail\agent-data\RAHUL_Y_S_CV.pdf"
                final_attachment_path = None
                
                if uploaded_file:
                    upload_dir = "temp_uploads"
                    os.makedirs(upload_dir, exist_ok=True)
                    file_path = os.path.join(upload_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    final_attachment_path = os.path.abspath(file_path)
                    st.toast(f"Attached: {uploaded_file.name}")
                elif os.path.exists(default_cv_path):
                    final_attachment_path = default_cv_path
                
                edited_content = {"recipient": recipient, "subject": subject, "body": body, "attachment_path": final_attachment_path}

            elif task_type == 'linkedin_message':
                linkedin_data = state_values.get('linkedin_message', {})
                recipient = st.text_input("To", value=linkedin_data.get('recipient', ''), key=f"li_to_{k_suffix}")
                body = st.text_area("Message", value=linkedin_data.get('body', ''), height=400, key=f"li_body_{k_suffix}")
                edited_content = {"recipient": recipient, "body": body}
                
            elif task_type == 'cover_letter':
                cl_data = state_values.get('cover_letter', {})
                body = st.text_area("Letter", value=cl_data.get('body', ''), height=600, key=f"cl_body_{k_suffix}")
                edited_content = {"body": body}

        with col_controls:
            st.info("💡 Review the draft on the left. Use the controls below to refine or send.")
            
            with st.container(border=True):
                st.markdown("**Refinement**")
                feedback = st.text_area("Instructions", placeholder="E.g. Make it shorter...", height=100, key=f"feed_{k_suffix}")
                if st.button("Applying Changes 🔄", use_container_width=True):
                    if feedback:
                        with st.spinner("Polishing..."):
                            app.update_state(config, {"feedback": feedback})
                            app.invoke(None, config=config)
                            st.session_state.gen_count += 1
                            st.rerun()
            
            st.write("")
            st.write("")
            
            if task_type == 'email':
                if st.button("Send Email 📤", type="primary", use_container_width=True):
                    with st.spinner("Dispatching..."):
                        try:
                            # Attachments logic
                            atts = [edited_content.get('attachment_path')] if edited_content.get('attachment_path') else []
                            res = send_email.invoke({
                                "recipient": edited_content['recipient'],
                                "subject": edited_content['subject'],
                                "body": edited_content['body'],
                                "attachments": atts
                            })
                            st.balloons()
                            st.success(f"Success: {res}")
                            app.update_state(config, {"feedback": "send"})
                            app.invoke(None, config=config)
                        except Exception as e:
                            st.error(str(e))
            else:
                 if st.button("Mark Complete ✅", type="primary", use_container_width=True):
                    app.update_state(config, {"feedback": "send"})
                    app.invoke(None, config=config)
                    st.balloons()
                    st.success("Done!")
                    
            if st.button("Start Over 🆕", use_container_width=True):
                reset_session()
