"""
Request and response models for poem_flow API.
"""
from typing import Optional
from pydantic import BaseModel, Field

from ..common import ExecutionResponse, ExecutionStatusResponse


class PoemFlowRequest(BaseModel):
    """Request model for triggering poem flow execution."""
    sentence_count: Optional[int] = Field(
        None,
        ge=1,
        le=10,
        description="Number of sentences in the poem (1-10). If not provided, will be randomly generated."
    )


class PoemResult(BaseModel):
    """Result data for a completed poem execution."""
    sentence_count: int = Field(..., description="Number of sentences in the poem")
    poem: str = Field(..., description="Generated poem text")
