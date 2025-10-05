from dotenv import load_dotenv

from ingestion import retriever_vector
from graph.chains.retrieval_grader import GradeDocument, retrieval_grader_chain
from graph.chains.generation import generation_chain
from graph.chains.hallucination_grader import hallucination_grader_chain, GradeHallucination

load_dotenv()

def test_retrieval_grader_answer_yes() -> None:
    question = "agent memory"
    documents = retriever_vector.invoke(question)
    doc_text = documents[1].page_content

    ressult: GradeDocument = retrieval_grader_chain.invoke({"document": doc_text, "question": question})
    assert ressult.binary_score == "yes"
    print("Reason: \n", ressult.reason)


def test_retrieval_grader_answer_no() -> None:
    question = "how to make pizza"
    documents = retriever_vector.invoke(question)
    doc_text = documents[1].page_content

    ressult: GradeDocument = retrieval_grader_chain.invoke({"document": doc_text, "question": question})
    assert ressult.binary_score == "no"
    print("Reason: \n", ressult.reason)

def test_generation_chain() -> None:
    question = "agent memory"
    documents = retriever_vector.invoke(question)
    result = generation_chain.invoke({"context": documents, "question": question})
    print("Result: \n", result)

def test_hallucination_grader_answer_yes() -> None:
    question = "agent memory"
    documents = retriever_vector.invoke(question)
    generation = generation_chain.invoke({"context": documents, "question": question})
    result: GradeHallucination = hallucination_grader_chain.invoke({"documents": documents, "generation": generation})
    print("Result: \n", result)
    assert result.binary_score

def test_hallucination_grader_answer_no() -> None:
    question = "agent memory"
    documents = retriever_vector.invoke(question)
    #generation = generation_chain.invoke({"context": documents, "question": question})
    result: GradeHallucination = hallucination_grader_chain.invoke({"documents": documents, "generation": "In order to make a pizza we need to first start with the dugh."})
    print("Result: \n", result)
    assert not result.binary_score