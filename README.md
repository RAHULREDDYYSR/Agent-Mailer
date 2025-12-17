# Agent Mailer: LangChain Deep Agent ✉️

Agent Mailer is a sophisticated **Deep Agent** built with **LangChain** and **LangGraph**, designed to automate and enhance your job application process. Unlike simple template generators, this agent employs a graph-based state machine to reason, plan, and execute complex workflows with **Human-in-the-Loop (HITL)** control.

## 🧠 Deep Agent Architecture

This project implements a "Deep Agent" architecture where the application logic is not just a linear script but a cognitive graph. The agent:
1.  **Perceives**: Analyzes Job Descriptions and your Resume (context retrieval).
2.  **Reasons**: Decides the best approach for the specific outreach type (Email vs. LinkedIn vs. Cover Letter).
3.  **Acts**: Generates high-quality drafts.
4.  **Collaborates**: Pauses for human review and refinement before finalizing or sending.

## 🚀 Key Features

-   **Human-in-the-Loop (HITL)**:
    -   **Interactive Refinement**: The agent doesn't just output text; it collaborates with you. You can review drafts, provide natural language feedback (e.g., "Make it more professional" or "Mention my leadership experience"), and the agent will **iterate** on its work.
    -   **Approval Workflows**: Critical actions like sending emails require your explicit approval, ensuring safety and control.

-   **Multi-Channel Outreach**:
    -   **Emails**: Professional, context-aware emails to hiring managers.
    -   **LinkedIn Messages**: Optimized for networking and direct messaging.
    -   **Cover Letters**: Comprehensive letters linking your CV details to the JD requirements.

-   **Context-Aware Intelligence**:
    -   **Resume Integration**: Automatically extracts and utilizes skills and experiences from your uploaded resume (`RAHUL_Y_S_CV.pdf`).
    -   **Job Description Analysis**: Tailors every message to the specific keywords and requirements of the target role.

-   **Tool Use**:
    -   **Web Search**: Capable of searching the web for company details to hyper-personalize the content.
    -   **Gmail Integration**: Can send emails directly via Gmail API upon your command.

## 🛠️ Tech Stack

-   **Orchestration**: [LangChain](https://www.langchain.com/) & [LangGraph](https://langchain-ai.github.io/langgraph/) (Stateful orchestration).
-   **Package Manager**: [uv](https://github.com/astral-sh/uv) (Fast Python package installer and resolver).
-   **UI**: [Gradio](https://www.gradio.app/) (Interactive Dashboard).
-   **LLMs**: Support for Google Gemini and OpenAI models.

## ⚙️ Setup & Installation

This project uses **uv** for modern, fast dependency management.

### Prerequisites

-   Python 3.10+
-   [uv](https://github.com/astral-sh/uv) installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`).

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    ```

3.  **Environment Setup**:
    Create a `.env` file in the root directory:
    ```env
    GOOGLE_API_KEY=your_google_api_key
    OPENAI_API_KEY=your_openai_api_key
    # Add other keys as needed
    ```

## 🖥️ Usage

Run the agent with `uv run`:

```bash
uv run app.py
```

### Dashboard Workflow
1.  **Launch**: Open the local URL (e.g., `http://127.0.0.1:7860`).
2.  **Input**: Paste a Job Description.
3.  **Collaborate**:
    -   Click **Generate**.
    -   Review the output in the "Draft Content" pane.
    -   provide feedback in the "Refine Instructions" box and hit **Refine Draft**.
4.  **Action**: Once satisfied, click **Send Email** to execute the final action.

## 📂 Project Structure

-   `graph/`: The brain of the agent. Contains `graph.py` (state machine), `nodes.py` (agent actions), and `chains.py` (LLM logic).
-   `utils/`: Tools for the agent (Gmail sender, Web Search).
-   `ui/`: Gradio frontend components.
-   `app.py`: Entry point for the application.
