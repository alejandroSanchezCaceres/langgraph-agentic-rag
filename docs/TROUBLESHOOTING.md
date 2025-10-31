# Solución de Problemas

Esta guía ayuda a resolver problemas comunes al usar LangGraph Agentic RAG.

## Errores Comunes

### 1. Error: "Author identity unknown" en Git

**Problema**: Git no tiene configurado usuario/email

**Solución**:
```bash
git config user.name "Tu Nombre"
git config user.email "tu@email.com"
```

### 2. Error: "OPENAI_API_KEY not found"

**Problema**: Falta configurar variables de entorno

**Solución**:
1. Crea archivo `.env` desde `.env_example`
2. Agrega tu API key real de OpenAI
3. Verifica que `.env` esté en `.gitignore`

```bash
cp .env_example .env
# Edita .env con tus keys
```

### 3. Error: "ChromaDB collection not found"

**Problema**: El vectorstore no existe

**Solución**: Ejecuta el script de ingesta
```bash
poetry run python ingestion.py
```

### 4. Error: "TAVILY_API_KEY invalid"

**Problema**: API key de Tavily incorrecta o sin créditos

**Solución**:
1. Verifica tu API key en https://tavily.com
2. Confirma que tengas créditos disponibles
3. Revisa `.env`:

```env
TAVILY_API_KEY=tu_key_correcta
```

### 5. Error: "Module not found"

**Problema**: Dependencias no instaladas

**Solución**:
```bash
poetry install
# O si usas pip
pip install -r requirements.txt
```

### 6. Error: "Connection timeout" en web search

**Problema**: Problema de red o API rate limit

**Solución**:
- Verifica conectividad a internet
- Espera unos minutos si es rate limit
- Verifica tus límites en Tavily

### 7. Error: "No documents retrieved"

**Problema**: Vectorstore vacío o query no encuentra matches

**Solución**:
1. Verifica que exista `chroma.sqlite3`
2. Re-ejecuta `ingestion.py`
3. Intenta query diferente/más genérica

### 8. Error: "TypeError: 'NoneType' object"

**Problema**: Documentos None en el estado

**Solución**: Revisa `web_search.py` línea 39-43

El código ya maneja este caso:
```python
if "documents" in state:
    documents = state["documents"]
else:
    documents = None
```

## Problemas de Rendimiento

### Respuestas Lentas

**Causas posibles**:
1. **Muchos LLM calls**: Cada validación usa LLM
2. **Documentos grandes**: Chunking ineficiente
3. **Rate limits**: Límites de API

**Soluciones**:
```python
# Reducir número de documentos
docs = retriever_vector.invoke(query)
top_5 = docs[:5]

# Usar modelo más rápido
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Habilitar caching
from langchain.cache import InMemoryCache
from langchain.globals import set_llm_cache
set_llm_cache(InMemoryCache())
```

### Memoria Alta

**Causa**: ChromaDB almacenando muchos embeddings

**Solución**:
```python
# Limpiar vectorstore
import os
os.remove("chroma.sqlite3")

# Recrear con menos documentos
# Modifica URLs en ingestion.py
```

## Problemas de Calidad

### Respuestas Irrelevantes

**Causa**: Documentos recuperados no son relevantes

**Solución**:
1. Mejora chunks en `ingestion.py`:
```python
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=250,  # Reducir si muy genéricos
    chunk_overlap=50  # Aumentar para contexto
)
```

2. Ajusta threshold de relevancia en `retrieval_grader.py`

### Alucinaciones Frecuentes

**Causa**: LLM inventando información

**Solución**:
1. Ajusta system prompt en `hallucination_grader.py`:
```python
system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts."""
```

2. Verifica que `documents` se pase correctamente:
```python
result = hallucination_grader_chain.invoke({
    "documents": documents,  # Asegúrate que es lista
    "generation": generation
})
```

### Respuestas No Contestan Pregunta

**Causa**: Prompt de generación no está claro

**Solución**: Usa prompt más específico:
```python
prompt = hub.pull("rlm/rag-prompt")
# O customiza:
prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer concisely based ONLY on the context provided."),
    ("human", "Question: {question}\nContext: {context}\nAnswer:")
])
```

## Problemas de Configuración

### Poetry Lock Error

