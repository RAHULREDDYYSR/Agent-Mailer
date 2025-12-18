import streamlit as st
import uuid
import os
from dotenv import load_dotenv
from graph.graph import app
from utils.email_sender_tool import send_email

# Load environment variables
load_dotenv()

# Design and Layout Configuration
st.set_page_config(page_title="Agent Mailer - Commander", page_icon="✉️", layout="wide")

# Custom CSS for Sidebar Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stTextArea textarea {
        border-radius: 8px;
    }
    
    .stButton button {
        border-radius: 6px;
        font-weight: 600;
    }
    
    /* Subtle sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    @media (prefers-color-scheme: dark) {
        [data-testid="stSidebar"] {
            background-color: #1e1e1e;
        }
    }
    
    h1, h2, h3 {
        font-weight: 600;
        letter-spacing: -0.02em;
    }
</style>
""", unsafe_allow_html=True)

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

# --- SIDEBAR: CONTROLS ---
with st.sidebar:
    st.title("✉️ Agent Mailer")
    st.caption("Control Center")
    
    st.markdown("### 1. Job Context")
    job_description = st.text_area(
        "Job Description", 
        height=300, 
        placeholder="Paste the JD here...",
        label_visibility="collapsed"
    )
    
    st.markdown("### 2. Output Type")
    output_type = st.radio(
        "Generate:",
        ["Email", "LinkedIn Message", "Cover Letter"],
        key="type_selector"
    )
    
    st.markdown("---")
    generate_btn = st.button("🚀 Generate Draft", use_container_width=True, type="primary")
    
    st.markdown("---")
    if st.button("🗑️ Reset All", use_container_width=True):
        reset_session()

# --- MAIN: DISPLAY ---
if generate_btn and job_description:
    with st.spinner("🤖 Reasoning & Drafting..."):
        type_mapping = {
            "Email": "email",
            "LinkedIn Message": "linkedin_message",
            "Cover Letter": "cover_letter"
        }
        
        initial_state = {
            "job_description": job_description,
            "type": type_mapping[output_type]
        }
            
        config = get_config()
        final_state = app.invoke(initial_state, config=config)
        st.session_state.generated = True
        st.session_state.gen_count += 1 # Force increment on new generation
        st.rerun()

# --- PREVIEW AREA ---
config = get_config()
current_state = app.get_state(config)

if st.session_state.generated and current_state.values:
    state_values = current_state.values
    task_type = state_values.get("type", "email")
    
    st.header(f"📝 {output_type}")
    
    # Dynamic Editor Layout
    edited_content = {}
    k_suffix = st.session_state.gen_count
    
    if task_type == 'email':
        email_data = state_values.get('email', {})
        
        c1, c2 = st.columns([4, 1])
        with c1:
            recipient = st.text_input("To:", value=email_data.get('recipient', ''), key=f"rec_{k_suffix}")
            subject = st.text_input("Subject:", value=email_data.get('subject', ''), key=f"sub_{k_suffix}")
        
        body = st.text_area("Content", value=email_data.get('body', ''), height=500, key=f"body_{k_suffix}")
        
        # Attachments
        with st.expander("📎 Attachments (Drag & Drop)", expanded=True):
            uploaded_file = st.file_uploader("Upload file", type=['pdf', 'docx', 'txt'], key=f"up_{k_suffix}", label_visibility="collapsed")
            
            default_cv_path = r"C:\Users\rahul\work_space\LLM\langchain_deep_agents\draft_mail\agent-data\RAHUL_Y_S_CV.pdf"
            final_attachment_path = None
            
            if uploaded_file:
                upload_dir = "temp_uploads"
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                final_attachment_path = os.path.abspath(file_path)
                st.caption(f"Ready to send: `{uploaded_file.name}`")
            elif os.path.exists(default_cv_path):
                final_attachment_path = default_cv_path
                st.caption(f"Using Default CV: `{os.path.basename(default_cv_path)}`")
            else:
                st.warning("No attachment selected & default CV not found.")

        edited_content = {"recipient": recipient, "subject": subject, "body": body, "attachment_path": final_attachment_path}
        
    elif task_type == 'linkedin_message':
        linkedin_data = state_values.get('linkedin_message', {})
        recipient = st.text_input("To Profile:", value=linkedin_data.get('recipient', ''), key=f"li_to_{k_suffix}")
        body = st.text_area("Message", value=linkedin_data.get('body', ''), height=400, key=f"li_body_{k_suffix}")
        edited_content = {"recipient": recipient, "body": body}
        
    elif task_type == 'cover_letter':
        cl_data = state_values.get('cover_letter', {})
        body = st.text_area("Letter Content", value=cl_data.get('body', ''), height=600, key=f"cl_body_{k_suffix}")
        edited_content = {"body": body}

    # Footer Actions
    st.markdown("### Refine & Action")
    
    col_refine, col_send = st.columns([3, 1])
    
    with col_refine:
        feedback = st.text_input("Feedback", placeholder="Type instructions to refine this draft...", key=f"feed_{k_suffix}")
        if st.button("🔄 Refine Draft") and feedback:
            with st.spinner("Refining..."):
                app.update_state(config, {"feedback": feedback})
                app.invoke(None, config=config)
                st.session_state.gen_count += 1
                st.rerun()
                
    with col_send:
        if task_type == 'email':
            if st.button("📤 Send Now", type="primary", use_container_width=True):
                with st.spinner("Sending..."):
                    try:
                        app.update_state(config, {"attachment_path": edited_content.get('attachment_path')})
                        atts = [edited_content.get('attachment_path')] if edited_content.get('attachment_path') else []
                        res = send_email.invoke({
                            "recipient": edited_content['recipient'],
                            "subject": edited_content['subject'],
                            "body": edited_content['body'],
                            "attachments": atts
                        })
                        st.success("Sent!")
                        app.update_state(config, {"feedback": "send"})
                        app.invoke(None, config=config)
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            if st.button("✅ Approve", type="primary"):
                app.update_state(config, {"feedback": "send"})
                app.invoke(None, config=config)
                st.success("Approved!")
else:
    st.info("👈 Please enter a Job Description in the sidebar to get started.")
