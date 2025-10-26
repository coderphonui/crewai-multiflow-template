"""
Root-level API router for execution management across all flows.
"""
from typing import Optional
from fastapi import APIRouter

from .common import ExecutionStatusResponse
from .execution_store import execution_store, ExecutionStatus


router = APIRouter()


@router.get("/executions", response_model=list[ExecutionStatusResponse])
async def list_executions(
    flow_name: Optional[str] = None,
    status: Optional[ExecutionStatus] = None,
    limit: int = 100
):
    """
    List all executions across all flows with optional filtering.
    
    Args:
        flow_name: Filter by specific flow name (optional)
        status: Filter by execution status (optional)
        limit: Maximum number of records to return (default: 100)
        
    Returns:
        List of execution records
    """
    records = execution_store.list_executions(
        flow_name=flow_name,
        status=status,
        limit=limit
    )
    
    # Convert to response models
    responses = []
    for record in records:
        responses.append(
            ExecutionStatusResponse(
                execution_id=record.execution_id,
                flow_name=record.flow_name,
                status=record.status,
                created_at=record.created_at,
                started_at=record.started_at,
                completed_at=record.completed_at,
                result=record.result,
                error=record.error
            )
        )
    
    return responses
