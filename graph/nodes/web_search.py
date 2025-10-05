from typing import Any, Dict
import sys
from pathlib import Path

from langchain.schema import Document
from langchain_tavily import TavilySearch

if __name__ == "__main__":
    # Get the project root (3 levels up from this file)
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
try:
    from ..state import GraphState  # Relative import (when run as module)
except ImportError:
    from graph.state import GraphState  # Absolute import (when run directly)

from dotenv import load_dotenv

load_dotenv()

web_search_tool = TavilySearch(max_results=3)

def web_search(state: GraphState) -> Dict[str, Any]:
    """
    Performs a web search for the question
    """
    """
    Perform a web search for the given question and append the results as a Document to the documents list.

    Args:
        state (GraphState): The current graph state containing the question and documents.

    Returns:
        Dict[str, Any]: Updated state with the new web search Document appended to documents.
    """
    print("---PERFORMING WEB SEARCH---")
    question = state["question"]
    documents = state["documents"]

    # Invoke TavilySearch to get web search results for the question
    tavily_results = web_search_tool.invoke({"query": question})

    # Join the content from all search results into a single string
    joined_tavily_result = "\n\n".join(
        [result["content"] for result in tavily_results["results"]]
    )

    # Create a new Document with the joined web search results
    web_results = Document(
        page_content=joined_tavily_result,
        metadata={"source": "web_search"}
    )

    # Ensure documents is a list and append the new web search Document
    if documents is not None:
        print(f"Documents length: {len(documents)}")
        print("Appending web results to documents")
        documents.append(web_results)
        print(f"Documents length: {len(documents)}")
    else:
        print("No documents found, creating new list with web results")
        documents = [web_results]

    # Return the updated state with the new documents list
    return {"documents": documents, "question": question}

if __name__ == "__main__":
    web_search(state={"question": "agent memory?", "documents": None})
    
