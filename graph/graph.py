from dotenv import load_dotenv

from langgraph.graph import StateGraph, END

from graph.consts import RETRIEVE, GRADE_DOCUMENTS, GENERATE, WEBSEARCH
from graph.nodes import web_search, retriever, grade_documents, generate
from graph.state import GraphState
from graph.chains.answer_grader import answer_grader_chain
from graph.chains.hallucination_grader import hallucination_grader_chain
from graph.chains.router import question_router, RouteQuery

from logger import log_info, log_success, log_error, log_warning, log_header

# Load environment variables from .env file
load_dotenv()

def decide_to_generate(state: GraphState):
    """
    Decide whether to generate an answer or not based on the documents.
    If web_search is True in the state, route to WEBSEARCH.
    Otherwise, route to GENERATE.
    """
    log_info("---EVALUANDO RELEVANCIA DE LOS DOCUMENTOS PARA LA PREGUNTA---")

    if state["web_search"]:
        log_info("---DECISIÓN: BUSCAR EN LA WEB PARA COMPLEMENTAR LA INFORMACIÓN - NO TODOS LOS DOCUMENTOS SON RELEVANTES PARA LA PREGUNTA--")
        return WEBSEARCH
    else:
        log_info("--DECISIÓN: GENERAR RESPUESTA - TODOS LOS DOCUMENTOS SON RELEVANTES PARA LA PREGUNTA--")
        return GENERATE

def grade_generation_grounded_in_documents_and_question(state: GraphState) -> str:
    """
    Grade whether the generated answer is grounded in the provided documents and addresses the question.
    First, check for hallucination (is the answer grounded in the documents?).
    If grounded, check if the answer addresses the question.
    Returns:
        - "useful" if answer is grounded and addresses the question
        - "not useful" if answer is grounded but does not address the question
        - "not supported" if answer is not grounded (hallucinated)
    """
    log_info("---🤖 REVISANDO ALUCINACIÓN EN LA GENERACION DE RESPUESTA---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    # Check if the generation is grounded in the documents
    score = hallucination_grader_chain.invoke({"documents": documents, "generation": generation})
    if hallucinations_grade := score.binary_score:
        log_info("---🤖 EVALUAR QUE LA RESPUESTA CONTESTA LA PREGUNTA---")
        # If grounded, check if the answer addresses the question
        score = answer_grader_chain.invoke({"question": question, "generation": generation})
        if answer_grade := score.binary_score:
            log_info("---🤖 DECISIÓN: GENERACIÓN DE RESPUESTA ATIENDE LA PREGUNTA---")
            return "useful"
        else:
            log_info("---🤖DECISIÓN: GENERACIÓN DE RESPUESTA NO ATIENDE LA PREGUNTA---")
            return "not useful"
    else:
        log_info("---🤖DECISIÓN: GENERACIÓN DE RESPUESTA NO ESTA BASADA EN LOS DOCUMENTOS, REINTENTAR---")
        return "not supported"

def route_question(state: GraphState) -> str:
    """
    Route the question to either websearch or vectorstore retrieval based on its content.
    Uses the question_router chain to determine the appropriate datasource.
    Returns:
        - WEBSEARCH if the router decides to use web search
        - RETRIEVE if the router decides to use the vectorstore
    """
    log_info("---RUTANDO PREGUNTA---")
    question = state["question"]
    result: RouteQuery = question_router.invoke({"question": question})
    if result.datasource == WEBSEARCH:
        log_info("---🤖 DECISIÓN: RUTEANDO A BÚSQUEDA WEB---")
        return WEBSEARCH
    else:
        log_info("---🤖 DECISIÓN: RUTEANDO A RECUPERACIÓN DE DOCUMENTOS---")
        return RETRIEVE
    

# Initialize the workflow graph with the custom state class
workflow = StateGraph(GraphState)

# Add nodes to the workflow graph
workflow.add_node(RETRIEVE, retriever)
workflow.add_node(GRADE_DOCUMENTS, grade_documents)
workflow.add_node(GENERATE, generate)
workflow.add_node(WEBSEARCH, web_search)

# Set the conditional entry point based on the router's decision
workflow.set_conditional_entry_point(
    route_question,
    {
        WEBSEARCH: WEBSEARCH,
        RETRIEVE: RETRIEVE,
    },
)

# Define the edges between nodes in the workflow
workflow.add_edge(RETRIEVE, GRADE_DOCUMENTS)
workflow.add_conditional_edges(
    GRADE_DOCUMENTS, decide_to_generate,
    {
        WEBSEARCH: WEBSEARCH,
        GENERATE: GENERATE,
    },
)

# Add conditional edges for the GENERATE node based on grading results
workflow.add_conditional_edges(
    GENERATE, 
    grade_generation_grounded_in_documents_and_question,
    path_map={
        "useful": END,           # End if answer is useful
        "not useful": WEBSEARCH,  # Route to websearch if not grounded
        "not supported": END, # Retry generation if not supported
    },
)

# Add direct edges for websearch and generation completion
workflow.add_edge(WEBSEARCH, GENERATE)
workflow.add_edge(GENERATE, END)

# Compile the workflow into an executable app
app = workflow.compile()

# Draw the workflow graph as a PNG image
app.get_graph().draw_mermaid_png(output_file_path="graph.png")
# Uncomment the following line to print the Mermaid diagram to stdout
#print(app.get_graph().draw_mermaid())
