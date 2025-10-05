from dotenv import load_dotenv

from graph.graph import app

load_dotenv()



if __name__ == "__main__":
    print("Hello, Agentic Advanced RAG!")
    #result = app.invoke(input={"question": "What is agent memory?"})
    result = app.invoke(input={"question": "Cuáles son las mejores prácticas para operar Oracle UIM?"})
    print(result.keys())
    print(result["generation"])
