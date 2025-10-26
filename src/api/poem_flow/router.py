"""
API router for poem_flow endpoints.
Handles flow execution and status retrieval without coupling the flow to FastAPI.
"""
import asyncio
from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks

from .models import (
    PoemFlowRequest,
    PoemResult
)
from ..common import ExecutionResponse, ExecutionStatusResponse
from ..execution_store import (
    execution_store,
    ExecutionStatus
)

# Import the flow - note that the flow itself has no FastAPI dependencies
from flows.poem_flow.main import PoemFlow


router = APIRouter()


def execute_flow(execution_id: str, sentence_count: Optional[int] = None):
    """
    Execute the poem flow in a background task.
    
    Args:
        execution_id: The execution ID to track
        sentence_count: Optional sentence count override
    """
    try:
        # Update status to running
        execution_store.update_status(execution_id, ExecutionStatus.RUNNING)
        
        # Create and execute the flow
        flow = PoemFlow()
        
        # Override sentence count if provided
        if sentence_count is not None:
            flow.state.sentence_count = sentence_count
        
        # Execute the flow
        flow.kickoff()
        
        # Extract results from the flow state
        result = PoemResult(
            sentence_count=flow.state.sentence_count,
            poem=flow.state.poem
        )
        
        # Update status to completed
        execution_store.update_status(
            execution_id,
            ExecutionStatus.COMPLETED,
            result=result.model_dump()
        )
        
    except Exception as e:
        # Update status to failed
        execution_store.update_status(
            execution_id,
            ExecutionStatus.FAILED,
            error=str(e)
        )


@router.post("/execute", response_model=ExecutionResponse)
async def trigger_poem_flow(
    request: PoemFlowRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger a poem flow execution.
    
    The flow will execute asynchronously in the background.
    Use the returned execution_id to check status and retrieve results.
    
    Args:
        request: Flow execution parameters
        background_tasks: FastAPI background tasks
        
    Returns:
        ExecutionResponse with execution_id and initial status
    """
    # Create execution record
    execution_id = execution_store.create_execution(
        flow_name="poem_flow",
        inputs=request.model_dump()
    )
    
    # Schedule flow execution in background
    background_tasks.add_task(
        execute_flow,
        execution_id,
        request.sentence_count
    )
    
    return ExecutionResponse(
        execution_id=execution_id,
        status=ExecutionStatus.PENDING,
        message=f"Poem flow execution initiated with ID: {execution_id}"
    )


@router.get("/execution/{execution_id}", response_model=ExecutionStatusResponse)
async def get_execution_status(execution_id: str):
    """
    Get the status and results of a flow execution.
    
    Args:
        execution_id: The execution ID
        
    Returns:
        ExecutionStatusResponse with current status and results (if completed)
        
    Raises:
        HTTPException: If execution_id is not found
    """
    record = execution_store.get_execution(execution_id)
    
    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"Execution {execution_id} not found"
        )
    
    # Convert result dict back to PoemResult if available
    result = None
    if record.result:
        result = PoemResult(**record.result)
    
    return ExecutionStatusResponse(
        execution_id=record.execution_id,
        flow_name=record.flow_name,
        status=record.status,
        created_at=record.created_at,
        started_at=record.started_at,
        completed_at=record.completed_at,
        result=result,
        error=record.error
    )
