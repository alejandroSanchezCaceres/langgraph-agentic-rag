# LangGraph Agentic RAG

Un sistema de **Agentic Retrieval-Augmented Generation (RAG)** construido con LangGraph que combina recuperación de documentos vectoriales y búsqueda web para generar respuestas fundamentadas y precisas a preguntas de los usuarios.

## 🎯 Descripción

Este proyecto implementa un agente inteligente que decide automáticamente si responder desde documentos internos vectorizados o desde búsquedas web en tiempo real. Incluye validación de relevancia, detección de alucinaciones y evaluación de utilidad de las respuestas.

## ✨ Características

- **Ruteo Inteligente**: Decide entre vectorstore interno y búsqueda web según el contexto de la pregunta
- **Validación de Relevancia**: Evalúa si los documentos recuperados son relevantes para la pregunta
- **Detección de Alucinaciones**: Verifica que las respuestas estén fundamentadas en las fuentes
- **Evaluación de Utilidad**: Confirma que la respuesta aborda correctamente la pregunta
- **Búsqueda Web Integrada**: Complementa información con Tavily cuando es necesario
- **Persistencia de Datos**: Usa ChromaDB para almacenar documentos vectorizados

## 🏗️ Arquitectura

El sistema implementa un flujo de trabajo con nodos especializados:

```
┌─────────────┐
│   Router    │ Decide: vectorstore o websearch
└──────┬──────┘
       │
       ├─→ RETRIEVE → GRADE_DOCUMENTS → DECIDE_TO_GENERATE
       │                                    │
       │                                    ├─→ GENERATE → GRADE_GENERATION
       │                                    │                │
       │                                    │                ├─→ END (useful)
       │                                    │                ├─→ WEBSEARCH (not useful)
       │                                    │                └─→ END (not supported)
       │                                    │
       └─→ WEBSEARCH → GENERATE → END
```

### Nodos del Grafo

- **Router**: Decide qué fuente de datos usar (vectorstore o web search)
- **Retrieve**: Recupera documentos relevantes del vectorstore
- **Grade Documents**: Evalúa la relevancia de los documentos recuperados
- **Web Search**: Realiza búsqueda web con Tavily
- **Generate**: Genera la respuesta final usando el contexto disponible
- **Grade Generation**: Valida la calidad y fundamentación de la respuesta

## 🚀 Instalación

### Requisitos

- Python >= 3.10
- Poetry (para gestión de dependencias)

### Pasos

1. Clona el repositorio:
```bash
git clone https://github.com/alejandroSanchezCaceres/langgraph-agentic-rag.git
cd langgraph-agentic-rag
```

2. Instala las dependencias:
```bash
poetry install
```

3. Configura las variables de entorno:
```bash
cp .env_example .env
```

Edita el archivo `.env` con tus API keys:
```
OPENAI_API_KEY=tu_key_aqui
LANGCHAIN_API_KEY=tu_key_aqui
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=langgraph-agentic-rag
TAVILY_API_KEY=tu_key_aqui
```

4. (Opcional) Ejecuta el script de ingesta para cargar documentos iniciales:
```bash
poetry run python ingestion.py
```

## 📖 Uso

### Ejecutar el Agente

```bash
poetry run python main.py
```

### Personalizar las Preguntas

Edita `main.py` y descomenta/modifica las preguntas de ejemplo:

```python
# Pregunta que usa documentos internos
result = app.invoke(input={"question": "What is agent memory?"})

# Pregunta que requiere búsqueda web
result = app.invoke(input={"question": "Cómo termino el IPC de bolsa mexicana de valores el día de hoy?"})

# Pregunta en español
result = app.invoke(input={"question": "Qué me puedes decir de los agentes de inteligencia artificial?"})
```

## 🧩 Componentes Principales

### Chains (Cadenas de Procesamiento)

- **Router**: Rutea preguntas a la fuente de datos apropiada
- **Retrieval Grader**: Evalúa relevancia de documentos
- **Hallucination Grader**: Detecta alucinaciones en respuestas
- **Answer Grader**: Verifica que la respuesta conteste la pregunta
- **Generation**: Genera respuestas fundamentadas en contexto

### Nodos

- **retrieve**: Recuperación de documentos desde ChromaDB
- **grade_documents**: Evaluación de relevancia de documentos
- **web_search**: Búsqueda web con Tavily
- **generate**: Generación de respuestas con LLM

## 🔧 Configuración

### Modelo LLM

Por defecto usa `gpt-4o-mini`. Puedes modificarlo en los archivos de chains:

```python
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
```

### Vectorstore

Usa ChromaDB con persistencia local. Configuración en `ingestion.py`:

```python
retriever_vector = Chroma(
    collection_name="rag-chroma",
    embedding_function=OpenAIEmbeddings(),
    persist_directory="./"
).as_retriever()
```

### Documentos Iniciales

Por defecto carga documentos de:
- Agentes de IA (Lilian Weng)
- Prompt Engineering
- Adversarial Attacks en LLMs

Puedes modificar la lista de URLs en `ingestion.py`.

## 📊 Validaciones y Control de Calidad

El sistema implementa tres niveles de validación:

1. **Relevancia de Documentos**: Si no son relevantes, busca en la web
2. **Fundamentación**: Si la respuesta no está basada en documentos, termina
3. **Utilidad**: Si no contesta la pregunta, intenta con búsqueda web

## 🛠️ Desarrollo

### Estructura del Proyecto

```
langgraph-agentic-rag/
├── graph/                    # Nodos y configuración del grafo
│   ├── chains/              # Cadenas de procesamiento
│   │   ├── router.py
│   │   ├── retrieval_grader.py
│   │   ├── hallucination_grader.py
│   │   ├── answer_grader.py
│   │   └── generation.py
│   ├── nodes/               # Nodos del grafo
│   │   ├── retrieve.py
│   │   ├── grade_documents.py
│   │   ├── web_search.py
│   │   └── generate.py
│   ├── graph.py            # Construcción del grafo
│   ├── state.py            # Estado del grafo
│   └── consts.py           # Constantes
├── ingestion.py            # Script de ingesta de documentos
├── main.py                 # Punto de entrada
├── logger.py               # Utilidades de logging
├── pyproject.toml          # Configuración Poetry
└── README.md               # Este archivo
```

### Ejecutar Pruebas

```bash
poetry run pytest
```

### Formateo de Código

```bash
poetry run black .
poetry run isort .
```

## 📝 Licencia

Este proyecto es de uso educativo y de investigación.

## 👤 Autor

**Gualberto Alejandro Sanchez Caceres**
- Email: sanchezga@globalhitss.com

## 🙏 Agradecimientos

- [LangGraph](https://github.com/langchain-ai/langgraph) - Framework para agentes AI
- [LangChain](https://github.com/langchain-ai/langchain) - Framework para aplicaciones LLM
- [ChromaDB](https://www.trychroma.com/) - Base de datos vectorial
- [Tavily](https://tavily.com/) - API de búsqueda web para AI

## 🔗 Referencias

- [Agentes de IA - Lilian Weng](https://lilianweng.github.io/posts/2023-06-23-agent/)
- [Prompt Engineering - Lilian Weng](https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/)
- [Adversarial Attacks on LLMs - Lilian Weng](https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/)

