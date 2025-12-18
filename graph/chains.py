from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from .schemas import EmailSchema, LinkedInMessageSchema, CoverLetterSchema
from utils.web_search_tool import internet_search



llm = ChatOpenAI(model_name="gpt-4.1-nano-2025-04-14")

agent = create_deep_agent(
    tools=[internet_search],
    model=llm,
    backend=FilesystemBackend(root_dir="./agent-data", virtual_mode=True)
)

email_llm = llm.with_structured_output(EmailSchema)
linkedin_message_llm = llm.with_structured_output(LinkedInMessageSchema)
cover_letter_llm = llm.with_structured_output(CoverLetterSchema)