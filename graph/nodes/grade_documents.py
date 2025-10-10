from typing import Any, Dict

from graph.chains.retrieval_grader import retrieval_grader_chain
from graph.state import GraphState

from logger import log_info

def grade_documents(state: GraphState) -> Dict[str, Any]:
    """
    Determines whether the retrieved documents are relevant to the question
    If any document is not relevant, we will set a flag to run web search

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Filtered out irrelevant documents and updated web_search state
    """

    log_info("---CHECK DOCUMENT RELEVANCE TO QUESTION---")

    question = state["question"]
    documents = state["documents"]

    filtered_documents = []
    web_search_required = False

    for document in documents:
        score = retrieval_grader_chain.invoke({"document": document.page_content, "question": question})
        if score.binary_score.lower() == "yes":
            log_info(f"---Document {document.metadata['source']} is relevant to the question")
            filtered_documents.append(document)
        else:
            log_info(f"---Document {document.metadata['source']} is not relevant to the question")
            web_search_required = True
            continue

    return {"documents": filtered_documents, "question": question, "web_search": web_search_required}
