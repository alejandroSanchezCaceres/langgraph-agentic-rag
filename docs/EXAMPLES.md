# Ejemplos de Uso

Este documento contiene ejemplos prácticos de cómo usar LangGraph Agentic RAG.

## Ejemplos Básicos

### 1. Pregunta Simple sobre Agentes (Vectorstore)

```python
from graph.graph import app

result = app.invoke(input={
    "question": "What is agent memory?"
})
print(result['generation'])
```

**Salida esperada**:
```
Los agentes de IA usan memoria para mantener contexto entre interacciones.
La memoria puede ser episódica, semántica o procedimental.
```

### 2. Pregunta en Español

```python
from graph.graph import app

result = app.invoke(input={
    "question": "Qué me puedes decir de los agentes de inteligencia artificial?"
})
print(result['generation'])
```

**Características**:
- Detecta el idioma español
- Genera respuesta en español
- Busca en documentos internos

### 3. Pregunta que Requiere Búsqueda Web

```python
from graph.graph import app

result = app.invoke(input={
    "question": "Cómo termino el IPC de bolsa mexicana de valores el día de hoy?"
})
print(result['generation'])
print(f"Búsqueda web realizada: {result['web_search']}")
```

**Flujo**:
1. Router decide usar websearch
2. Tavily busca información actual
3. Genera respuesta basada en resultados web
4. Valida fundamentación

### 4. Pregunta no Relacionada con Documentos Internos

```python
from graph.graph import app

result = app.invoke(input={
    "question": "La empresa Red Nacional Ultima Milla parte de América Movil de México tiene iniciativas de inteligencia artificial?"
})
print(result['generation'])
```

**Comportamiento**:
- Router detecta que no está en documentos internos
- Rutea a websearch automáticamente
- Busca información en tiempo real

### 5. Pregunta Sin Sentido

```python
from graph.graph import app

result = app.invoke(input={
    "question": "gdsfgsdfgwertserttg sdfgsdfgsdfg?"
})
print(result['generation'])
```

**Resultado**:
- Respuesta corta indicando no comprensión
- Se marca como "not supported"
- Termina el flujo

## Casos de Uso Avanzados

### 6. Monitoreo del Flujo Completo

```python
from graph.graph import app
from logger import log_header

log_header("Ejemplo de monitoreo")
result = app.invoke(input={"question": "What is prompt engineering?"})

print("\n=== Información Detallada ===")
print(f"Pregunta: {result['question']}")
print(f"Respuesta: {result['generation']}")
print(f"Documentos usados: {len(result['documents'])}")
print(f"Búsqueda web: {result['web_search']}")
```

**Salida del logger**:
```
ℹ️  ---RUTANDO PREGUNTA---
ℹ️  ---🤖 DECISIÓN: RUTEANDO A RECUPERACIÓN DE DOCUMENTOS---
ℹ️  ---RECUPERANDO INFORMACIÓN---
ℹ️  ---CHECK DOCUMENT RELEVANCE TO QUESTION---
ℹ️  ---EVALUANDO RELEVANCIA DE LOS DOCUMENTOS PARA LA PREGUNTA---
ℹ️  --DECISIÓN: GENERAR RESPUESTA - TODOS LOS DOCUMENTOS SON RELEVANTES PARA LA PREGUNTA--
ℹ️  ---🤖 GENERANDO RESPUESTA---
ℹ️  ---🤖 REVISANDO ALUCINACIÓN EN LA GENERACION DE RESPUESTA---
ℹ️  ---🤖 EVALUAR QUE LA RESPUESTA CONTESTA LA PREGUNTA---
ℹ️  ---🤖 DECISIÓN: GENERACIÓN DE RESPUESTA ATIENDE LA PREGUNTA---
```

### 7. Usar Chains Individuales

```python
from graph.chains.router import question_router

# Verificar ruta sin ejecutar todo el flujo
result = question_router.invoke({"question": "What is AI?"})
print(f"Ruta sugerida: {result.datasource}")
```

### 8. Evaluar Relevancia Manual

```python
from graph.chains.retrieval_grader import retrieval_grader_chain

doc = "La inteligencia artificial es una disciplina..."
question = "What is agent memory?"

result = retrieval_grader_chain.invoke({
    "document": doc,
    "question": question
})

print(f"Score: {result.binary_score}")
print(f"Razón: {result.reason}")
```

### 9. Detectar Alucinaciones

```python
from graph.chains.hallucination_grader import hallucination_grader_chain

documents = [
    "Los agentes usan memoria para mantener contexto.",
    "Existen diferentes tipos de memoria."
]
generation = "Los agentes de IA almacenan información en bases de datos relacionales."

result = hallucination_grader_chain.invoke({
    "documents": documents,
    "generation": generation
})

print(f"Fundamentada: {result.binary_score}")
```

### 10. Generar con Contexto Personalizado

```python
from graph.chains.generation import generation_chain

context = [
    "LangGraph es una biblioteca para construir agentes.",
    "Permite definir grafos de estado y decisiones.",
    "Facilita el desarrollo de sistemas multi-agente."
]

answer = generation_chain.invoke({
    "context": context,
    "question": "What is LangGraph?"
})

print(answer)
```

