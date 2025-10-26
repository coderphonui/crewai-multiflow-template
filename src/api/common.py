"""
Common models and utilities shared across all API flows.
"""
from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

from .execution_store import ExecutionStatus


class ExecutionResponse(BaseModel):
    """Response model for flow execution initiation."""
    execution_id: str = Field(..., description="Unique execution ID")
    status: ExecutionStatus = Field(..., description="Current execution status")
    message: str = Field(..., description="Human-readable message")


class ExecutionStatusResponse(BaseModel):
    """Response model for execution status queries (generic for all flows)."""
    execution_id: str = Field(..., description="Unique execution ID")
    flow_name: str = Field(..., description="Name of the flow")
    status: ExecutionStatus = Field(..., description="Current execution status")
    created_at: datetime = Field(..., description="When the execution was created")
    started_at: Optional[datetime] = Field(None, description="When the execution started")
    completed_at: Optional[datetime] = Field(None, description="When the execution completed")
    result: Optional[Any] = Field(None, description="Execution result (if completed), type depends on flow")
    error: Optional[str] = Field(None, description="Error message (if failed)")
