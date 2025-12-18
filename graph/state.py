from typing import TypedDict, List, Optional, Dict, Literal

class GraphState(TypedDict):
    '''Defines the state of the graph'''
    job_description: str
    context: str
    type: Literal['email', 'cover_letter','linkedin_message']
    email: dict
    linkedin_message: dict
    cover_letter: dict
    feedback: str
    attachment_path: Optional[str]
    context_job_description: Optional[str]
