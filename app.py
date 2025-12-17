import gradio as gr
import uuid
from graph.graph import app as graph_app
from ui.components import CUSTOM_CSS, get_theme
from langgraph.types import Command

# --- State Management ---
def get_initial_session():
    return {
        "thread_id": str(uuid.uuid4()),
        "draft_body": "",
        "draft_metadata": {} 
    }

def get_config(session):
    return {"configurable": {"thread_id": session["thread_id"]}}

# --- Business Logic ---

def update_visibility(outreach_type):
    """Updates the visibility of settings fields based on type."""
    # Returns (recipient_row_update, subject_row_update)
    if outreach_type == "email":
        return gr.update(visible=True), gr.update(visible=True)
    elif outreach_type == "linkedin_message":
        return gr.update(visible=True), gr.update(visible=True) # Usually keeps subject/recipient for LI too, or maybe just recipient
    elif outreach_type == "cover_letter":
        # Cover letters usually don't have explicit Subject headers in the same way, 
        # but often have recipient blocks. For simplicity, let's hide subject.
        return gr.update(visible=False), gr.update(visible=False)
    return gr.update(visible=True), gr.update(visible=True)

def generate_draft(job_desc, outreach_type, session):
    if not job_desc.strip():
        raise gr.Error("Please enter a Job Description.")
    
    config = get_config(session)
    initial_state = {
        "job_description": job_desc,
        "type": outreach_type,
        "feedback": "",
        "email": {},
        "linkedin_message": {},
        "cover_letter": {},
        "attachment_path": None
    }
    
    # Stream Graph
    events = []
    try:
        for event in graph_app.stream(initial_state, config, stream_mode="values"):
            events.append(event)
    except Exception as e:
        raise gr.Error(f"Generation failed: {str(e)}")
        
    final_state = events[-1] if events else {}
    
    # Extract Content
    recipient = ""
    subject = ""
    body = ""
    
    if outreach_type == "email" and final_state.get('email'):
        data = final_state['email']
        recipient = data.get('recipient', '')
        subject = data.get('subject', '')
        body = data.get('body', '')
    elif outreach_type == "linkedin_message" and final_state.get('linkedin_message'):
        data = final_state['linkedin_message']
        recipient = data.get('recipient', '')
        subject = data.get('subject', '')
        body = data.get('body', '')
    elif outreach_type == "cover_letter" and final_state.get('cover_letter'):
        data = final_state['cover_letter']
        body = data.get('body', '')

    session["draft_body"] = body
    session["draft_metadata"] = {"recipient": recipient, "subject": subject}
    
    # Return updates for UI: (recipient_val, subject_val, body_val, status_msg, session)
    return recipient, subject, body, f"Draft generated for {outreach_type}!", session

def refine_draft(prompt, file_obj, current_body, current_recipient, current_subject, session):
    if not prompt and not file_obj:
        return current_body, "No feedback provided."
        
    config = get_config(session)
    
    # Update State with CURRENT UI values to preserve manual edits
    current_state = {
        "email": {
            "recipient": current_recipient,
            "subject": current_subject,
            "body": current_body 
        },
        "feedback": prompt
    }
    
    if file_obj:
        current_state["attachment_path"] = file_obj.name

    graph_app.update_state(config, current_state)
    
    try:
        events = list(graph_app.stream(Command(resume=prompt), config, stream_mode="values"))
        final_state = events[-1] if events else {}
        
        new_body = ""
        if final_state.get('email'):
             new_body = final_state['email'].get('body')
        
        session["draft_body"] = new_body
        return new_body, "Draft refined!"
        
    except Exception as e:
        return current_body, f"Error: {str(e)}"

def send_email(current_body, current_recipient, current_subject, file_obj, session):
    config = get_config(session)
    
    current_state = {
        "email": {
            "recipient": current_recipient,
            "subject": current_subject,
            "body": current_body
        },
        "feedback": "send"
    }

    if file_obj:
        current_state["attachment_path"] = file_obj.name
    
    graph_app.update_state(config, current_state)
    
    try:
        list(graph_app.stream(Command(resume="send"), config, stream_mode="values"))
        return "✅ Email Sent Successfully!"
    except Exception as e:
        return f"❌ Send failed: {str(e)}"


# --- UI Layout ---

with gr.Blocks(title="Agent Mailer", css=CUSTOM_CSS) as demo:
    
    session_state = gr.State(value=get_initial_session())
    
    with gr.Column(elem_classes=["main-header"]):
        gr.Markdown("# ✉️ Agent Mailer")
        gr.Markdown("Dashboard Mode")
    
    # 1. Inputs
    with gr.Row():
        with gr.Column(scale=2):
            job_desc_input = gr.Textbox(label="Job Description", lines=4, placeholder="Paste JD here...")
        with gr.Column(scale=1):
            type_input = gr.Radio(
                ["email", "cover_letter", "linkedin_message"], 
                label="Outreach Type", 
                value="email"
            )
            generate_btn = gr.Button("✨ Generate Draft", variant="primary", size="lg")
            
    gr.Markdown("---")
    
    # 2. Main Dashboard (Settings + Content)
    with gr.Row():
        # LEFT: Metadata Settings
        with gr.Column(scale=1):
            gr.Markdown("### Settings")
            
            # These rows toggle visibility
            with gr.Group() as meta_group:
                with gr.Row() as rec_row:
                    recipient_input = gr.Textbox(label="Recipient", placeholder="e.g. Hiring Manager")
                with gr.Row() as sub_row:
                    subject_input = gr.Textbox(label="Subject Line", placeholder="e.g. Application for...")
                    
            status_box = gr.Textbox(label="Status", interactive=False)

        # RIGHT: Draft Content
        with gr.Column(scale=2):
            gr.Markdown("### Draft Content")
            body_input = gr.Textbox(
                label="Message Body (Editable)", 
                lines=20, 
                interactive=True
            )

    # 3. Actions / Footer
    with gr.Row():
        with gr.Column(scale=4):
            refine_input = gr.Textbox(
                label="Refine Instructions", 
                placeholder="Type instructions to refine the draft (e.g. 'Make it shorter')..."
            )
            file_input = gr.File(label="Attach File (for Context)")
        with gr.Column(scale=1):
            refine_btn = gr.Button("Refine Draft", variant="secondary")
            send_btn = gr.Button("🚀 Send Email", variant="primary")

    # --- Event Wiring ---
    
    # Visibility Toggle
    type_input.change(
        update_visibility,
        inputs=[type_input],
        outputs=[rec_row, sub_row]
    )
    
    # Generation
    generate_btn.click(
        generate_draft,
        inputs=[job_desc_input, type_input, session_state],
        outputs=[recipient_input, subject_input, body_input, status_box, session_state]
    )
    
    # Refinement
    refine_btn.click(
        refine_draft,
        inputs=[refine_input, file_input, body_input, recipient_input, subject_input, session_state],
        outputs=[body_input, status_box]
    )
    
    # Send
    send_btn.click(
        send_email,
        inputs=[body_input, recipient_input, subject_input, file_input, session_state],
        outputs=[status_box]
    )

demo.launch(theme=get_theme(), css=CUSTOM_CSS)
