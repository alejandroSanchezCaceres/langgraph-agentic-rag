from dotenv import load_dotenv

from langgraph.graph import StateGraph, END

from graph.consts import RETRIEVE, GRADE_DOCUMENTS, GENERATE, WEBSEARCH
from graph.nodes import web_search, retriever, grade_documents, generate
from graph.state import GraphState
from graph.chains.answer_grader import answer_grader_chain
from graph.chains.hallucination_grader import hallucination_grader_chain

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

def grade_eneration_grounded_in_documnts_and_question(state: GraphState) -> str:
    print("---CHECK HALLUCINATION IN GENERATION---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader_chain.invoke({"documents": documents, "generation": generation})
    if score.binary_score:
        print("---GENERATION IS GROUNDED IN DOCUMENTS---")
        print("---GRADE GENERATION vs QUESTION")
        score = answer_grader_chain.invoke({"question": question, "generation": generation})
        if score.binary_score:
            print("---DECISION: GNERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GNERATION DOES NOT ADDRESS QUESTION---")
            return "not useful "
    else:
        print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"
    


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

workflow.add_conditional_edges(
    GENERATE, 
    grade_eneration_grounded_in_documnts_and_question,
    path_map={
        "useful": END,
        "not useful": GENERATE,
        "not supported": WEBSEARCH,
    },
)

workflow.add_edge(WEBSEARCH, GENERATE)
workflow.add_edge(GENERATE, END)

app = workflow.compile()

app.get_graph().draw_mermaid_png(output_file_path="graph.png")
#print(app.get_graph().draw_mermaid())
