# ✉️ Agent Mailer - Intelligent Deep Agent System

**Agent Mailer** is a sophisticated **Human-in-the-Loop (HITL)** AI application designed to automate professional outreach. Built on the **Deep Agent** architecture, it leverages **LangChain**, **LangGraph**, and **LangSmith** to generate, refine, and dispatch hyper-personalized Emails, LinkedIn Messages, and Cover Letters.

## ✨ What's New
- **User Context from Uploads**: Upload personal files (PDF, TXT, MD) to build a per-session cached user context used by agents to personalize drafts.
- **Attachments & SMTP Sending**: Attach files to outgoing emails and send directly via SMTP (configure `EMAIL_HOST` / `EMAIL_PORT` / `EMAIL_USER` / `EMAIL_PASSWORD`).
- **Split View Streamlit App**: Use `streamlit_app3.py` for a split-view UI that supports uploads, preview, refining via feedback, and sending emails directly from the interface.

## 🧠 Deep Agent Architecture

This system is not just a simple LLM wrapper; it is a **Multi-Agent System** guided by a cyclic state machine.

### Core Components
1.  **Deep Agents**: Specialized autonomous units responsible for specific tasks.
    -   `content_generator`: Performs deep analysis of the Job Description (JD) to build a "Context" layer.
    -   `drafters` (Email/LinkedIn/Cover Letter): Specialized agents that consume the Context and generate channel-specific drafts.
2.  **LangGraph State Machine**: Orchestrates the flow of information. It defines the "Brain" of the application, managing state transitions between generation, review, and feedback loops.
3.  **LangSmith Integration**:
    -   **Prompt Management**: All system prompts (e.g., `email_drafter_prompt`) are version-controlled and pulled dynamically from LangSmith (`context_generator:f92e9e5f`), ensuring easy updates without code changes.
    -   **Observability**: Traces every step of the agent's reasoning process.

## 🔄 Agentic Workflow

The application follows a generic cyclic graph structure. It uses **Conditionals** to route tasks and **Interrupts** for Human-in-the-Loop interaction.

```mermaid
graph TD
    Start([Start]) --> Generator[Context Generator]
    Generator --> Router{Draft Type?}
    
    Router -->|Email| EmailAgent[Email Drafter]
    Router -->|LinkedIn| LIAgent[LinkedIn Drafter]
    Router -->|Cover Letter| CLAgent[Cover Letter Drafter]
    
    EmailAgent --> Reviewer[Human Reviewer]
    LIAgent --> Reviewer
    CLAgent --> Reviewer
    
    Reviewer --> Check{Feedback?}
    
    Check -->|Request Changes| Router
    Check -->|Approved| End([End/Send])
    
    style Start fill:#f9f,stroke:#333
    style Reviewer fill:#bbf,stroke:#333
    style End fill:#9f9,stroke:#333
```

### Key Logic
1.  **Context Caching**: The system intelligently caches the `context` generated from the JD. Switching output types (e.g., Email -> LinkedIn) skips the expensive analysis step.
2.  **HITL Loop**: The process pauses at the `Reviewer` node. The user can provide natural language feedback (e.g., "Make it more formal"). The state carries this feedback back to the drafting agent, which "remembers" the previous attempt and acts to correct it.

## 🚀 Key Features

-   **Multi-Modal Output**: Supports Emails, LinkedIn Messages, and Cover Letters.
-   **Conversation-Driven UI**: Chat with your agent to refine drafts naturally.
-   **User Context from Uploads**: Upload PDFs / TXT / MD files (CVs, notes) to provide personal data that personalizes generated drafts.
-   **Attachments & Sending**: Attach files to outgoing emails; the app sends messages using a configurable SMTP tool (`EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USER`, `EMAIL_PASSWORD`). Attachments are transmitted along with the message.
-   **Split View App**: The split-view Streamlit app (`streamlit_app3.py`) supports uploading, previewing drafts, refining via feedback, and sending emails directly from the UI.

## 🛠️ Setup & Installation

### Prerequisites
-   Python 3.10+
-   [uv](https://github.com/astral-sh/uv) (Fast Python package manager)

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd draft_mail
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    ```

3.  **Environment Setup**:
    Create a `.env` file in the root directory:
    ```env
    OPENAI_API_KEY=sk-...
    LANGCHAIN_API_KEY=lsv2-...
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_PROJECT=Agent-Mailer

# SMTP (required for sending emails via the app)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465        # 465 for SSL, 587 for STARTTLS
Run the main Streamlit application (split view with uploads and send) using:

```bash
# If using uv (recommended)
uv run streamlit run streamlit_app3.py

# Or directly with streamlit
streamlit run streamlit_app3.py
```

### Workflow
1.  **Input**: Paste the Job Description in the sidebar.
2.  **Select**: Choose your output type (Email, LinkedIn, Cover Letter).
3.  **Collaborate**:
    -   **Review**: See the draft in the right-hand canvas.
    -   **Refine**: Tell the agent "Mention my Python experience" in the feedback box.
    -   **Edit**: Manually tweak the text if needed.
4.  **Action**: Click **Send Email** (for emails) or **Approve** (for others) to finish.

## 📂 Project Structure

```
Agent-Mailer/
├── app.py                      # Legacy Streamlit app (entry point variant)
├── main.py                     # Optional launcher / quick tests
├── streamlit_app.py            # Streamlit app variant
├── streamlit_app1.py           # Alternate streamlit examples
├── streamlit_app2.py
├── streamlit_app3.py           # Recommended split-view UI (uploads, preview, send)
├── langgraph.json              # LangGraph definition and configuration
├── README.md
├── pyproject.toml              # Project metadata & dependencies
├── demo/                       # Demo assets & visualizations
│   └── graph.png
├── graph/                      # Core agent logic & LangGraph implementation
│   ├── __init__.py
│   ├── graph.py                # LangGraph state machine and orchestration
│   ├── nodes.py                # Node handler functions and tool calls
│   ├── chains.py               # LLM chains / agent configurations
│   ├── state.py                # Typed state and schemas for the graph
│   └── schemas.py              # Pydantic output schemas
├── utils/                      # Helper utilities and tools
│   ├── __init__.py
│   ├── context_builder.py      # Build per-session user context from uploads
│   ├── file_parser.py          # Parse PDF, TXT, MD files (extend for DOCX)
│   ├── email_sender_tool.py    # SMTP email sending with attachment support
│   └── web_search_tool.py      # Web search helper (used by agents)
└── user_data/                  # Runtime-created per-session user context files
    └── <session-id>/user_context.txt
```

## ⚠️ Notes & Known Issues

## ⚠️ Notes & Known Issues

- **Supported upload types**: PDF, TXT, and MD are parsed by `utils/file_parser.py`. The UI currently allows `docx` uploads but `docx` parsing is not implemented yet and will raise an error — consider converting `.docx` files to PDF or TXT for now, or ask to add `python-docx` support.
- **Default CV path**: The app uses a fallback `default_cv_path` that is currently hard-coded in `streamlit_app3.py` to an absolute Windows path. It's recommended to upload attachments explicitly or change the code to point to your local CV.
- **Email sending**: Ensure `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USER`, and `EMAIL_PASSWORD` are set in `.env`. For Gmail accounts with 2FA enable an App Password.

## 🔧 Testing the email tool

You can test SMTP by running:

```bash
python utils/email_sender_tool.py
```

after setting the required env variables — the script will attempt to send a test email if `EMAIL_USER` is set.
