"""
This module defines the generation chain for producing answers using a retrieval-augmented generation (RAG) approach.
It composes a prompt, a language model, and an output parser into a single chain for generating responses.
"""
from dotenv import load_dotenv

from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

load_dotenv()

# Initialize the language model with the specified parameters
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Retrieve the RAG prompt template from the LangChain hub
# Example of prompt get it
"""
    human
    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
    Question: {question} 
    Context: {context} 
    Answer:
    """
prompt = hub.pull("rlm/rag-prompt")

# Compose the generation chain: prompt -> LLM -> output parser
generation_chain = prompt | llm | StrOutputParser()
