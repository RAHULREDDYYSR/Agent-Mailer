import streamlit as st
import uuid
import os
from dotenv import load_dotenv
from graph.graph import app
from utils.email_sender_tool import send_email

# Load environment variables
load_dotenv()

# Design and Layout Configuration
st.set_page_config(page_title="Agent Mailer", page_icon="✉️", layout="wide")

# Custom CSS for Industrial/Clean Look
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
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
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

if "current_view_state" not in st.session_state:
    st.session_state.current_view_state = None  # To store the graph state object

def get_config():
    return {"configurable": {"thread_id": st.session_state.thread_id}}

def reset_session():
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.generated = False
    st.session_state.current_view_state = None
    st.rerun()

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Operations")
    st.markdown("---")
    if st.button("🗑️ Clear History & Reset", use_container_width=True):
        reset_session()
    
    st.markdown("### ℹ️ About")
    st.info("Agent Mailer uses LangGraph to draft and refine professional communications.")


# --- MAIN CONTENT ---
st.title("✉️ Agent Mailer")
st.markdown("### Intelligent Job Application Assistant")

# Input Section
with st.container():
    col1, col2 = st.columns([2, 1])
    
    with col1:
        job_description = st.text_area(
            "📋 Paste Job Description Here", 
            height=200, 
            placeholder="Paste the full job description or relevant context..."
        )
    
    with col2:
        st.markdown("### 🎯 Output Type")
        output_type = st.radio(
            "Select the type of draft to generate:",
            ["Email", "LinkedIn Message", "Cover Letter"],
            key="type_selector"
        )
        
        generate_btn = st.button("🚀 Generate Draft", use_container_width=True, type="primary")

# Generation Logic
if generate_btn and job_description:
    with st.spinner("🤖 Analyzing and Drafting..."):
        # Map UI selection to graph keys
        # Map UI selection to graph keys
        type_mapping = {
            "Email": "email",
            "LinkedIn Message": "linkedin_message",
            "Cover Letter": "cover_letter"
        }
        
        initial_state = {
            "job_description": job_description,
            "type": type_mapping[output_type]
        }
            
        # Run graph until interruption
        # We assume the graph has been compiled with interrupt_before=['reviewer']
        # We need to iterate stream to get to the interrupt
        # using invoke won't stop correctly for checking, stream is better or invoke with proper config
        
        # Invoking start
        config = get_config()
        # Clean start requires new thread usually, but we reuse for session
        
        # We use app.invoke but we expect it to stop. 
        # Actually app.invoke runs to completion or interrupt.
        final_state = app.invoke(initial_state, config=config)
        
        st.session_state.generated = True
        st.rerun()

# --- DISPLAY & REFINE SECTION ---

# Check current state of graph
config = get_config()
current_state = app.get_state(config)

if "gen_count" not in st.session_state:
    st.session_state.gen_count = 0

if st.session_state.generated and current_state.values:
    state_values = current_state.values
    task_type = state_values.get("type", "email")
    
    st.markdown("---")
    st.subheader(f"📝 {output_type} Draft")
    
    # Dynamic Editor Layout
    edited_content = {}
    
    # Use gen_count in keys to force refresh on new generation
    k_suffix = st.session_state.gen_count
    
    if task_type == 'email':
        email_data = state_values.get('email', {})
        
        col_meta, col_space = st.columns([3, 1])
        with col_meta:
            recipient = st.text_input("To:", value=email_data.get('recipient', ''), key=f"email_to_{k_suffix}")
            subject = st.text_input("Subject:", value=email_data.get('subject', ''), key=f"email_sub_{k_suffix}")

        body = st.text_area("Body:", value=email_data.get('body', ''), height=400, key=f"email_body_{k_suffix}")
        
        # Attachment Logic
        st.markdown("#### 📎 Attachments")
        uploaded_file = st.file_uploader("Upload a file (Drag & Drop)", type=['pdf', 'docx', 'txt', 'png', 'jpg'], key=f"upload_{k_suffix}")
        
        default_cv_path = r"C:\Users\rahul\work_space\LLM\langchain_deep_agents\draft_mail\RAHUL_Y_S_CV.pdf"
        final_attachment_path = None
        
        if uploaded_file:
            # Save uploaded file temporarily
            upload_dir = "temp_uploads"
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            final_attachment_path = os.path.abspath(file_path)
            st.success(f"Attached: {uploaded_file.name}")
        else:
            final_attachment_path = default_cv_path
            if os.path.exists(default_cv_path):
                st.info(f"Using default CV: {os.path.basename(default_cv_path)}")
            else:
                st.warning(f"Default CV not found at: {default_cv_path}")
        
        edited_content = {"recipient": recipient, "subject": subject, "body": body, "attachment_path": final_attachment_path}
        
    elif task_type == 'linkedin_message':

        linkedin_data = state_values.get('linkedin_message', {})
        recipient = st.text_input("To (Profile):", value=linkedin_data.get('recipient', ''), key=f"li_to_{k_suffix}")
        body = st.text_area("Message:", value=linkedin_data.get('body', ''), height=300, key=f"li_body_{k_suffix}")
        
        edited_content = {"recipient": recipient, "body": body}
        
    elif task_type == 'cover_letter':
        cl_data = state_values.get('cover_letter', {})
        body = st.text_area("Cover Letter Content:", value=cl_data.get('body', ''), height=600, key=f"cl_body_{k_suffix}")
        
        edited_content = {"body": body}

    # Action Toolbar
    st.markdown("### 🛠️ Review & Actions")
    
    col_feedback, col_actions = st.columns([2, 1])
    
    with col_feedback:
        feedback = st.text_area("Feedback / Refine Instructions", placeholder="E.g., Make it more formal, emphasize my Python skills...", height=100, key=f"feedback_{k_suffix}")
        
    with col_actions:
        st.write("") # Spacer
        st.write("") # Spacer
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🔄 Refine", use_container_width=True):
                if feedback:
                    with st.spinner("Re-drafting based on feedback..."):
                        # Update state with feedback
                        app.update_state(config, {"feedback": feedback})
                        
                        # Resume execution
                        app.invoke(None, config=config)
                        
                        # Increment generation count to force UI refresh
                        st.session_state.gen_count += 1
                        st.rerun()
                else:
                    st.warning("Please enter feedback to refine.")
        
        with col_btn2:
            if task_type == ('email'):
                if st.button("📤 Send Email", type="primary", use_container_width=True):
                    with st.spinner("Sending..."):
                        # Use the EDITED content from the UI widgets
                        try:
                            # Update state with attachment info for record keeping
                            app.update_state(config, {"attachment_path": edited_content.get('attachment_path')})
                            
                            attachments_list = []
                            if edited_content.get('attachment_path') and os.path.exists(edited_content.get('attachment_path')):
                                attachments_list.append(edited_content.get('attachment_path'))

                            result = send_email.invoke({
                                "recipient": edited_content['recipient'],
                                "subject": edited_content['subject'],
                                "body": edited_content['body'],
                                "attachments": attachments_list
                            })
                            st.success(f"✅ {result}")
                            # Optionally notify graph to end
                            app.update_state(config, {"feedback": "send"})
                            app.invoke(None, config=config)
                        except Exception as e:
                            st.error(f"❌ Failed: {e}")
            else:
                if st.button("✅ Approve", type="primary", use_container_width=True):
                    # For non-email, just marking done
                    app.update_state(config, {"feedback": "send"})
                    app.invoke(None, config=config)
                    st.success("Draft approved and saved!")
