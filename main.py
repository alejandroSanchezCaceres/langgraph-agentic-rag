from dotenv import load_dotenv
load_dotenv()
import os

if __name__ == "__main__":
    print("Hello, Agentic RAG!")
    print(os.getenv("OPENAI_API_KEY"))
