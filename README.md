# CrewAI multi flow project

A multi-flow CrewAI project as a template.

## Project Structure

```
<project-root>/
├── run_flow.py              # Main entry point for running flows
├── run_api.py               # API server for exposing flows via REST
├── examples/
│   └── api_usage.py         # Example API client usage
├── src/
│   ├── api/                 # FastAPI integration (flow-independent)
│   │   ├── app.py           # FastAPI app setup
│   │   ├── execution_store.py  # Execution tracking
│   │   └── <flow_name>/     # Flow-specific API integration
│   │       ├── models.py    # Request/Response models
│   │       └── router.py    # API endpoints
│   ├── flows/               # Individual flow implementations
│   │   └── poem_flow/       # Example: Poem generation flow
│   │       ├── main.py      # Flow definition
│   │       └── crews/       # Flow-specific crews
│   │           └── poem_crew/
│   │               ├── poem_crew.py
│   │               └── config/
│   │                   ├── agents.yaml
│   │                   └── tasks.yaml
│   └── shared/
│       └── tools/           # Shared tools across flows
└── pyproject.toml

```

## Installation

Ensure you have Python >=3.10 <3.13 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```

Or install with pip:
```bash
pip install python-dotenv
pip install "crewai[tools]>=0.114.0,<1.0.0"
pip install fastapi uvicorn[standard]  # For API functionality
```

### Environment Setup

This project is based mainly on Google Gemini, but it's not the limitation. You can freely add more LLM depends on your flow.

**Create a `.env` file in the project root and add your API keys:**

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

The `run_flow.py` script automatically loads environment variables from the `.env` file when running flows.

### Customizing

- Each flow has its own agents and tasks defined in `src/flows/<flow_name>/crews/<crew_name>/config/`
- Modify `agents.yaml` to define your agents for each crew
- Modify `tasks.yaml` to define your tasks for each crew
- Shared tools can be added to `src/shared/tools/`

## Running the Project

To run a flow, use the `run_flow.py` script from the root folder. The script automatically:
- Sets up the Python path correctly
- Loads environment variables from `.env` file
- Executes the specified flow

```bash
python run_flow.py <flow_name> [command]
```

Examples:
```bash
# Run the poem flow (default command is 'kickoff')
python run_flow.py poem_flow

# Explicitly run kickoff
python run_flow.py poem_flow kickoff

# Generate flow diagram
python run_flow.py poem_flow plot
```

List available flows:
```bash
python run_flow.py
```

## Running the API Server

To expose flows through REST API:

```bash
# Start the API server (default: http://127.0.0.1:8000)
python run_api.py

# Custom host and port
python run_api.py --host 0.0.0.0 --port 8080

# Development mode with auto-reload
python run_api.py --reload
```

Once running, access:
- **API Documentation**: http://127.0.0.1:8000/docs
- **Alternative Docs**: http://127.0.0.1:8000/redoc

### API Usage Example

```bash
# 1. Trigger a flow execution
curl -X POST "http://127.0.0.1:8000/api/v1/poem-flow/execute" \
  -H "Content-Type: application/json" \
  -d '{"sentence_count": 3}'

# Response: {"execution_id": "...", "status": "pending", ...}

# 2. Check execution status
curl "http://127.0.0.1:8000/api/v1/poem-flow/execution/{execution_id}"

# 3. List all executions
curl "http://127.0.0.1:8000/api/v1/poem-flow/executions"
```

Or use the Python example client:
```bash
python examples/api_usage.py
```

For complete API documentation, see [`src/api/README.md`](src/api/README.md).

## Adding a New Flow

1. Create a new directory under `src/flows/`:
```bash
mkdir -p src/flows/my_new_flow/crews/my_crew/config
```

2. Create `src/flows/my_new_flow/main.py` with your flow definition:
```python
from crewai.flow import Flow, listen, start
from .crews.my_crew.my_crew import MyCrew

class MyNewFlow(Flow):
    # Your flow implementation
    pass

def kickoff():
    flow = MyNewFlow()
    flow.kickoff()
```

3. Create your crew in `src/flows/my_new_flow/crews/my_crew/my_crew.py`

4. Configure agents and tasks in YAML files under `config/`

5. Run your new flow:
```bash
python run_flow.py my_new_flow
```

## Exposing Flows via API

To expose a flow through REST API, create an API integration module:

### 1. Create API Module Structure

```bash
mkdir -p src/api/my_new_flow
touch src/api/my_new_flow/__init__.py
touch src/api/my_new_flow/models.py
touch src/api/my_new_flow/router.py
```

### 2. Define Request/Response Models (`models.py`)

```python
from pydantic import BaseModel, Field
from typing import Optional

class MyFlowRequest(BaseModel):
    """Request parameters for the flow."""
    param1: str = Field(..., description="Parameter 1")
    param2: int = Field(default=10, ge=1, le=100)

class MyFlowResult(BaseModel):
    """Result structure."""
    output: str
```

### 3. Create API Router (`router.py`)

```python
from fastapi import APIRouter, BackgroundTasks
from flows.my_new_flow.main import MyNewFlow
from ..execution_store import execution_store, ExecutionStatus
from .models import MyFlowRequest, MyFlowResult

router = APIRouter()

def execute_flow(execution_id: str, **params):
    try:
        execution_store.update_status(execution_id, ExecutionStatus.RUNNING)
        flow = MyNewFlow()
        flow.kickoff()
        result = MyFlowResult(output=flow.state.output).model_dump()
        execution_store.update_status(
            execution_id, ExecutionStatus.COMPLETED, result=result
        )
    except Exception as e:
        execution_store.update_status(
            execution_id, ExecutionStatus.FAILED, error=str(e)
        )

@router.post("/execute")
async def trigger_flow(request: MyFlowRequest, background_tasks: BackgroundTasks):
    execution_id = execution_store.create_execution(
        flow_name="my_new_flow", inputs=request.model_dump()
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

### 4. Register Router in `src/api/app.py`

```python
from .my_new_flow import router as my_new_flow_router

app.include_router(
    my_new_flow_router,
    prefix="/api/v1/my-new-flow",
    tags=["my-new-flow"]
)
```

The flow remains independent of FastAPI—all API integration lives in `src/api/`.

## Understanding Your Flows

Each flow in this project is self-contained with its own crews, agents, and tasks. Agents collaborate on tasks defined in their respective `config/tasks.yaml` files, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent.

