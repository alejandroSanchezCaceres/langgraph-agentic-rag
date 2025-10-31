# Referencia de API

## Módulo principal: graph.graph

### `app.invoke(input: dict) -> dict`

Ejecuta el grafo completo con la pregunta del usuario.

**Parámetros**:
- `input` (dict): Diccionario con la pregunta
  - `question` (str): La pregunta del usuario

**Retorna**:
- `dict`: Estado final del grafo con:
  - `question` (str): Pregunta original
  - `generation` (str): Respuesta generada
  - `web_search` (bool): Si se realizó búsqueda web
  - `documents` (list): Documentos usados para contexto

**Ejemplo**:
```python
result = app.invoke(input={"question": "What is agent memory?"})
print(result['generation'])
```

## Chains

### Router Chain

**Archivo**: `graph/chains/router.py`

#### `question_router.invoke(input: dict) -> RouteQuery`

Rutea una pregunta a la fuente de datos apropiada.

**Parámetros**:
- `input` (dict):
  - `question` (str): Pregunta a rutear

**Retorna**:
- `RouteQuery`: Objeto con:
  - `datasource` (Literal["vectorstore", "websearch"]): Fuente recomendada

**Ejemplo**:
```python
result = question_router.invoke({"question": "What is Python?"})
print(result.datasource)  # "vectorstore" o "websearch"
```

### Retrieval Grader Chain

**Archivo**: `graph/chains/retrieval_grader.py`

#### `retrieval_grader_chain.invoke(input: dict) -> GradeDocument`

Evalúa si un documento es relevante para una pregunta.

**Parámetros**:
- `input` (dict):
  - `document` (str): Contenido del documento
  - `question` (str): Pregunta del usuario

**Retorna**:
- `GradeDocument`: Objeto con:
  - `binary_score` (str): "yes" o "no"
  - `reason` (str): Razonamiento

**Ejemplo**:
```python
result = retrieval_grader_chain.invoke({
    "document": "...",
    "question": "What is AI?"
})
print(result.binary_score)  # "yes" o "no"
```

### Hallucination Grader Chain

**Archivo**: `graph/chains/hallucination_grader.py`

#### `hallucination_grader_chain.invoke(input: dict) -> GradeHallucination`

Detecta si una generación está fundamentada en documentos.

**Parámetros**:
- `input` (dict):
  - `documents` (list): Lista de documentos
  - `generation` (str): Respuesta generada

**Retorna**:
- `GradeHallucination`: Objeto con:
  - `binary_score` (bool): True si fundamentada, False si hay alucinaciones

**Ejemplo**:
```python
result = hallucination_grader_chain.invoke({
    "documents": [...],
    "generation": "..."
})
print(result.binary_score)  # True o False
```

### Answer Grader Chain

**Archivo**: `graph/chains/answer_grader.py`

#### `answer_grader_chain.invoke(input: dict) -> GradeAnswer`

Verifica si una respuesta contesta la pregunta.

**Parámetros**:
- `input` (dict):
  - `question` (str): Pregunta original
  - `generation` (str): Respuesta generada

**Retorna**:
- `GradeAnswer`: Objeto con:
  - `binary_score` (bool): True si contesta, False si no

**Ejemplo**:
```python
result = answer_grader_chain.invoke({
    "question": "What is AI?",
    "generation": "..."
})
print(result.binary_score)  # True o False
```

### Generation Chain

**Archivo**: `graph/chains/generation.py`

#### `generation_chain.invoke(input: dict) -> str`

Genera una respuesta usando contexto y pregunta.

**Parámetros**:
- `input` (dict):
  - `context` (list): Documentos de contexto
  - `question` (str): Pregunta del usuario

**Retorna**:
- `str`: Respuesta generada

**Ejemplo**:
```python
answer = generation_chain.invoke({
    "context": [...],
    "question": "What is AI?"
})
print(answer)
```

## Nodos

### Retriever Node

**Archivo**: `graph/nodes/retrieve.py`

#### `retriever(state: GraphState) -> dict`

Recupera documentos relevantes del vectorstore.

**Parámetros**:
- `state` (GraphState): Estado actual del grafo

**Retorna**:
- `dict`: Estado actualizado con:
  - `documents`: Documentos recuperados
  - `question`: Pregunta original

### Grade Documents Node

**Archivo**: `graph/nodes/grade_documents.py`

#### `grade_documents(state: GraphState) -> dict`

Evalúa relevancia de documentos y determina si se necesita búsqueda web.

**Parámetros**:
- `state` (GraphState): Estado actual del grafo

**Retorna**:
- `dict`: Estado actualizado con:
  - `documents`: Documentos relevantes filtrados
  - `web_search`: Flag si se requiere búsqueda web

### Web Search Node

**Archivo**: `graph/nodes/web_search.py`

#### `web_search(state: GraphState) -> dict`

Realiza búsqueda web usando Tavily.

**Parámetros**:
- `state` (GraphState): Estado actual del grafo

