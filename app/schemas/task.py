from datetime import datetime
from typing import Optional, Any, List
from pydantic import BaseModel, Field
from app.services.task_manager import TaskStatus


class TaskCreate(BaseModel):
    name: str = Field(..., description="Name of the task to execute")
    task_type: str = Field(..., description="Type of task (e.g., 'data_processing', 'long_running')")
    parameters: Optional[dict] = Field(default=None, description="Task parameters")


class TaskResponse(BaseModel):
    task_id: str = Field(..., description="Unique task identifier")
    name: str = Field(..., description="Task name")
    status: TaskStatus = Field(..., description="Current task status")
    progress: int = Field(default=0, ge=0, le=100, description="Task progress percentage")
    message: str = Field(default="", description="Current status message")
    result: Optional[Any] = Field(default=None, description="Task result when completed")
    error: Optional[str] = Field(default=None, description="Error message if task failed")
    created_at: datetime = Field(..., description="Task creation timestamp")
    started_at: Optional[datetime] = Field(default=None, description="Task start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Task completion timestamp")

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse] = Field(..., description="List of tasks")


class TaskEventData(BaseModel):
    """Data structure for Server-Sent Events"""
    task_id: str
    status: TaskStatus
    progress: int
    message: str
    result: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TaskCancelResponse(BaseModel):
    task_id: str
    message: str
    cancelled: bool