**Solución**:
```bash
poetry lock --no-update
poetry install
```

### Python Version Error

**Problema**: Python < 3.10

**Solución**: Usa Python 3.10+:
```bash
python --version  # Verificar
# Si < 3.10, instalar versión correcta
```

### Path Issues en WSL

**Problema**: Paths Windows en código

**Solución**: Actualiza `ingestion.py`:
```python
# Antes:
persist_directory="C:\\pythonProyectsAI\\langgraph-agentic-rag"

# Después:
persist_directory="./"
```

## Debugging

### Activar Logs Detallados

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspeccionar Estado

```python
from graph.graph import app

result = app.invoke(input={"question": "test"})

# Ver cada campo
for key, value in result.items():
    if isinstance(value, list):
        print(f"{key}: {len(value)} items")
    else:
        print(f"{key}: {value}")
```

### Verificar LLM Calls

```python
from langchain.callbacks import StdOutCallbackHandler

handler = StdOutCallbackHandler()
result = app.invoke(
    input={"question": "test"},
    config={"callbacks": [handler]}
)
```

### Tracer de LangSmith

Si tienes LangSmith configurado:

```python
# En .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=tu_key
LANGCHAIN_PROJECT=langgraph-agentic-rag
```

Ve a https://smith.langchain.com para ver traces

### Inspeccionar Documentos

```python
from ingestion import retriever_vector

docs = retriever_vector.invoke("test query")

for i, doc in enumerate(docs):
    print(f"\nDoc {i+1}:")
    print(f"Content: {doc.page_content[:100]}...")
    print(f"Metadata: {doc.metadata}")
```

### Debug ChromaDB

```python
import chromadb

client = chromadb.Client()

# Ver collections
print(client.list_collections())

# Verificar embedding dimensions
collection = client.get_collection("rag-chroma")
print(f"Count: {collection.count()}")
```

## Preguntas Frecuentes

### ¿Cómo cambio el modelo LLM?

Edita los archivos en `graph/chains/`:
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4", temperature=0)  # Cambia modelo aquí
```

### ¿Cómo agrego más documentos?

Edita `ingestion.py`:
```python
urls = [
    "https://lilianweng.github.io/posts/2023-06-23-agent/",
    # Agrega más URLs aquí
]
```

### ¿Cómo cambio los documentos por defecto?

```python
# En ingestion.py
urls = [
    "tu_url_1",
    "tu_url_2",
    "tu_url_3"
]

# Luego re-ejecuta
# poetry run python ingestion.py
```

### ¿Funciona con otros LLMs?

Sí, modifica la inicialización:
```python
# Anthropic Claude
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-sonnet")

# Google Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model="gemini-pro")
```

### ¿Puedo usar otra base vectorial?

Sí, modifica `ingestion.py`:
```python
# Pinecone
from langchain_pinecone import PineconeVectorStore
vectorstore = PineconeVectorStore.from_documents(docs, embeddings)

# Weaviate
from langchain_weaviate import WeaviateVectorStore
vectorstore = WeaviateVectorStore.from_documents(docs, embeddings)
```

### ¿Cómo personalizo las validaciones?

Modifica los prompts en:
- `graph/chains/retrieval_grader.py`
- `graph/chains/hallucination_grader.py`
- `graph/chains/answer_grader.py`

### ¿Es posible múltiples vueltas?

No por defecto. Para implementar:

1. Agrega memoria al estado
2. Modifica edges para permitir loops
3. Agrega condición de parada

### ¿Cómo mejoro respuestas en español?

1. Usa modelo entrenado en español
2. Personaliza prompts en español
3. Agrega documentos en español

```python
system = """Eres un asistente experto. Responde siempre en español de manera clara y concisa."""
```

## Recursos de Ayuda

- **LangChain Docs**: https://python.langchain.com
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **ChromaDB Docs**: https://docs.trychroma.com
- **OpenAI Docs**: https://platform.openai.com/docs
- **Tavily Docs**: https://tavily.com/docs

## Contactar Soporte

Si el problema persiste:

1. Revisa este documento completo
2. Consulta logs detallados
3. Busca en issues de GitHub
4. Crea issue con:
   - Descripción detallada
   - Pasos para reproducir
   - Logs relevantes
   - Versión de Python/Poetry

