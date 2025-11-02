# RAG System Integration

## Overview
This project now includes a **Retrieval-Augmented Generation (RAG)** system that provides contextual information to the AI agent, particularly for Paint-related operations.

## Architecture

### Components
1. **RAG.py**: The RAG module with document retrieval capabilities
2. **Perception.py**: Enhanced with RAG integration for context-aware input processing
3. **Decision_Making.py**: Enhanced to use RAG context in decision generation

### How It Works

#### 1. Document Store
The RAG system maintains a knowledge base of Paint-related instructions:
- **Opening Paint**: Instructions for launching Paint
- **Drawing Rectangles**: Coordinates and workflow for drawing
- **Adding Text**: How to insert text in Paint
- **Workflow**: Complete process flow
- **Turtle Graphics**: Alternative visualization method
- **Coordinates**: Toolbar positions and screen coordinates
- **Troubleshooting**: Common issues and solutions

#### 2. Document Retrieval
When a user query contains Paint-related keywords, the RAG system:
1. Analyzes the query for relevant keywords
2. Scores documents based on keyword matches
3. Retrieves top-k most relevant documents
4. Generates function recommendations

#### 3. Context Enhancement
Retrieved documents are added to the agent's context:
```
=== KNOWLEDGE BASE CONTEXT ===
**Title**: Content...
**Title2**: Content2...
```

## Usage Examples

### Example 1: Opening Paint
**Query**: "How do I open Paint application?"

**RAG Response**:
```
**Opening Paint**: To open Microsoft Paint application, use the open_paint_maximized 
function. This will open Paint in a maximized window. You must wait for Paint to 
fully load before attempting to draw or add text.

**Drawing Rectangles in Paint**: To draw a rectangle in Paint, first call 
open_paint_maximized. Then use draw_rectangle_paint function with coordinates 
(x1, y1, x2, y2)...

Recommended Functions: draw_rectangle_paint, add_text_in_paint, open_paint_maximized
```

### Example 2: Drawing in Paint
**Query**: "Can you help me draw a rectangle in Paint?"

**RAG Response**:
```
**Drawing Rectangles in Paint**: To draw a rectangle in Paint, first call 
open_paint_maximized. Then use draw_rectangle_paint function with coordinates...

**Opening Paint**: To open Microsoft Paint application...

**Paint Workflow**: Complete Paint workflow: 1) Call open_paint_maximized...

Recommended Functions: draw_rectangle_paint, add_text_in_paint, open_paint_maximized
```

### Example 3: Non-Paint Query
**Query**: "Find the ASCII values of characters in INDIA"

**RAG Response**: None (no Paint-related context added)

## Integration Points

### In Perception.py
```python
# RAG context is added automatically for Paint queries
if self.rag and ("paint" in user_query.lower() or "draw" in user_query.lower()):
    rag_context = self.rag.enhance_context(user_query)
    processed_input["rag_context"] = rag_context.get("context_summary")
    processed_input["rag_recommendations"] = self.rag.get_function_recommendations(user_query)
```

### In Decision_Making.py
```python
# RAG context is injected into the LLM prompt
if "rag_context" in perception_data and perception_data["rag_context"]:
    query_parts.append("\n\n=== KNOWLEDGE BASE CONTEXT ===")
    query_parts.append(perception_data["rag_context"])
```

## Testing

Run the test script to see RAG in action:
```bash
.venv\Scripts\python.exe test_rag_paint.py
```

This will test various Paint-related queries and show the RAG-enhanced context.

## Benefits

1. **Context-Aware**: Agent has access to Paint-specific instructions
2. **Function Recommendations**: Suggests relevant functions automatically
3. **Better Decision Making**: LLM receives structured knowledge
4. **Extensible**: Easy to add more documents to the knowledge base

## Future Enhancements

1. **Vector Embeddings**: Replace keyword matching with semantic embeddings
2. **Dynamic Documents**: Load documents from external sources
3. **Feedback Loop**: Learn from successful/failed operations
4. **Multi-Domain**: Extend beyond Paint to other operations

