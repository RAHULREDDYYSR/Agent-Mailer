from tavily import TavilyClient
from typing import Literal
from dotenv import load_dotenv
load_dotenv()

tavily_client = TavilyClient()

def internet_search(
    query: str,
    max_results: int = 3,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_answer='advanced',
        topic=topic
    )


if __name__ == "__main__":
    result = internet_search(query="What is the capital of France?")
    print(result['answer'])