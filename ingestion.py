"""
This module handles the ingestion and preprocessing of web documents for use in a retrieval-augmented generation (RAG) pipeline.
It loads documents from specified URLs, splits them into manageable chunks, and prepares a retriever using a persistent Chroma vector store.
"""

from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from logger import log_info

# Load environment variables (e.g., API keys)
load_dotenv()

# List of URLs to ingest
urls = [
    "https://lilianweng.github.io/posts/2023-06-23-agent/",
    "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
    "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",
]

# Load documents from each URL using WebBaseLoader
docs = [WebBaseLoader(url).load() for url in urls]
# Flatten the list of lists into a single list of documents
docs_list = [item for sublist in docs for item in sublist]

# Initialize a text splitter to chunk documents for embedding
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=250,
    chunk_overlap=50
)

# Split documents into smaller chunks
doc_splits = text_splitter.split_documents(docs_list)

# Prepare a retriever using a persistent Chroma vector store
retriever_vector = Chroma(
    collection_name="rag-chroma",
    embedding_function=OpenAIEmbeddings(),
    persist_directory="C:\\pythonProyectsAI\\langgraph-agentic-rag"
).as_retriever()