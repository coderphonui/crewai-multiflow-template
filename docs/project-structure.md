# Project Structure - FastAPI Integration

```
crewai-multiflow-template/
│
├── run_flow.py                    # Run flows directly (existing)
├── run_api.py                     # Run API server (NEW)
│
├── examples/                      # (NEW)
│   └── api_usage.py              # Example API client
│
├── docs/                          # Documentation
│   ├── requirement.md            # (existing)
│   ├── API_QUICKSTART.md         # Quick start guide (NEW)
│   └── FASTAPI_IMPLEMENTATION.md # Implementation summary (NEW)
│
├── src/
│   ├── api/                      # ✨ FastAPI Integration (NEW)
│   │   ├── __init__.py           # API module
│   │   ├── app.py                # FastAPI app, CORS, routing
│   │   ├── execution_store.py   # Execution tracking system
│   │   ├── README.md             # Complete API documentation
│   │   │
│   │   └── poem_flow/            # Flow-specific API integration
│   │       ├── __init__.py       # Router export
│   │       ├── models.py         # Request/Response Pydantic models
│   │       └── router.py         # API endpoints (POST execute, GET status)
│   │
│   ├── flows/                    # Flow implementations (unchanged)
│   │   └── poem_flow/
│   │       ├── main.py           # Flow logic (NO FastAPI dependency)
│   │       └── crews/
│   │           └── poem_crew/
│   │               ├── poem_crew.py
│   │               └── config/
│   │                   ├── agents.yaml
│   │                   └── tasks.yaml
│   │
│   └── shared/                   # Shared utilities
│       └── tools/
│
├── pyproject.toml                # Dependencies (updated with FastAPI)
├── README.md                     # Project README (updated)
└── .env                          # Environment variables (API keys)
```

## Key Design Principles

### 1. **Separation of Concerns**
- ✅ Flows live in `src/flows/` with NO FastAPI dependencies
- ✅ API integration isolated in `src/api/`
- ✅ Each flow's API module in `src/api/{flow_name}/`

### 2. **Modular Structure**
```
src/api/{flow_name}/
├── __init__.py    → Export router
├── models.py      → Pydantic request/response models
└── router.py      → FastAPI endpoints
```

### 3. **Execution Tracking**
- Unique UUID per execution
- Status transitions: `pending` → `running` → `completed`/`failed`
- In-memory storage (upgradable to Redis/DB)

### 4. **Standard API Flow**
```
1. POST /execute      → Get execution_id (immediate)
2. Background Task    → Flow executes asynchronously
3. GET /execution/ID  → Poll status and retrieve results
```

## New Files Created

### Core Infrastructure (3 files)
- `src/api/app.py` - FastAPI app setup
- `src/api/execution_store.py` - Execution tracking
- `src/api/__init__.py` - Module init

### Poem Flow API (3 files)
- `src/api/poem_flow/router.py` - Endpoints
- `src/api/poem_flow/models.py` - Models
- `src/api/poem_flow/__init__.py` - Export

### Server & Examples (2 files)
- `run_api.py` - Server launcher
- `examples/api_usage.py` - Python client example

### Documentation (3 files)
- `src/api/README.md` - Complete guide
- `docs/API_QUICKSTART.md` - Quick setup
- `docs/FASTAPI_IMPLEMENTATION.md` - Summary

### Updates (2 files)
- `pyproject.toml` - Added dependencies
- `README.md` - Added API sections

**Total: 13 new/updated files**

## Quick Start

```bash
# 1. Install dependencies
pip install -e .

# 2. Start API server
python run_api.py

# 3. Test API
python examples/api_usage.py

# Or use curl
curl -X POST http://127.0.0.1:8000/api/v1/poem-flow/execute \
  -H "Content-Type: application/json" \
  -d '{"sentence_count": 3}'
```

## Adding New Flow API

For each new flow (e.g., `my_flow`):

1. Create `src/api/my_flow/` with `models.py` and `router.py`
2. Register in `src/api/app.py`
3. Flow code in `src/flows/my_flow/` stays unchanged
4. Zero FastAPI dependencies in flow logic

See `src/api/README.md` for complete guide.
