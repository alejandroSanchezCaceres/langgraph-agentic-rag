"""
This module defines the generation chain for producing answers using a retrieval-augmented generation (RAG) approach.
It composes a prompt, a language model, and an output parser into a single chain for generating responses.
"""

from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# Initialize the language model with the specified parameters
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Retrieve the RAG prompt template from the LangChain hub
prompt = hub.pull("rlm/rag-prompt")

# Compose the generation chain: prompt -> LLM -> output parser
generation_chain = prompt | llm | StrOutputParser()
