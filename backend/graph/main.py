from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END, START

from typing import Literal
from .state import GenerateState, DraftState, GitHubScrapeState
from .nodes import (
    content_generator,
    email_drafter_agent,
    linkedin_message_agent,
    cover_letter_agent,
    github_context_builder,
)

# ── Generate Graph ────────────────────────────────────────────────────────────
# Flow: content_generator only.
# GitHub README summaries are already stored in user_context by the background
# task that ran at registration — no need to re-summarise on every call.
generate_graph = StateGraph(GenerateState)
generate_graph.add_node('content_generator', content_generator)
generate_graph.add_edge(START, 'content_generator')
generate_graph.add_edge('content_generator', END)


# ── Draft Graph ───────────────────────────────────────────────────────────────
draft_graph = StateGraph(DraftState)
draft_graph.add_node('email_drafter_agent', email_drafter_agent)
draft_graph.add_node('linkedin_message_agent', linkedin_message_agent)
draft_graph.add_node('cover_letter_agent', cover_letter_agent)


def route_start(state):
    if state.get('type'):
        return state['type']
    return END

draft_graph.add_conditional_edges(
    START,
    route_start,
    {
        'email': 'email_drafter_agent',
        'linkedin_message': 'linkedin_message_agent',
        'cover_letter': 'cover_letter_agent',
        END: END
    }
)


# ── GitHub Scrape Graph (standalone) ─────────────────────────────────────────
# Used by POST /generation/scrape_github to build & persist github_context.
github_scrape_graph = StateGraph(GitHubScrapeState)
github_scrape_graph.add_node('github_context_builder', github_context_builder)
github_scrape_graph.add_edge(START, 'github_context_builder')
github_scrape_graph.add_edge('github_context_builder', END)


generate_graph = generate_graph.compile()
draft_graph = draft_graph.compile()
github_scrape_graph = github_scrape_graph.compile()
