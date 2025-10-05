from dotenv import load_dotenv

from langgraph.graph import StateGraph, END

from graph.consts import RETRIEVE, GRADE_DOCUMENTS, GENERATE, WEBSEARCH
from graph.nodes import web_search, retriever, grade_documents, generate
from graph.state import GraphState

load_dotenv()

def decide_to_generate(state: GraphState) -> bool:
    """
    Decide whether to generate an answer or not based on the documents.
    """
    print("---ASSESSING DOCUMENT RELEVANCE TO QUESTION---")

    if state["web_search"]:
        print("--DECISION SEARCHING WEB: NOT ALL DOCUMENTS ARE RELEVANT TO THE QUESTION--")
        return WEBSEARCH
    else:
        print("--DECISION GENERATING ANSWER: ALL DOCUMENTS ARE RELEVANT TO THE QUESTION--")
        return GENERATE

workflow = StateGraph(GraphState)

workflow.add_node(RETRIEVE, retriever)
workflow.add_node(GRADE_DOCUMENTS, grade_documents)
workflow.add_node(GENERATE, generate)
workflow.add_node(WEBSEARCH, web_search)

workflow.set_entry_point(RETRIEVE)
workflow.add_edge(RETRIEVE, GRADE_DOCUMENTS)
workflow.add_conditional_edges(
    GRADE_DOCUMENTS, decide_to_generate,
    {
        WEBSEARCH: WEBSEARCH,
        GENERATE: GENERATE,
    },
)
workflow.add_edge(WEBSEARCH, GENERATE)
workflow.add_edge(GENERATE, END)

app = workflow.compile()

app.get_graph().draw_mermaid_png(output_file_path="graph.png")
