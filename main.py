from dotenv import load_dotenv

from graph.graph import app

from logger import log_info, log_success, log_error, log_warning, log_header

load_dotenv()



if __name__ == "__main__":
    log_header("🤖 Sistema de Agentes IA que contesta preguntas \n fundamentadas en fuentes de información internas o externas...")

    # 1 - This question cause the stage of Happy Path and inhouse docs
    result = app.invoke(input={"question": "What is agent memory?"})

    # 1 - This question cause the stage of Happy Path and inhouse docs with spanish translation
    #result = app.invoke(input={"question": "Qué me puedes decir de los agentes de inteligencia artificial?"})
    
    # 2 - This question cause the stage of "not supported"
    #result = app.invoke(input={"question": "La empresa Red Nacional Ultima Milla parte de América Movil de México tiene inciativas de inteligencia artificaial?"})

    # 3 - This question cause the stag of happy path
    #result = app.invoke(input={"question": "Cuál es la participación de mercado de Telmex en el mercado de acceso a internet?"})

    # 4 - This question cause the stage not supported where Agent termina
    #result = app.invoke(input={"question": "gdsfgsdfgwertserttg sdfgsdfgsdfg?"})

    # 5 - This question retrive today information
    #result = app.invoke(input={"question": "Cómo termino el IPC de bolsa mexicana de valores el día de hoy?"})

    print("\n")
    log_success(f"---🤖 RESPUESTA: {result['generation']}\n")
    #print(result[-1].tool_calls[0]["args"]["answer"])
