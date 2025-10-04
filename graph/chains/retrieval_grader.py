"""
This module provides a chain for grading the relevance of retrieved documents to a user question.
It uses a language model to assign a binary relevance score and provide reasoning.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Initialize the language model for grading
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


class GradeDocument(BaseModel):
    """
    Binary score for relevance check on retrieved documents.

    Attributes:
        binary_score: 'yes' if the document is relevant to the question, 'no' otherwise.
        reason: Explanation for the assigned score.
    """

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )
    reason: str = Field(description="Reasoning for the score")


# Wrap the LLM with structured output for document grading
structured_llm_grader = llm.with_structured_output(GradeDocument)

# System prompt for the grader
system_prompt = (
    "You are a grader assessing relevance of a retrieved document to a user question.\n"
    "If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant.\n"
    "Give a binary score 'yes' or 'no' to indicate whether the document is relevant to the question."
)

# Human prompt template for document and question
grader_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "Retrieved document:\n{document}\nquestion: {question}"),
    ]
)

# The retrieval grader chain: prompt -> LLM with structured output
retrieval_grader_chain = grader_prompt | structured_llm_grader
