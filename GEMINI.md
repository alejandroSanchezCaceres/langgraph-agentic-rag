# Gemini Context: LangGraph Agentic RAG

## Project Overview
This project is an **Agentic Retrieval-Augmented Generation (RAG)** system built with **LangGraph**. It intelligently routes user queries between an internal vector store (ChromaDB) and web search (Tavily) to provide grounded and accurate responses. The system includes self-correction mechanisms for relevance, hallucination detection, and answer utility.

**Primary Goal:** Deliver a robust question-answering agent that validates its own retrieved context and generated answers.

## Technology Stack
*   **Language:** Python 3.10+
*   **Dependency Manager:** Poetry
*   **Orchestration:** LangGraph, LangChain
*   **Vector Database:** ChromaDB (local persistence)
*   **LLM:** OpenAI (GPT-4o-mini default)
*   **Web Search:** Tavily API
*   **Testing:** Pytest

## Architecture
The agent follows a graph-based workflow defined in `graph/graph.py`.

### Key Nodes (`graph/nodes/`)
1.  **Router**: Decides whether to query the vector store or perform a web search.
2.  **Retrieve**: Fetches relevant documents from ChromaDB.
3.  **Grade Documents**: Filters retrieved documents for relevance. If irrelevant, falls back to web search.
4.  **Web Search**: Queries Tavily for real-time information.
5.  **Generate**: Synthesizes an answer using the LLM.
6.  **Grade Generation**: Checks for hallucinations and whether the answer addresses the question.

### Data Ingestion
*   **Script:** `ingestion.py`
*   **Source:** Loads documents from specified URLs (e.g., Lilian Weng's blog) into the local ChromaDB instance.
*   **Storage:** `.chroma/` directory.

## Development & Usage

### 1. Setup
Ensure `.env` is configured with necessary API keys:
```bash
OPENAI_API_KEY=...
LANGCHAIN_API_KEY=...
TAVILY_API_KEY=...
```

### 2. Dependency Management
Install dependencies using Poetry:
```bash
poetry install
```

### 3. Data Ingestion
Populate the vector database before running the agent:
```bash
poetry run python ingestion.py
```

### 4. Running the Agent
Execute the main script to query the agent:
```bash
poetry run python main.py
```
*Modify `main.py` to change the input question.*

### 5. Testing & Formatting
*   **Run Tests:** `poetry run pytest`
*   **Format Code:** `poetry run black .`
*   **Sort Imports:** `poetry run isort .`

## File Structure Highlights
*   `graph/`: Core logic.
    *   `chains/`: LLM chain definitions (prompts + models).
    *   `nodes/`: Functional units of the graph.
    *   `state.py`: TypedDict defining the graph state.
*   `main.py`: Entry point for CLI interaction.
*   `ingestion.py`: ETL process for the knowledge base.
*   `README.md`: Comprehensive documentation (in Spanish).
