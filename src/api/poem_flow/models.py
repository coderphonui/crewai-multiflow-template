"""
Request and response models for poem_flow API.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from ..execution_store import ExecutionStatus


class PoemFlowRequest(BaseModel):
    """Request model for triggering poem flow execution."""
    sentence_count: Optional[int] = Field(
        None,
        ge=1,
        le=10,
        description="Number of sentences in the poem (1-10). If not provided, will be randomly generated."
    )


class ExecutionResponse(BaseModel):
    """Response model for flow execution initiation."""
    execution_id: str = Field(..., description="Unique execution ID")
    status: ExecutionStatus = Field(..., description="Current execution status")
    message: str = Field(..., description="Human-readable message")


class PoemResult(BaseModel):
    """Result data for a completed poem execution."""
    sentence_count: int = Field(..., description="Number of sentences in the poem")
    poem: str = Field(..., description="Generated poem text")


class ExecutionStatusResponse(BaseModel):
    """Response model for execution status queries."""
    execution_id: str = Field(..., description="Unique execution ID")
    flow_name: str = Field(..., description="Name of the flow")
    status: ExecutionStatus = Field(..., description="Current execution status")
    created_at: datetime = Field(..., description="When the execution was created")
    started_at: Optional[datetime] = Field(None, description="When the execution started")
    completed_at: Optional[datetime] = Field(None, description="When the execution completed")
    result: Optional[PoemResult] = Field(None, description="Execution result (if completed)")
    error: Optional[str] = Field(None, description="Error message (if failed)")
