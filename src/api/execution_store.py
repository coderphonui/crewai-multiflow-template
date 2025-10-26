"""
Execution tracking and storage for flow executions.
Stores execution results in-memory (can be extended to use persistent storage).
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any
from pydantic import BaseModel


class ExecutionStatus(str, Enum):
    """Status of a flow execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionRecord(BaseModel):
    """Record of a flow execution."""
    execution_id: str
    flow_name: str
    status: ExecutionStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    inputs: Dict[str, Any]
    result: Optional[Any] = None
    error: Optional[str] = None


class ExecutionStore:
    """
    In-memory store for flow execution records.
    
    In production, this should be replaced with a persistent storage solution
    (e.g., Redis, PostgreSQL, etc.)
    """
    
    def __init__(self):
        self._executions: Dict[str, ExecutionRecord] = {}
    
    def create_execution(
        self,
        flow_name: str,
        inputs: Dict[str, Any]
    ) -> str:
        """
        Create a new execution record.
        
        Args:
            flow_name: Name of the flow being executed
            inputs: Input parameters for the flow
            
        Returns:
            str: Unique execution ID
        """
        execution_id = str(uuid.uuid4())
        record = ExecutionRecord(
            execution_id=execution_id,
            flow_name=flow_name,
            status=ExecutionStatus.PENDING,
            created_at=datetime.now(),
            inputs=inputs
        )
        self._executions[execution_id] = record
        return execution_id
    
    def get_execution(self, execution_id: str) -> Optional[ExecutionRecord]:
        """
        Get an execution record by ID.
        
        Args:
            execution_id: The execution ID
            
        Returns:
            ExecutionRecord if found, None otherwise
        """
        return self._executions.get(execution_id)
    
    def update_status(
        self,
        execution_id: str,
        status: ExecutionStatus,
        result: Optional[Any] = None,
        error: Optional[str] = None
    ):
        """
        Update the status of an execution.
        
        Args:
            execution_id: The execution ID
            status: New status
            result: Execution result (for completed status)
            error: Error message (for failed status)
        """
        record = self._executions.get(execution_id)
        if not record:
            return
        
        record.status = status
        
        if status == ExecutionStatus.RUNNING and record.started_at is None:
            record.started_at = datetime.now()
        
        if status in (ExecutionStatus.COMPLETED, ExecutionStatus.FAILED):
            record.completed_at = datetime.now()
            if result is not None:
                record.result = result
            if error is not None:
                record.error = error
    
    def list_executions(
        self,
        flow_name: Optional[str] = None,
        status: Optional[ExecutionStatus] = None,
        limit: int = 100
    ) -> list[ExecutionRecord]:
        """
        List execution records with optional filters.
        
        Args:
            flow_name: Filter by flow name
            status: Filter by status
            limit: Maximum number of records to return
            
        Returns:
            List of execution records
        """
        executions = list(self._executions.values())
        
        if flow_name:
            executions = [e for e in executions if e.flow_name == flow_name]
        
        if status:
            executions = [e for e in executions if e.status == status]
        
        # Sort by created_at descending
        executions.sort(key=lambda e: e.created_at, reverse=True)
        
        return executions[:limit]


# Global execution store instance
execution_store = ExecutionStore()
