import streamlit as st
import uuid
import os
from dotenv import load_dotenv

from graph.graph import app
from utils.email_sender_tool import send_email
from utils.file_parser import parse_file
from utils.context_builder import build_user_context
from utils.pdf_generator import create_pdf

# --------------------------------------------------
# ENV SETUP
# --------------------------------------------------
load_dotenv()

st.set_page_config(
    page_title="Agent Mailer",
    page_icon="✉️",
    layout="wide"
)

# --------------------------------------------------
# GLOBAL STYLES
# --------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

h1, h2, h3 {
    font-weight: 600;
    letter-spacing: -0.02em;
}

.stButton button {
    border-radius: 6px;
    font-weight: 600;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "generated" not in st.session_state:
    st.session_state.generated = False

if "gen_count" not in st.session_state:
    st.session_state.gen_count = 0

if "user_context" not in st.session_state:
    st.session_state.user_context = None


def get_config():
    return {"configurable": {"thread_id": st.session_state.thread_id}}


def reset_session():
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.generated = False
    st.session_state.gen_count = 0
    st.session_state.user_context = None
    st.rerun()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.title("⚙️ User Context")

    uploaded_files = st.file_uploader(
        "Upload your personal files (Resume, Projects, Notes)",
        type=["pdf", "txt", "md", "docx"],
        accept_multiple_files=True
    )

    if uploaded_files:
        with st.spinner("📂 Processing personal files..."):
            user_id = st.session_state.thread_id
            base_dir = f"user_data/{user_id}"
            raw_dir = os.path.join(base_dir, "raw_uploads")
            os.makedirs(raw_dir, exist_ok=True)

            parsed_texts = []

            for file in uploaded_files:
                file_path = os.path.join(raw_dir, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())

                parsed_texts.append(parse_file(file_path))

            context_path = build_user_context(user_id, parsed_texts)

            with open(context_path, "r", encoding="utf-8") as f:
                st.session_state.user_context = f.read()

            st.success("✅ User context created & cached")

    st.markdown("---")

    if st.button("🗑️ Reset Session", use_container_width=True):
        reset_session()

    st.info(
        "Agent Mailer uses a Human-in-the-Loop LangGraph workflow. "
        "User files are parsed once and reused across generations."
    )

# --------------------------------------------------
# MAIN HEADER
# --------------------------------------------------
st.title("✉️ Agent Mailer")
st.caption("AI-powered job application drafting & outreach assistant")

st.divider()

# --------------------------------------------------
# INPUT SECTION
# --------------------------------------------------
col_left, col_right = st.columns([2, 1])

with col_left:
    job_description = st.text_area(
        "📋 Job Description",
        height=220,
        placeholder="Paste the full job description here..."
    )

with col_right:
    st.markdown("### 🎯 Output Type")
    output_type = st.radio(
        "Select draft type",
        ["Email", "LinkedIn Message", "Cover Letter"],
        horizontal=False
    )

    generate_btn = st.button("🚀 Generate Draft", type="primary", use_container_width=True)

# --------------------------------------------------
# GENERATION LOGIC
# --------------------------------------------------
if generate_btn:
    if not job_description:
        st.warning("Please provide a job description.")
    elif not st.session_state.user_context:
        st.warning("Please upload personal files to build user context.")
    else:
        with st.spinner("🤖 Generating draft..."):
            type_map = {
                "Email": "email",
                "LinkedIn Message": "linkedin_message",
                "Cover Letter": "cover_letter"
            }

            initial_state = {
                "job_description": job_description,
                "type": type_map[output_type],
                "user_context": st.session_state.user_context
            }

            app.invoke(initial_state, config=get_config())

            st.session_state.generated = True
            st.session_state.gen_count += 1
            st.rerun()

# --------------------------------------------------
# OUTPUT SECTION
# --------------------------------------------------
config = get_config()
state = app.get_state(config)

if not st.session_state.generated or not state.values:
    st.info("Generated draft will appear here.")
else:
    values = state.values
    task_type = values.get("type")
    k = st.session_state.gen_count

    st.divider()
    st.subheader("📝 Draft Workspace")

    tabs = st.tabs(["✏️ Edit Draft", "🔄 Refine", "🚀 Actions"])

    # ---------------- EDIT TAB ----------------
    with tabs[0]:
        if task_type == "email":
            data = values.get("email", {})
            to = st.text_input("To", data.get("recipient", ""), key=f"to_{k}")
            subject = st.text_input("Subject", data.get("subject", ""), key=f"sub_{k}")
            body = st.text_area("Body", data.get("body", ""), height=420, key=f"body_{k}")

            edited = {
                "recipient": to,
                "subject": subject,
                "body": body
            }

        elif task_type == "linkedin_message":
            data = values.get("linkedin_message", {})
            to = st.text_input("LinkedIn Profile", data.get("recipient", ""), key=f"li_{k}")
            body = st.text_area("Message", data.get("body", ""), height=350, key=f"li_body_{k}")

            edited = {"recipient": to, "body": body}

        else:
            data = values.get("cover_letter", {})
            body = st.text_area("Cover Letter", data.get("body", ""), height=520, key=f"cl_{k}")
            
            # --- PDF Download ---
            pdf_bytes = create_pdf(body)
            st.download_button(
                label="📄 Download as PDF",
                data=pdf_bytes,
                file_name="cover_letter.pdf",
                mime="application/pdf",
                key=f"dl_{k}"
            )
            
            edited = {"body": body}

    # ---------------- REFINE TAB ----------------
    with tabs[1]:
        feedback = st.text_area(
            "Refinement Instructions",
            placeholder="Make it more concise, highlight GenAI work, adjust tone...",
            height=160
        )

        if st.button("🔄 Apply Refinement"):
            if feedback:
                with st.spinner("Refining draft..."):
                    app.update_state(config, {"feedback": feedback})
                    app.invoke(None, config=config)
                    st.session_state.gen_count += 1
                    st.rerun()
            else:
                st.warning("Enter refinement instructions.")

    # ---------------- ACTIONS TAB ----------------
    with tabs[2]:
        if task_type == "email":
            if st.button("📤 Send Email", type="primary", use_container_width=True):
                with st.spinner("Sending email..."):
                    send_email.invoke({
                        "recipient": edited["recipient"],
                        "subject": edited["subject"],
                        "body": edited["body"],
                        "attachments": []
                    })
                    app.update_state(config, {"feedback": "send"})
                    app.invoke(None, config=config)
                    st.success("Email sent successfully ✅")
        else:
            if st.button("✅ Approve & Finish", type="primary", use_container_width=True):
                app.update_state(config, {"feedback": "send"})
                app.invoke(None, config=config)
                st.success("Draft approved 🎉")
