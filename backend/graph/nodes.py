from .state import GenerateState, DraftState, GitHubScrapeState
from .chains import email_llm, linkedin_message_llm, cover_letter_llm, agent, llm
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langsmith import Client
from backend.utils.github_scraper import fetch_repo_readmes
import logging

from dotenv import load_dotenv
load_dotenv()
client = Client()
logger = logging.getLogger(__name__)

# ── System prompt for the README summariser ──────────────────────────────────
GITHUB_README_SUMMARIZER_PROMPT = """\
You are an expert technical recruiter assistant and career advisor.
Your job is to analyse a GitHub repository README and extract ONLY the
information that is useful for crafting personalised job outreach —
cold emails, LinkedIn messages, and cover letters.

You will receive:
- Repository name
- Repository description (if any)
- README content

Output a CONCISE, structured summary using EXACTLY this format
(omit a section entirely if no relevant info is found):

### Project: {repo_name}
**What it does** (1-2 sentences):
<plain-English purpose — what problem does it solve?>

**Tech Stack**:
<comma-separated key languages, frameworks, tools — skip boilerplate like npm/git/pip>

**Key Highlights** (max 3 bullets):
- <metric, scale, impressive technical decision, or production signal>

**Relevance Signal**:
<one sentence: what job roles would this impress?>

Strict rules:
- Be EXTREMELY concise. Each section ≤ 3 lines.
- IGNORE: installation steps, contributing guides, license text, folder
  structure, CI/CD badges (unless they reveal something impressive).
- If the README is empty or only contains boilerplate setup instructions,
  output exactly: SKIP
- Never hallucinate. Only use facts present in the README.
- Output ONLY the structured summary — no preamble, no explanation.
"""

def content_generator(state: GenerateState) -> GenerateState:
    '''Generates the content for the email, linkedin message or cover letter'''
    
    current_jd = state.get('job_description', '').strip()

    user_context = state.get('user_context', '').strip()

    print("Generating context...")
    prompt_name = "context_generator:40940ed8"
    prompt = client.pull_prompt(prompt_name)
    messages = prompt.invoke({'job_description': state['job_description'], 'user_context': user_context}).to_messages()
    response = agent.invoke({'messages': messages})
    state['context'] = response['messages'][-1].content
    
    # Capture metadata
    state['model_used'] = llm.model_name
    state['prompt_version'] = prompt_name
    return state


async def github_context_builder(state: GitHubScrapeState) -> GitHubScrapeState:
    """
    Standalone node for the scrape-only graph (used by the /scrape_github endpoint).

    Fetches + summarises READMEs and stores the result in `github_context`
    so the caller can persist it to the user's profile.
    """
    github_url = state.get("github_url", "").strip()
    if not github_url:
        state["github_context"] = ""
        return state

    try:
        repos = await fetch_repo_readmes(github_url)
    except Exception as exc:
        logger.error("github_context_builder — fetch failed: %s", exc)
        state["github_context"] = ""
        return state

    summaries: list[str] = []
    for repo in repos:
        prompt = GITHUB_README_SUMMARIZER_PROMPT.format(repo_name=repo["repo_name"])
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(
                content=(
                    f"Repository: {repo['repo_name']}\n"
                    f"Description: {repo['description']}\n"
                    f"Stars: {repo['stars']} | Language: {repo.get('language', 'N/A')}\n"
                    f"URL: {repo['repo_url']}\n\n"
                    f"README:\n{repo['readme_text']}"
                )
            ),
        ]
        try:
            response = llm.invoke(messages)
            summary_text = response.content.strip()
            if summary_text.upper() != "SKIP":
                summaries.append(summary_text)
        except Exception as exc:
            logger.warning("LLM summarisation failed for %s: %s", repo["repo_name"], exc)
            continue

    state["github_context"] = (
        "## GitHub Projects (auto-summarised)\n\n" + "\n\n---\n\n".join(summaries)
        if summaries
        else ""
    )
    return state



def email_drafter_agent(state: DraftState) -> DraftState:
    """Drafts an email to the HR/Recruiter based on the generated context."""
    prompt_name = "email_draft_prompt"
    prompt = client.pull_prompt(prompt_name)
    messages = prompt.invoke({'context': state['context'], 'user_details': state['user_details']}).to_messages()
    if state.get('feedback'):
        messages.append(HumanMessage(content=state['feedback']))
    
    response = email_llm.invoke(messages)
    state['email'] = response.model_dump()
    # Capture metadata
    state['model_used'] = llm.model_name
    state['prompt_version'] = prompt_name
    return state






def linkedin_message_agent(state: DraftState) -> DraftState:
    """Sends a LinkedIn message to the HR/Recruiter based on the generated context."""
    prompt_name = "linkedin_message_prompt"
    prompt = client.pull_prompt(prompt_name)
    messages = prompt.invoke({'context': state['context']}).to_messages()
    if state.get('feedback'):
        messages.append(HumanMessage(content=state['feedback']))
    
      
    response = linkedin_message_llm.invoke(messages)
    state['linkedin_message'] = response.model_dump()
    # Capture metadata
    state['model_used'] = llm.model_name
    state['prompt_version'] = prompt_name
    return state


    
def cover_letter_agent(state: DraftState) -> DraftState:
    """generate cover letter """
    prompt_name = "cover_letter_prompt"
    prompt = client.pull_prompt(prompt_name)
    messages = prompt.invoke({'context': state['context']}).to_messages()
    if state.get('feedback'):
        messages.append(HumanMessage(content=state['feedback']))
    response = cover_letter_llm.invoke(messages)
    state['cover_letter'] = response.model_dump()
    # Capture metadata
    state['model_used'] = llm.model_name
    state['prompt_version'] = prompt_name
    return state
