# Arquitectura del Sistema

## Visión General

LangGraph Agentic RAG implementa un sistema de RAG (Retrieval-Augmented Generation) con capacidades de agente que puede decidir dinámicamente entre múltiples fuentes de información para proporcionar respuestas precisas y fundamentadas.

## Flujo de Datos

El sistema procesa preguntas a través de los siguientes pasos:

```
Usuario → Router → [Retrieve | WebSearch] → Grade → Generate → Validate → Respuesta
```

### 1. Ruteo Inicial (Router)

**Archivo**: `graph/chains/router.py`

El router analiza la pregunta del usuario y decide qué fuente de datos utilizar:

- **Vectorstore**: Para preguntas sobre agentes, prompt engineering, adversarial attacks
- **WebSearch**: Para cualquier otra pregunta

**Implementación**:
- Usa `RouteQuery` (Pydantic) para respuesta estructurada
- Modelo: GPT-4o-mini con temperatura 0
- Output: "vectorstore" o "websearch"

### 2. Recuperación (Retrieve)

**Archivo**: `graph/nodes/retrieve.py`

Recupera documentos relevantes del vectorstore usando búsqueda semántica:

- **Vectorstore**: ChromaDB con persistencia local
- **Embeddings**: OpenAI Embeddings
- **Retrieval**: Top-K documentos más relevantes a la pregunta

### 3. Evaluación de Documentos (Grade Documents)

**Archivo**: `graph/nodes/grade_documents.py`

Evalúa cada documento recuperado para determinar su relevancia:

- **Chain**: `retrieval_grader_chain`
- **Output**: Binario (yes/no) con razonamiento
- **Acción**: 
  - Si algún documento no es relevante → activa búsqueda web
  - Filtra documentos irrelevantes antes de generar

### 4. Búsqueda Web (Web Search)

**Archivo**: `graph/nodes/web_search.py`

Ejecuta búsqueda web complementaria usando Tavily:

- **Max Results**: 3 resultados
- **Output**: Documento combinado con metadata "web_search"
- **Uso**: Cuando documentos internos son insuficientes o irrelevantes

### 5. Generación (Generate)

**Archivo**: `graph/nodes/generate.py`

Genera la respuesta final usando el contexto disponible:

- **Chain**: `generation_chain` (LangChain Hub)
- **Prompt**: RAG prompt template optimizado
- **Output**: Respuesta concisa (máximo 3 oraciones)

### 6. Validación de Generación

**Archivo**: `graph/graph.py` - `grade_generation_grounded_in_documents_and_question`

Implementa dos validaciones secuenciales:

#### 6.1. Hallucination Grader
- **Archivo**: `graph/chains/hallucination_grader.py`
- **Verifica**: Si la respuesta está fundamentada en los documentos
- **Output**: 
  - `true`: La respuesta está fundamentada
  - `false`: Hay alucinaciones

#### 6.2. Answer Grader
- **Archivo**: `graph/chains/answer_grader.py`
- **Verifica**: Si la respuesta contesta la pregunta
- **Output**: Binario (yes/no)

**Decisiones finales**:
- `useful`: Respuesta correcta → END
- `not useful`: Respuesta no contesta → WebSearch
- `not supported`: Alucinaciones detectadas → END

## Estado del Grafo

**Archivo**: `graph/state.py`

```python
class GraphState(TypedDict):
    question: str        # Pregunta del usuario
    generation: str      # Respuesta generada
    web_search: bool     # Flag para búsqueda web
    documents: List[str] # Documentos de contexto
```

## Construcción del Grafo

**Archivo**: `graph/graph.py`

