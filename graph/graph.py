from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END

from typing import Literal
from .state import GraphState
from .nodes import (
    content_generator,
    email_drafter_agent,
    linkedin_message_agent,
    cover_letter_agent,
    reviewer
)

graph = StateGraph(GraphState)
graph.add_node('content_generator', content_generator)
graph.add_node('email_drafter_agent', email_drafter_agent)
graph.add_node('reviewer', reviewer)
graph.add_node('linkedin_message_agent', linkedin_message_agent)
graph.add_node('cover_letter_agent', cover_letter_agent)

graph.set_entry_point('content_generator')

# Route directly from content_generator based on type
graph.add_conditional_edges(
    'content_generator',
    lambda state: state['type'],
    {
        'email': 'email_drafter_agent',
        'linkedin_message': 'linkedin_message_agent',
        'cover_letter': 'cover_letter_agent'
    }
)

graph.add_edge('email_drafter_agent', 'reviewer')
graph.add_edge('linkedin_message_agent', 'reviewer')
graph.add_edge('cover_letter_agent', 'reviewer')


def check_review(state):
    feedback = state.get('feedback', '').strip().lower()
    if feedback == 'send':
        return END
    
    # Retry logic based on type
    t = state['type']
    if t == 'email':
        return 'email_drafter_agent'
    elif t == 'linkedin_message':
        return 'linkedin_message_agent'
    elif t == 'cover_letter':
        return 'cover_letter_agent'
    return END

graph.add_conditional_edges(
    'reviewer',
    check_review,
    {
        'email_drafter_agent': 'email_drafter_agent',
        'linkedin_message_agent': 'linkedin_message_agent',
        'cover_letter_agent': 'cover_letter_agent',
        END: END
    }
)


from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = graph.compile(checkpointer=memory, interrupt_before=['reviewer'])

