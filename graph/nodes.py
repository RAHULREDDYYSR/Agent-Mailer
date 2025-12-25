from .state import GraphState
from .chains import email_llm, linkedin_message_llm, cover_letter_llm, agent
from langchain_core.messages import SystemMessage, HumanMessage
from langsmith import Client

from dotenv import load_dotenv
load_dotenv()
client = Client()
try:
    from langgraph.types import interrupt
except ImportError:
    # Fallback or mock for older versions if needed, though dependency says >=1.0
    def interrupt(value):
        return input(f"Interrupt: {value}\n> ")

def content_generator(state: GraphState) -> GraphState:
    '''Generates the content for the email, linkedin message or cover letter'''
    
    current_jd = state.get('job_description', '').strip()
    cached_jd = state.get('context_job_description', '').strip()
    user_context = state.get('user_context', '').strip()
    
    # Check if we can reuse the context
    if state.get('context') and current_jd == cached_jd and current_jd:
        print("Using cached context (Job Description unchanged)")
        return state

    print("Generating new context...")
    prompt = client.pull_prompt("context_generator:89c5d81e")
    messages = prompt.invoke({'job_description': state['job_description'], 'user_context': user_context}).to_messages()
    response = agent.invoke({'messages': messages})
    state['context'] = response['messages'][-1].content
    
    # Cache the JD used for this context
    state['context_job_description'] = current_jd
    return state



def email_drafter_agent(state: GraphState) -> GraphState:
    """Drafts an email to the HR/Recruiter based on the generated context."""
    prompt = client.pull_prompt("email_drafter_prompt")
    messages = prompt.invoke({'context': state['context']}).to_messages()
    # Handle feedback loop
    if state.get('feedback') and state.get('email'):
         feedback_msg = f"Previous draft was rejected. Feedback: {state['feedback']}. \n\n Previous Draft: {state.get('email')}"
         messages.append(HumanMessage(content=feedback_msg))
    response = email_llm.invoke(messages)
    # send_email.invoke removed. Only drafting now.
    state['email'] = response.model_dump()
    return state



def reviewer(state: GraphState) -> GraphState:
    """Takes user input to review the draft. This node is interrupted by the graph."""
    # The interruption happens BEFORE this node via interrupt_before
    # The UI will update the state with feedback before resuming
    # This node just passes through since feedback is set by UI
    return state




def linkedin_message_agent(state: GraphState) -> GraphState:
    """Sends a LinkedIn message to the HR/Recruiter based on the generated context."""
    prompt = client.pull_prompt("linkedin_message_prompt")
    messages = prompt.invoke({'context': state['context']}).to_messages()
    
    if state.get('feedback') and state.get('linkedin_message'):
         feedback_msg = f"Previous draft was rejected. Feedback: {state['feedback']}. \n\n Previous Draft: {state.get('linkedin_message')}"
         messages.append(HumanMessage(content=feedback_msg))
         
    response = linkedin_message_llm.invoke(messages)
    state['linkedin_message'] = response.model_dump()
    return state


    
def cover_letter_agent(state: GraphState) -> GraphState:
    """generate cover letter """
    prompt = client.pull_prompt("cover_letter_prompt")
    messages = prompt.invoke({'context': state['context']}).to_messages()
    
    if state.get('feedback') and state.get('cover_letter'):
         feedback_msg = f"Previous draft was rejected. Feedback: {state['feedback']}. \n\n Previous Draft: {state.get('cover_letter')}"
         messages.append(HumanMessage(content=feedback_msg))
         
    response = cover_letter_llm.invoke(messages)
    state['cover_letter'] = response.model_dump()
    return state