```python
workflow = StateGraph(GraphState)

# Nodos
workflow.add_node(RETRIEVE, retriever)
workflow.add_node(GRADE_DOCUMENTS, grade_documents)
workflow.add_node(GENERATE, generate)
workflow.add_node(WEBSEARCH, web_search)

# Entry point condicional
workflow.set_conditional_entry_point(route_question, {...})

# Edges
workflow.add_edge(RETRIEVE, GRADE_DOCUMENTS)
workflow.add_conditional_edges(GRADE_DOCUMENTS, decide_to_generate, {...})
workflow.add_conditional_edges(GENERATE, grade_generation, {...})
workflow.add_edge(WEBSEARCH, GENERATE)
workflow.add_edge(GENERATE, END)

# Compilar
app = workflow.compile()
```

## Cadenas de Procesamiento

### Router Chain
- **Función**: Decidir fuente de datos
- **Modelo**: GPT-4o-mini
- **Output Estructurado**: RouteQuery

### Retrieval Grader Chain
- **Función**: Evaluar relevancia de documentos
- **Modelo**: GPT-4o-mini
- **Output Estructurado**: GradeDocument (binary_score, reason)

### Hallucination Grader Chain
- **Función**: Detectar alucinaciones
- **Modelo**: GPT-4o-mini
- **Output Estructurado**: GradeHallucination (binary_score: bool)

### Answer Grader Chain
- **Función**: Verificar utilidad de respuesta
- **Modelo**: GPT-4o-mini
- **Output Estructurado**: GradeAnswer (binary_score: bool)

### Generation Chain
- **Función**: Generar respuesta final
- **Modelo**: GPT-4o-mini
- **Prompt**: LangChain Hub ("rlm/rag-prompt")
- **Output**: String de texto

## Almacenamiento

### Vectorstore: ChromaDB

**Configuración**:
- **Embeddings**: OpenAI Embeddings
- **Collection**: "rag-chroma"
- **Persistencia**: Local (archivo SQLite)
- **Chunking**: RecursiveCharacterTextSplitter
  - Chunk size: 250 caracteres
  - Overlap: 50 caracteres
  - Encoder: tiktoken

## Herramientas Externas

### TavilySearch
- **Propósito**: Búsqueda web optimizada para AI
- **Max Results**: 3
- **Output**: Documentos con metadata

### LangChain Hub
- **Recurso**: "rlm/rag-prompt"
- **Uso**: Plantilla para generación de respuestas

## Logging

**Archivo**: `logger.py`

Sistema de logging con colores y emojis para facilitar debugging:

- `log_info()`: Mensajes informativos (cyan)
- `log_success()`: Operaciones exitosas (verde)
- `log_error()`: Errores (rojo)
- `log_warning()`: Advertencias (amarillo)
- `log_header()`: Encabezados de sección (purple, bold)

## Decisiones de Diseño

### 1. Separación de Responsabilidades
- Cada nodo tiene una responsabilidad única
- Chains reutilizables para diferentes contextos
- Estado compartido a través de GraphState

### 2. Validación en Múltiples Capas
- Validación de relevancia de documentos
- Validación de fundamentación
- Validación de utilidad

### 3. Fallback Inteligente
- Si documentos no son relevantes → buscar en web
- Si respuesta no contesta → buscar en web
- Si hay alucinaciones → terminar

### 4. Persistencia
- ChromaDB para almacenar embeddings
- Permite reutilizar embeddings sin recalcular
- Optimiza tiempo de búsqueda

## Optimizaciones

### Chunking
- Tamaño pequeño (250) para granularidad
- Overlap (50) para mantener contexto
- tiktoken para división precisa

### Retrieval
- Top-K automático basado en similitud
- Filtrado posterior con grader

### Generación
- Prompt conciso para respuestas breves
- Temperature 0 para consistencia
- Validación de fundamentación

## Extensiones Futuras

Posibles mejoras al sistema:

1. **Memoria de Conversación**: Mantener contexto entre turnos
2. **Múltiples Fuentes**: Integrar más bases de datos
3. **Fine-tuning**: Ajustar prompts para casos específicos
4. **Caching**: Cachear resultados frecuentes
5. **Streaming**: Respuestas en tiempo real
6. **Métricas**: Tracking de performance y calidad

