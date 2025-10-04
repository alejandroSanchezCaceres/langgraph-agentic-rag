from dotenv import load_dotenv

from ingestion import retriever_vector
from graph.chains.retrieval_grader import GradeDocument, retrieval_grader_chain
load_dotenv()



def test_retrieval_grader_answer_yes() -> None:
    question = "agent memory"
    documents = retriever_vector.invoke(question)
    doc_text = documents[1].page_content

    ressult: GradeDocument = retrieval_grader_chain.invoke({"document": doc_text, "question": question})
    assert ressult.binary_score == "yes"

    