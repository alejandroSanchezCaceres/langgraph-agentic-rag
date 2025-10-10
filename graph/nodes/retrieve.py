from typing import Any, Dict

from graph.state import GraphState
from ingestion import retriever_vector
from logger import log_info

def retriever(state: GraphState) -> Dict[str, Any]:
    log_info("---RECUPERANDO INFORMACIÓN---")
    question = state["question"]

    documents = retriever_vector.invoke(question)
    return {"documents": documents, "question": question}
