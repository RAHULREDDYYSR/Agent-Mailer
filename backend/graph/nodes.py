from .state import GenerateState, DraftState
from .chains import email_llm, linkedin_message_llm, cover_letter_llm, agent, llm
from langchain_core.messages import SystemMessage, HumanMessage
from langsmith import Client

from dotenv import load_dotenv
load_dotenv()
client = Client()

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



def email_drafter_agent(state: DraftState) -> DraftState:
    """Drafts an email to the HR/Recruiter based on the generated context."""
    prompt_name = "email_drafter_prompt"
    prompt = client.pull_prompt(prompt_name)
    messages = prompt.invoke({'context': state['context']}).to_messages()
    
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
    response = cover_letter_llm.invoke(messages)
    state['cover_letter'] = response.model_dump()
    return state
