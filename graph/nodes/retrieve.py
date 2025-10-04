from typing import Any, Dict

from graph.state import GraphState
from ingestion import retrieverVecor

def retriever(state: GraphState) -> Dict[str, Any]:
    print("---RETRIEVE---")
    question = state["question"]

    documents = retrieverVecor.invoke(question)
    return {"documents": documents, "question": question}
