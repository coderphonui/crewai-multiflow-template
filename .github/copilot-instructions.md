## Purpose

This project is a multi-flow CrewAI-based application.

## Quick start (commands)

- Python: required 3.10 ≤ py < 3.13 (see `pyproject.toml`).
- Install uv and project deps: `pip install uv` then (optional) `crewai install`.
- Install required packages: `pip install python-dotenv` and `pip install "crewai[tools]>=0.114.0,<1.0.0"`
- For API functionality: `pip install fastapi uvicorn[standard]`
- Set LLM API key: add `GEMINI_API_KEY=your_key` to a `.env` file in the project root.
- Run flows from the repo root: `python run_flow.py <flow_name> [command]`
  - Example: `python run_flow.py poem_flow` or `python run_flow.py poem_flow kickoff`
  - The runner automatically loads `.env` and sets up Python paths
- Run API server: `python run_api.py` (default: http://127.0.0.1:8000)
  - With custom settings: `python run_api.py --host 0.0.0.0 --port 8080 --reload`
  - API docs available at `/docs` and `/redoc`

## Big-picture architecture

- This repo is a crewAI-based multi-agent project with support for multiple flows. The runtime is organized around:
  - Flows: each flow lives in `src/flows/<flow_name>/` (e.g., `src/flows/poem_flow/main.py` defines `PoemFlow`)
  - Crews: each flow has its own crews in `src/flows/<flow_name>/crews/` (e.g., `poem_crew.py` defines `PoemCrew` using `@CrewBase`)
  - Agents & Tasks: configured by YAML under each crew's `config/` directory (`agents.yaml` and `tasks.yaml`)
  - Tools: shared tools live under `src/shared/tools/` (available across all flows)
  - Runner: `run_flow.py` at project root handles Python path setup and flow execution
  - API Layer: `src/api/` contains FastAPI integration (flow-independent)
    - Core: `app.py` (FastAPI setup), `execution_store.py` (execution tracking)
    - Flow-specific: `src/api/<flow_name>/` with `models.py` (Pydantic schemas) and `router.py` (endpoints)
    - API runner: `run_api.py` at project root starts the FastAPI server

- Data flow example: `PoemFlow.generate_poem` calls
  `PoemCrew().crew().kickoff(inputs={"sentence_count": ...})` and stores the returned `result.raw` into `poem.txt`.

- API flow example: POST to `/api/v1/poem-flow/execute` triggers background execution via `execution_store`, 
  returns `execution_id` immediately, client polls `/api/v1/poem-flow/execution/{execution_id}` for status/result.

## Project-specific conventions and patterns

- YAML-driven agent/task configuration: agent and task behavior (role, goal, llm, expected_output) comes from YAML keys referenced by `agents_config` and `tasks_config`.
  - Example: `agents_config = "config/agents.yaml"` then `Agent(config=self.agents_config["poem_writer"])`.
- Decorator wiring: use `@agent`, `@task`, and `@crew` on methods inside `@CrewBase` classes to auto-create runtime objects.
- Crew process default: `Process.sequential` is used in the example crew—expect synchronous task ordering unless changed.
- Tools implement `crewai.tools.BaseTool` with a Pydantic `args_schema` (see `MyCustomTool` in `tools/custom_tool.py`).

## Integration points & external dependencies

- Primary runtime: `crewai` package (Flow, Crew, Agent, Task, Process, tools). Look at imports in `main.py` and `poem_crew.py`.
- LLM provider: YAML may specify `llm: gemini/gemini-2.5-flash` — ensure credentials (GEMINI_API_KEY) and provider-specific config are present when running.
- API layer: `fastapi` and `uvicorn` for REST API exposure of flows. All API integration lives in `src/api/` keeping flows independent.
- Execution tracking: `execution_store` manages async flow execution state (pending, running, completed, failed) with in-memory storage.

## Examples the assistant may produce or modify

- To add a new flow: create directory `src/flows/<new_flow_name>/` with `main.py`, crews, and config following the `poem_flow` pattern
- To add an agent that uses a tool: add tool class in `src/shared/tools/`, update the flow's `agents.yaml`, and add an `@agent` factory method in the crew class
- To change outputs: modify the flow's save method (e.g., `PoemFlow.save_poem` writes `poem.txt` at repo root)
- To expose a flow via API: create `src/api/<flow_name>/` with `models.py` (Pydantic request/response), `router.py` (endpoints), and register router in `src/api/app.py`
- API endpoint pattern: POST `/api/v1/<flow-name>/execute` triggers async execution, GET `/api/v1/<flow-name>/execution/{id}` checks status

## Files worth checking when making edits

- `run_flow.py` — Flow runner with Python path setup and `.env` loading for executing flows from project root
- `run_api.py` — API server runner for exposing flows via REST endpoints
- `src/flows/<flow_name>/main.py` — Flow orchestrator and entry points (`kickoff`, `plot`)
- `src/flows/<flow_name>/crews/<crew_name>/<crew_name>.py` — crew declaration, agent/task factories
- `src/flows/<flow_name>/crews/<crew_name>/config/agents.yaml` and `tasks.yaml` — authoritative agent/task definitions
- `src/shared/tools/` — shared custom tools implementation and schemas
- `src/api/app.py` — FastAPI application setup and router registration
- `src/api/execution_store.py` — Execution tracking and status management
- `src/api/<flow_name>/models.py` — Pydantic request/response models for API endpoints
- `src/api/<flow_name>/router.py` — API endpoints for specific flow
- `.env` — environment variables (API keys) loaded automatically by `run_flow.py`

## Constraints & non-obvious details

- Many runtime objects are created dynamically by decorators and YAML lookups. When editing, change both code and YAML consistently.
- `python run_flow.py <flow_name>` is the recommended entry point for running flows from the project root
- The `run_flow.py` script automatically loads `.env` file and sets up Python paths
- Each flow is self-contained in `src/flows/<flow_name>/` with its own crews and configuration
- API keys should be stored in `.env` file at project root (not committed to git)

## Merge guidance (if updating this file)

- Preserve the Quick start commands and any project-specific environment hints (Python range, GEMINI_API_KEY).
- Keep concrete file references; avoid adding generic policy or style rules that aren't discoverable in code.

---
