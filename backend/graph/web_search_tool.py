from tavily import TavilyClient
from typing import Literal
from dotenv import load_dotenv
load_dotenv()

tavily_client = TavilyClient()

def internet_search(
    query: str
):
    """Run a web search"""
    return tavily_client.extract(
        urls=[query],
        extract_depth='advanced'
        
    )


if __name__ == "__main__":
    result = internet_search(query="https://www.accenture.com/in-en/careers/jobdetails?id=R00268097_en&title=S%26C+Global+Network+-+AI+-+CMT+Engineering+-Associate?")
    print(result['results'])