**Retorna**:
- `dict`: Estado actualizado con:
  - `documents`: Documentos existentes + resultados web
  - `question`: Pregunta original

### Generate Node

**Archivo**: `graph/nodes/generate.py`

#### `generate(state: GraphState) -> dict`

Genera respuesta usando documentos y pregunta.

**Parámetros**:
- `state` (GraphState): Estado actual del grafo

**Retorna**:
- `dict`: Estado actualizado con:
  - `documents`: Documentos usados
  - `question`: Pregunta original
  - `generation`: Respuesta generada

## Funciones de Decisión

### `route_question(state: GraphState) -> str`

Decide qué ruta tomar basado en el router.

**Parámetros**:
- `state` (GraphState): Estado actual del grafo

**Retorna**:
- `str`: "websearch" o "retrieve"

### `decide_to_generate(state: GraphState) -> str`

Decide si generar respuesta o buscar en web.

**Parámetros**:
- `state` (GraphState): Estado actual del grafo

**Retorna**:
- `str`: "generate" o "websearch"

### `grade_generation_grounded_in_documents_and_question(state: GraphState) -> str`

Valida la calidad y utilidad de la respuesta generada.

**Parámetros**:
- `state` (GraphState): Estado actual del grafo

**Retorna**:
- `str`: "useful", "not useful", o "not supported"

## Utilidades

### Logger

**Archivo**: `logger.py`

Funciones de logging con colores:

#### `log_info(message: str, color: str = Colors.CYAN)`

Log informativo.

#### `log_success(message: str)`

Log de éxito (verde).

#### `log_error(message: str)`

Log de error (rojo).

#### `log_warning(message: str)`

Log de advertencia (amarillo).

#### `log_header(message: str)`

Log de encabezado (púrpura, bold).

### Ingesta

**Archivo**: `ingestion.py`

#### `retriever_vector.invoke(query: str) -> list`

Recupera documentos del vectorstore.

**Parámetros**:
- `query` (str): Query de búsqueda

**Retorna**:
- `list`: Lista de documentos relevantes

**Ejemplo**:
```python
docs = retriever_vector.invoke("What is AI?")
for doc in docs:
    print(doc.page_content)
```

## Tipo de Datos

### GraphState

```python
class GraphState(TypedDict):
    question: str         # Pregunta del usuario
    generation: str       # Respuesta generada
    web_search: bool      # Flag de búsqueda web
    documents: List[str]  # Documentos de contexto
```

### RouteQuery

```python
class RouteQuery(BaseModel):
    datasource: Literal["vectorstore", "websearch"]
```

### GradeDocument

```python
class GradeDocument(BaseModel):
    binary_score: str     # "yes" o "no"
    reason: str           # Razonamiento
```

### GradeHallucination

```python
class GradeHallucination(BaseModel):
    binary_score: bool    # True o False
```

### GradeAnswer

```python
class GradeAnswer(BaseModel):
    binary_score: bool    # True o False
```

## Constantes

**Archivo**: `graph/consts.py`

```python
RETRIEVE = "retrieve"
GRADE_DOCUMENTS = "grade_documents"
GENERATE = "generate"
WEBSEARCH = "websearch"
```

## Ejemplos de Uso Completos

### Ejemplo 1: Pregunta Simple

```python
from graph.graph import app

# Pregunta sobre agentes (usa vectorstore)
result = app.invoke(input={
    "question": "What is agent memory?"
})
print(f"Respuesta: {result['generation']}")
```

### Ejemplo 2: Pregunta Actual (usa web search)

```python
from graph.graph import app

# Pregunta sobre evento actual (usa búsqueda web)
result = app.invoke(input={
    "question": "Cómo termino el IPC de bolsa mexicana hoy?"
})
print(f"Respuesta: {result['generation']}")
print(f"¿Búsqueda web?: {result['web_search']}")
```

### Ejemplo 3: Usar Chains Individualmente

```python
from graph.chains.generation import generation_chain

# Generar respuesta con contexto manual
answer = generation_chain.invoke({
    "context": [
        "Los agentes de IA usan memoria para mantener contexto.",
        "Existen diferentes tipos de memoria en agentes."
    ],
    "question": "¿Qué es la memoria en agentes?"
})
print(answer)
```

### Ejemplo 4: Evaluar Documento

```python
from graph.chains.retrieval_grader import retrieval_grader_chain

result = retrieval_grader_chain.invoke({
    "document": "La inteligencia artificial ha evolucionado...",
    "question": "What is agent memory?"
})
print(f"Relevante: {result.binary_score}")
print(f"Razón: {result.reason}")
```

### Ejemplo 5: Verificar Alucinaciones

```python
from graph.chains.hallucination_grader import hallucination_grader_chain

result = hallucination_grader_chain.invoke({
    "documents": ["Los agentes usan memoria..."],
    "generation": "Los agentes de IA almacenan información en memoria persistente."
})
print(f"Fundamentada: {result.binary_score}")
```

