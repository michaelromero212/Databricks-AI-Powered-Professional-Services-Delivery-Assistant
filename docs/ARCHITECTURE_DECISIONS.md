# Architecture Decision Records

This document captures key technical decisions made during development of the PS Delivery Assistant.

---

## ADR-001: React + Vite over Streamlit

### Decision
Use React with Vite for the frontend instead of Python-based options like Streamlit or Dash.

### Context
We needed a frontend framework for an internal tools POC that could demonstrate enterprise-grade UI capabilities.

### Options Considered
| Option | Pros | Cons |
|--------|------|------|
| **React + Vite** | Full customization, industry standard, fast dev server | Separate from Python backend |
| **Streamlit** | Python-only, quick prototypes | Limited styling, not scalable |
| **Dash** | Python, Plotly integration | Complex for custom UIs |

### Rationale
- React skills are more transferable and demonstrate broader frontend capability
- Vite provides near-instant hot reload
- Custom design system shows UI/UX understanding
- Better separation of concerns between API and UI

---

## ADR-002: Hugging Face over OpenAI

### Decision
Use Hugging Face Inference API with Mistral-7B instead of OpenAI GPT.

### Context
The project requires LLM capabilities for generating insights from delivery data.

### Options Considered
| Option | Pros | Cons |
|--------|------|------|
| **Hugging Face** | Free tier, open models, no vendor lock-in | Less powerful than GPT-4 |
| **OpenAI** | Most capable models | Cost, API rate limits |
| **Local LLM** | Privacy, free | Hardware requirements |

### Rationale
- Free tier enables demo without cost concerns
- `huggingface_hub` SDK is well-maintained
- Mistral-7B-Instruct provides sufficient quality for PS insights
- Shows ability to work with open-source AI ecosystem

---

## ADR-003: FastAPI over Flask

### Decision
Use FastAPI as the backend framework.

### Context
Need a Python web framework for the REST API layer.

### Options Considered
| Option | Pros | Cons |
|--------|------|------|
| **FastAPI** | Async, auto-docs, type hints | Newer, less tutorials |
| **Flask** | Simple, mature | No async, manual docs |
| **Django** | Full-featured | Overkill for API-only |

### Rationale
- Automatic OpenAPI documentation (`/docs`)
- Native async support for LLM calls
- Pydantic models for request/response validation
- Modern Python typing
- Better performance under concurrent load

---

## ADR-004: Local JSON over SQLite for Demo

### Decision
Use JSON files for local data storage instead of a database.

### Context
The POC needs persistent storage that works without infrastructure setup.

### Rationale
- Zero setup required (no database installation)
- Human-readable data files
- Easy to generate sample data
- Mirrors production pattern (Delta tables are also file-based)
- Git-trackable sample datasets

### Trade-offs
- No query optimization
- Manual caching required
- Would need migration for production

---

## ADR-005: Unity Catalog Volumes over DBFS

### Decision
Use Unity Catalog Volumes for Databricks file storage.

### Context
Need to upload files to Databricks for notebook processing.

### Rationale
- DBFS is deprecated for new workloads
- Volumes work with Community Edition
- Better governance and permissions model
- Future-proof for Unity Catalog adoption

---

## ADR-006: Singleton Pattern for Clients

### Decision
Use singleton pattern for AI client and Databricks connector.

### Context
Multiple API endpoints need access to shared resources.

### Rationale
- Avoids reconnection overhead
- Single source of truth for configuration
- Simpler dependency management
- Memory efficient

### Implementation
```python
_client: Optional[AIClient] = None

def get_ai_client() -> AIClient:
    global _client
    if _client is None:
        _client = AIClient()
    return _client
```

---

## Future Considerations

- **State Management**: Add React Query for frontend caching
- **Authentication**: Add OAuth/JWT for production
- **Observability**: Add structured logging and tracing
- **Testing**: Expand test coverage to 80%+