## Integración con Tu Propia Aplicación

### 11. API REST Simple

```python
from flask import Flask, jsonify, request
from graph.graph import app

flask_app = Flask(__name__)

@flask_app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question')
    
    result = app.invoke(input={"question": question})
    
    return jsonify({
        "answer": result['generation'],
        "sources_used": len(result['documents']),
        "web_search": result['web_search']
    })

if __name__ == '__main__':
    flask_app.run(debug=True)
```

**Uso con curl**:
```bash
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is agent memory?"}'
```

### 12. Procesar Múltiples Preguntas

```python
from graph.graph import app

questions = [
    "What is prompt engineering?",
    "What is an AI agent?",
    "How do adversarial attacks work?"
]

for q in questions:
    result = app.invoke(input={"question": q})
    print(f"\nQ: {q}")
    print(f"A: {result['generation']}")
```

### 13. Chat Interactivo

```python
from graph.graph import app

print("=== Chat con Agentic RAG ===")
print("Escribe 'salir' para terminar\n")

while True:
    question = input("Tú: ")
    if question.lower() == 'salir':
        break
    
    result = app.invoke(input={"question": question})
    print(f"\nBot: {result['generation']}\n")
```

### 14. Guardar Resultados

```python
import json
from graph.graph import app

questions = [
    "What is agent memory?",
    "What is prompt engineering?"
]

results = []
for q in questions:
    result = app.invoke(input={"question": q})
    results.append({
        "question": q,
        "answer": result['generation'],
        "sources": len(result['documents'])
    })

with open('results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
```

### 15. Comparar Respuestas con/sin RAG

```python
from langchain_openai import ChatOpenAI
from graph.chains.generation import generation_chain

llm = ChatOpenAI(model="gpt-4o-mini")

# Sin RAG (solo LLM)
question = "What is agent memory?"
simple_answer = llm.invoke(question).content

# Con RAG (contexto + LLM)
rag_result = generation_chain.invoke({
    "context": [...],  # documentos relevantes
    "question": question
})

print("Sin RAG:", simple_answer)
print("\nCon RAG:", rag_result)
```

## Personalización

### 16. Cambiar Modelo LLM

```python
from langchain_openai import ChatOpenAI
from graph.chains.generation import generation_chain

# Usar GPT-4 en lugar de GPT-4o-mini
llm = ChatOpenAI(model="gpt-4", temperature=0)
```

### 17. Configurar Retrieval

```python
from ingestion import retriever_vector

# Cambiar número de documentos
docs = retriever_vector.invoke("What is AI?")
top_3 = docs[:3]  # Tomar solo top 3
```

### 18. Personalizar Web Search

```python
from langchain_tavily import TavilySearch

# Búsqueda con más resultados
search = TavilySearch(max_results=10)

results = search.invoke({"query": "AI agents 2024"})
```

### 19. Agregar Logging Personalizado

```python
from logger import log_info, log_success

def custom_invoke(question: str):
    log_info(f"Procesando pregunta: {question}")
    result = app.invoke(input={"question": question})
    log_success("Respuesta generada exitosamente")
    return result

result = custom_invoke("What is AI?")
```

### 20. Testing Automatizado

```python
import pytest
from graph.graph import app

def test_simple_question():
    result = app.invoke(input={"question": "What is agent memory?"})
    assert len(result['generation']) > 0
    assert result['question'] == "What is agent memory?"

def test_web_search_trigger():
    result = app.invoke(input={"question": "What happened today in tech?"})
    assert result['web_search'] == True

def test_spanish_support():
    result = app.invoke(input={"question": "Qué es IA?"})
    assert len(result['generation']) > 0
```

## Solución de Problemas

### 21. Debugging del Flujo

```python
from graph.graph import app
from logger import log_info

# Activar logs detallados
import logging
logging.basicConfig(level=logging.DEBUG)

result = app.invoke(input={"question": "Debug this"})
```

### 22. Inspeccionar Estado

```python
from graph.graph import app

result = app.invoke(input={"question": "What is AI?"})

# Ver todos los campos del estado
print("Estado completo:")
for key, value in result.items():
    if key == 'documents':
        print(f"{key}: {len(value)} documentos")
    else:
        print(f"{key}: {value}")
```

### 23. Verificar Documentos Recuperados

```python
from ingestion import retriever_vector

docs = retriever_vector.invoke("What is prompt engineering?")

for i, doc in enumerate(docs):
    print(f"\nDocumento {i+1}:")
    print(f"Contenido: {doc.page_content[:200]}...")
    print(f"Fuente: {doc.metadata.get('source', 'N/A')}")
```

## Mejores Prácticas

1. **Preguntas Claras**: Formula preguntas específicas y claras
2. **Idioma Consistente**: El sistema detecta español e inglés
3. **Manejo de Errores**: Siempre valida resultados
4. **Caching**: Considera cachear respuestas frecuentes
5. **Logging**: Usa logs para debugging y monitoreo
6. **Testing**: Prueba diferentes tipos de preguntas

