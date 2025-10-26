# API Quick Start Guide

This guide will get you up and running with the CrewAI Flow API in 5 minutes.

## Prerequisites

- Python 3.10-3.12
- API keys configured in `.env` file

## Step 1: Install Dependencies

```bash
# Install all dependencies including FastAPI
pip install -e .

# Or manually
pip install fastapi uvicorn[standard] python-dotenv "crewai[tools]>=0.114.0,<1.0.0"
```

## Step 2: Configure Environment

Create `.env` in project root:

```env
GEMINI_API_KEY=your_api_key_here
```

## Step 3: Start the API Server

```bash
python run_api.py
```

You should see:
```
🚀 Starting CrewAI Flow API server...
   Host: 127.0.0.1
   Port: 8000
   
📖 API Documentation will be available at:
   http://127.0.0.1:8000/docs
```

## Step 4: Test the API

### Option A: Web Browser

Open http://127.0.0.1:8000/docs in your browser and use the interactive Swagger UI.

### Option B: Command Line

```bash
# Health check
curl http://127.0.0.1:8000/health

# Trigger poem generation
curl -X POST http://127.0.0.1:8000/api/v1/poem-flow/execute \
  -H "Content-Type: application/json" \
  -d '{"sentence_count": 3}'

# Copy the execution_id from response, then check status:
curl http://127.0.0.1:8000/api/v1/poem-flow/execution/YOUR_EXECUTION_ID
```

### Option C: Python Script

```bash
python examples/api_usage.py
```

## Step 5: Understand the Flow

1. **POST /api/v1/poem-flow/execute** - Triggers execution
   - Returns `execution_id` immediately
   - Flow runs in background
   
2. **GET /api/v1/poem-flow/execution/{id}** - Check status
   - `pending` → `running` → `completed` or `failed`
   - Results available when `completed`

3. **GET /api/v1/poem-flow/executions** - List all executions
   - Filter by status
   - Paginate with limit

## Common Issues

### "Import fastapi could not be resolved"

Install FastAPI:
```bash
pip install fastapi uvicorn[standard]
```

### "Connection refused"

Make sure the server is running:
```bash
python run_api.py
```

### "Execution timeout"

Long-running flows may take time. Check status periodically:
```bash
# Check every 5 seconds
watch -n 5 curl http://127.0.0.1:8000/api/v1/poem-flow/execution/YOUR_ID
```

## Next Steps

- Read the [full API documentation](README.md)
- Learn how to [add your own flow API](README.md#adding-a-new-flow-api)
- Explore the [Swagger UI](http://127.0.0.1:8000/docs) for all endpoints
- Check [main README](../README.md) for project overview

## Development Tips

**Auto-reload during development:**
```bash
python run_api.py --reload
```

**Custom port:**
```bash
python run_api.py --port 8080
```

**View logs:**
The server outputs logs directly to terminal. Watch for:
- Request logs (status codes, timing)
- Flow execution start/complete
- Any errors or exceptions

## Architecture Overview

```
Client Request
    ↓
FastAPI Endpoint (src/api/poem_flow/router.py)
    ↓
Background Task Scheduled
    ↓
Execution ID Returned (immediate response)
    ↓
Flow Executes (src/flows/poem_flow/main.py)
    ↓
Result Stored (src/api/execution_store.py)
    ↓
Client Polls Status
    ↓
Result Retrieved
```

**Key Design Principles:**
- ✅ Flows remain independent of FastAPI
- ✅ Async execution with tracking
- ✅ Modular structure (easy to add flows)
- ✅ In-memory storage (upgradable to persistent)
