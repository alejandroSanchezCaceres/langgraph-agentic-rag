from typing import Any, Dict

from graph.state import GraphState
from ingestion import retriever_vector

def retriever(state: GraphState) -> Dict[str, Any]:
    print("---RETRIEVE---")
    question = state["question"]

    documents = retriever_vector.invoke(question)
    return {"documents": documents, "question": question}
