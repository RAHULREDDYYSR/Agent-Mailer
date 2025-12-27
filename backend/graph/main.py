from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END, START

from typing import Literal
from .state import GenerateState, DraftState
from .nodes import (
    content_generator,
    email_drafter_agent,
    linkedin_message_agent,
    cover_letter_agent
)

generate_graph = StateGraph(GenerateState)
generate_graph.add_node('content_generator', content_generator)
generate_graph.add_edge(START, 'content_generator')
generate_graph.add_edge('content_generator', END)


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





generate_graph = generate_graph.compile()
draft_graph = draft_graph.compile()


