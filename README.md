# ✉️ Agent Mailer

> **Intelligent Deep Agent System for Automated Professional Outreach**

![Python](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker&logoColor=white)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/Powered%20by-LangChain-1C3C3C?logo=langchain&logoColor=white)
![UV](https://img.shields.io/badge/Package%20Manager-uv-de5fe9?logo=python&logoColor=white)

---

## 📖 About

**Agent Mailer** is a sophisticated **Human-in-the-Loop (HITL)** AI application designed to automate professional outreach. Built on the **Deep Agent** architecture, it leverages **LangChain**, **LangGraph**, and **LangSmith** to generate, refine, and dispatch hyper-personalized Emails, LinkedIn Messages, and Cover Letters.

Unlike simple LLM wrappers, this system acts as a **Multi-Agent System** where specialized agents work together to analyze job descriptions, generate content, and refine drafts based on your feedback.

## ✨ Key Features

- **🤖 Autonomous Agents**: Specialized agents for content generation (Email, LinkedIn, Cover Letter).
- **🧠 Context Awareness**: Analyzes Job Descriptions (JD) deeply to create a reusable context layer.
- **📂 User Context Support**: Upload your own files (PDF, TXT, MD) to personalize drafts with your resume or notes.
- **🔄 Human-in-the-Loop**: Review, refine, and edit drafts before they are finalized.
- **📧 Built-in Sending**: Send emails directly via SMTP with attachment support.
- **🖥️ Modern UI**: Split-view Streamlit interface for easy drafting and previewing.
- **🐳 Docker Ready**: Fully containerized for easy deployment.

---

## 🏗️ Architecture

The application follows a cyclic graph structure, orchestrated by **LangGraph**.

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

### Core Components

1.  **Backend (FastAPI)**: Handles the agent logic, database interactions, and state management.
2.  **Frontend (Streamlit)**: Provides the interactive user interface.
3.  **LangSmith**: Used for tracing and prompt management.

---

## 🚀 Getting Started

### Prerequisites

- **Docker** & **Docker Compose** (Recommended)
- *Or* **Python 3.13+** and [**uv**](https://github.com/astral-sh/uv) (for local development)

### Option 1: Run with Docker 🐳 (Recommended)

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/RAHULREDDYYSR/Agent-Mailer.git
    cd Agent-Mailer
    ```

2.  **Configure Environment**:
    Create a `.env` file in the root directory (see [Configuration](#-configuration) below).

3.  **Start the Application**:
    ```bash
    docker-compose up --build
    ```

4.  **Access the App**:
    - **Frontend**: [http://localhost:8501](http://localhost:8501)
    - **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Option 2: Local Development with `uv` 🐍

1.  **Install dependencies**:
    ```bash
    uv sync
    ```

2.  **Start Backend**:
    ```bash
    uv run uvicorn backend.main:app --reload
    ```

3.  **Start Frontend**:
    ```bash
    uv run streamlit run frontend/app.py
    ```

---

## ⚙️ Configuration

Create a `.env` file in the root directory with the following keys:

```env
# AI Providers
OPENAI_API_KEY=sk-...
LANGCHAIN_API_KEY=lsv2-...

# LangSmith (Optional but Recommended)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=Agent-Mailer

# SMTP Settings (For sending emails)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465        # 465 for SSL, 587 for STARTTLS
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

---

## 📂 Project Structure

```text
Agent-Mailer/
├── backend/                # FastAPI Backend Application
│   ├── main.py             # Entry point
│   ├── core/               # Config & Database
│   ├── models/             # Database Models
│   ├── routers/            # API Endpoints
│   └── utils/              # Backend Utilities
├── frontend/               # Streamlit Frontend Application
│   ├── app.py              # Main UI Entry point
│   └── ...
├── graph/                  # LangGraph Agent Logic
├── Dockerfile              # Container definition
├── docker-compose.yml      # Service orchestration
├── pyproject.toml          # Dependencies (uv)
└── README.md               # Documentation
```

## 🛠️ Tech Stack

-   **Language**: Python 3.13
-   **Orchestration**: LangGraph
-   **Frameworks**: FastAPI, Streamlit
-   **Database**: PostgreSQL / SQLite (via SQLAlchemy)
-   **Package Manager**: uv
-   **Containerization**: Docker

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
