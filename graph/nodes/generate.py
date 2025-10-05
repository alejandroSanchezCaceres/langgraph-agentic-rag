from typing import Any, Dict

from graph.chains.generation import generation_chain
from graph.state import GraphState

def generate(state: GraphState) -> Dict[str, Any]:
    """
    Generate an answer to the given question using the provided documents as context.

    Args:
        state (GraphState): The current graph state containing the question and documents.

    Returns:
        Dict[str, Any]: Updated state with the generated answer included.
    """
    print("Generating answer...")
    question = state["question"]
    documents = state["documents"]

    result = generation_chain.invoke({"context": documents, "question": question})

    return {
        "documents": documents,
        "question": question,
        "generation": result,
    }
