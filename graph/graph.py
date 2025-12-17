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
    email_reviewer,
    email_publisher
)

graph = StateGraph(GraphState)
graph.add_node('content_generator', content_generator)
graph.add_node('email_drafter_agent', email_drafter_agent)
graph.add_node('email_reviewer', email_reviewer)
graph.add_node('email_publisher', email_publisher)
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

graph.add_edge('email_drafter_agent', 'email_reviewer')

def check_review(state):
    feedback = state.get('feedback', '').strip().lower()
    if feedback == 'send':
        return 'email_publisher'
    return 'email_drafter_agent'

graph.add_conditional_edges(
    'email_reviewer',
    check_review,
    {
        'email_publisher': 'email_publisher',
        'email_drafter_agent': 'email_drafter_agent'
    }
)

graph.add_edge('email_publisher', END)
graph.add_edge('linkedin_message_agent', END)
graph.add_edge('cover_letter_agent', END)


from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = graph.compile(checkpointer=memory, interrupt_before=['email_reviewer'])
