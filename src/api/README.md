# API for flow

REST API for executing and monitoring CrewAI flows.

## Architecture

The API is structured to keep flows decoupled from FastAPI:

```
src/api/
├── __init__.py              # API module initialization
├── app.py                   # FastAPI app setup and configuration
├── execution_store.py       # Execution tracking and storage
└── {flow_name}/             # Flow-specific API integration
    ├── __init__.py          # Exports router
    ├── models.py            # Request/Response models
    └── router.py            # API endpoints
```

### Design Principles

1. **Flow Independence**: Flows have no dependency on FastAPI. All API integration logic lives in `src/api/`.
2. **Execution Tracking**: Each flow execution gets a unique ID for async status monitoring.
3. **Modular Structure**: Each flow has its own API module with request/response models and endpoints.

## Quick Start

### Installation

```bash
# Install dependencies
pip install -e .

# Or manually install FastAPI and uvicorn
pip install fastapi uvicorn[standard]
```

### Running the API Server

```bash
# Start the server (default: http://127.0.0.1:8000)
python run_api.py

# Custom host and port
python run_api.py --host 0.0.0.0 --port 8080

# Development mode with auto-reload
python run_api.py --reload
```

### API Documentation

Once the server is running, access the interactive documentation:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Usage Examples

### 1. Trigger a Flow Execution

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/poem-flow/execute" \
  -H "Content-Type: application/json" \
  -d '{"sentence_count": 3}'
```

Response:
```json
{
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Poem flow execution initiated with ID: 550e8400-e29b-41d4-a716-446655440000"
}
```

### 2. Check Execution Status

```bash
curl "http://127.0.0.1:8000/api/v1/poem-flow/execution/550e8400-e29b-41d4-a716-446655440000"
```

Response (completed):
```json
{
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "flow_name": "poem_flow",
  "status": "completed",
  "created_at": "2025-10-26T10:30:00.000Z",
  "started_at": "2025-10-26T10:30:01.000Z",
  "completed_at": "2025-10-26T10:30:15.000Z",
  "result": {
    "sentence_count": 3,
    "poem": "Your generated poem here..."
  },
  "error": null
}
```

### 3. List All Executions

```bash
# Get all executions
curl "http://127.0.0.1:8000/api/v1/poem-flow/executions"

# Filter by status
curl "http://127.0.0.1:8000/api/v1/poem-flow/executions?status=completed"

# Limit results
curl "http://127.0.0.1:8000/api/v1/poem-flow/executions?limit=10"
```

## Execution Flow

1. **Client sends request** → API endpoint receives parameters
2. **Execution ID created** → Unique ID generated and stored
3. **Background task scheduled** → Flow executes asynchronously
4. **Status updated** → Progress tracked (pending → running → completed/failed)
5. **Client polls status** → Retrieve results using execution ID

### Execution States

- `pending`: Execution created, waiting to start
- `running`: Flow is currently executing
- `completed`: Flow finished successfully, results available
- `failed`: Flow encountered an error

## Adding a New Flow API

To expose a new flow through the API:

### 1. Create Flow API Module

Create `src/api/{flow_name}/`:

```
src/api/{flow_name}/
├── __init__.py          # Export router
├── models.py            # Request/Response models
└── router.py            # API endpoints
```

### 2. Define Models (`models.py`)

```python
from pydantic import BaseModel, Field
from ..execution_store import ExecutionStatus

class YourFlowRequest(BaseModel):
    """Request parameters for your flow."""
    param1: str = Field(..., description="Parameter description")
    param2: int = Field(default=10, ge=1, le=100)

class YourFlowResult(BaseModel):
    """Result structure for your flow."""
    output_field: str
    
class ExecutionStatusResponse(BaseModel):
    """Standard execution status response."""
    execution_id: str
    status: ExecutionStatus
    result: Optional[YourFlowResult] = None
    error: Optional[str] = None
```

### 3. Create Router (`router.py`)

```python
from fastapi import APIRouter, BackgroundTasks
from flows.{flow_name}.main import YourFlow
from ..execution_store import execution_store, ExecutionStatus

router = APIRouter()

def execute_flow(execution_id: str, **params):
    try:
        execution_store.update_status(execution_id, ExecutionStatus.RUNNING)
        
        flow = YourFlow()
        # Set parameters and execute
        flow.kickoff()
        
        # Extract and store results
        result = {"output_field": flow.state.output}
        execution_store.update_status(
            execution_id,
            ExecutionStatus.COMPLETED,
            result=result
        )
    except Exception as e:
        execution_store.update_status(
            execution_id,
            ExecutionStatus.FAILED,
            error=str(e)
        )

@router.post("/execute")
async def trigger_flow(request: YourFlowRequest, background_tasks: BackgroundTasks):
    execution_id = execution_store.create_execution(
        flow_name="your_flow",
        inputs=request.model_dump()
    )
    background_tasks.add_task(execute_flow, execution_id, **request.model_dump())
    return {"execution_id": execution_id, "status": "pending"}

@router.get("/execution/{execution_id}")
async def get_status(execution_id: str):
    record = execution_store.get_execution(execution_id)
    if not record:
        raise HTTPException(status_code=404, detail="Not found")
    return record
```

### 4. Register Router (`app.py`)

```python
from .{flow_name} import router as your_flow_router

app.include_router(
    your_flow_router,
    prefix="/api/v1/{flow-name}",
    tags=["{flow-name}"]
)
```

## Storage

Currently uses in-memory storage (`ExecutionStore`). For production:

- Replace with **Redis** for distributed caching
- Use **PostgreSQL/MongoDB** for persistent storage
- Implement **message queues** (Celery, RabbitMQ) for better task management

## Environment Variables

Create a `.env` file in the project root:

```env
# LLM API Keys
GEMINI_API_KEY=your_api_key_here
OPENAI_API_KEY=your_openai_key

# API Configuration (optional)
API_HOST=127.0.0.1
API_PORT=8000
```

## Testing

```bash
# Run with reload for development
python run_api.py --reload

# Test health endpoint
curl http://127.0.0.1:8000/health

# Test root endpoint
curl http://127.0.0.1:8000/
```

## Production Considerations

1. **Authentication**: Add API key or OAuth authentication
2. **Rate Limiting**: Implement request throttling
3. **Persistent Storage**: Replace in-memory store
4. **Task Queue**: Use Celery or similar for long-running tasks
5. **Monitoring**: Add logging and metrics (Prometheus, Grafana)
6. **Error Handling**: Implement comprehensive error responses
7. **CORS**: Configure appropriate origins for production
8. **Deployment**: Use Gunicorn/Uvicorn workers with proper configuration

## Troubleshooting

### Import Errors

If you see import errors, ensure you're running from the project root:
```bash
python run_api.py  # Not: cd src && python ../run_api.py
```

### Flow Not Found

Check that `sys.path` includes `src/`:
```python
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))
```

### Port Already in Use

Change the port:
```bash
python run_api.py --port 8001
```
