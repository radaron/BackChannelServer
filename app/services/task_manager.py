import asyncio
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any, Callable, Awaitable
from dataclasses import dataclass
from asyncio import Queue
import logging

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskResult:
    task_id: str
    status: TaskStatus
    name: str = "Generic Task"
    progress: int = 0
    message: str = ""
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, TaskResult] = {}
        self.task_queues: Dict[str, Queue] = {}
        self._running_tasks: Dict[str, asyncio.Task] = {}

    async def create_task(
        self,
        task_func: Callable[..., Awaitable[Any]],
        *args,
        task_name: str = "Generic Task",
        **kwargs
    ) -> str:
        """Create and start a new background task"""
        task_id = str(uuid.uuid4())

        # Create task result
        task_result = TaskResult(
            task_id=task_id,
            name=task_name,
            status=TaskStatus.PENDING,
            message=f"Task '{task_name}' created"
        )

        # Store task result
        self.tasks[task_id] = task_result

        # Create event queue for this task
        self.task_queues[task_id] = Queue()

        # Start the task
        asyncio_task = asyncio.create_task(
            self._run_task(task_id, task_func, task_name, args, kwargs)
        )
        self._running_tasks[task_id] = asyncio_task

        logger.info("Created task %s: %s", task_id, task_name)
        return task_id

    async def _run_task(
        self,
        task_id: str,
        task_func: Callable[..., Awaitable[Any]],
        task_name: str,
        args: tuple,
        kwargs: dict
    ):
        """Internal method to run the task and handle status updates"""
        try:
            # Update to running
            await self._update_task_status(
                task_id,
                TaskStatus.RUNNING,
                message=f"Task '{task_name}' started",
                started_at=datetime.utcnow()
            )

            # Run the actual task function
            result = await task_func(self._get_progress_callback(task_id), *args, **kwargs)

            # Mark as completed
            await self._update_task_status(
                task_id,
                TaskStatus.COMPLETED,
                message=f"Task '{task_name}' completed successfully",
                result=result,
                progress=100,
                completed_at=datetime.utcnow()
            )

        except asyncio.CancelledError:
            await self._update_task_status(
                task_id,
                TaskStatus.CANCELLED,
                message=f"Task '{task_name}' was cancelled",
                completed_at=datetime.utcnow()
            )
        except Exception as e:
            logger.error("Task %s failed: %s", task_id, str(e))
            await self._update_task_status(
                task_id,
                TaskStatus.FAILED,
                message=f"Task '{task_name}' failed",
                error=str(e),
                completed_at=datetime.utcnow()
            )
        finally:
            # Clean up
            if task_id in self._running_tasks:
                del self._running_tasks[task_id]

    def _get_progress_callback(self, task_id: str):
        """Get a progress callback function for the task"""
        async def update_progress(progress: int, message: str = ""):
            await self._update_task_progress(task_id, progress, message)
        return update_progress

    async def _update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        message: str = "",
        result: Any = None,
        error: str = None,
        progress: int = None,
        started_at: datetime = None,
        completed_at: datetime = None
    ):
        """Update task status and notify subscribers"""
        if task_id not in self.tasks:
            return

        task_result = self.tasks[task_id]
        task_result.status = status
        if message:
            task_result.message = message
        if result is not None:
            task_result.result = result
        if error:
            task_result.error = error
        if progress is not None:
            task_result.progress = progress
        if started_at:
            task_result.started_at = started_at
        if completed_at:
            task_result.completed_at = completed_at

        # Notify subscribers via queue
        if task_id in self.task_queues:
            await self.task_queues[task_id].put(task_result)

    async def _update_task_progress(self, task_id: str, progress: int, message: str = ""):
        """Update task progress"""
        if task_id not in self.tasks:
            return

        task_result = self.tasks[task_id]
        task_result.progress = max(0, min(100, progress))  # Clamp between 0-100
        if message:
            task_result.message = message

        # Notify subscribers
        if task_id in self.task_queues:
            await self.task_queues[task_id].put(task_result)

    def get_task_status(self, task_id: str) -> Optional[TaskResult]:
        """Get current status of a task"""
        return self.tasks.get(task_id)

    async def get_task_updates(self, task_id: str) -> Queue:
        """Get the queue for task updates (for SSE)"""
        if task_id not in self.task_queues:
            return None
        return self.task_queues[task_id]

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self._running_tasks:
            self._running_tasks[task_id].cancel()
            return True
        return False

    def list_tasks(self) -> Dict[str, TaskResult]:
        """List all tasks"""
        return self.tasks.copy()

    def cleanup_completed_tasks(self, max_age_minutes: int = 60):
        """Clean up old completed tasks"""
        current_time = datetime.utcnow()
        tasks_to_remove = []

        for task_id, task_result in self.tasks.items():
            if task_result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                if task_result.completed_at:
                    age_minutes = (current_time - task_result.completed_at).total_seconds() / 60
                    if age_minutes > max_age_minutes:
                        tasks_to_remove.append(task_id)

        for task_id in tasks_to_remove:
            del self.tasks[task_id]
            if task_id in self.task_queues:
                del self.task_queues[task_id]


# Global task manager instance
task_manager = TaskManager()


# Example task functions
async def example_long_running_task(progress_callback, duration: int = 10, name: str = "Example Task"):
    """Example long-running task that reports progress"""
    for i in range(duration):
        await asyncio.sleep(1)
        progress = int((i + 1) / duration * 100)
        await progress_callback(progress, f"{name}: Step {i + 1}/{duration}")

    return f"{name} completed after {duration} seconds"


async def example_data_processing_task(progress_callback, items_count: int = 100):
    """Example data processing task"""
    processed_items = []

    for i in range(items_count):
        # Simulate processing
        await asyncio.sleep(0.1)
        processed_items.append(f"item_{i}")

        # Report progress every 10 items
        if (i + 1) % 10 == 0:
            progress = int((i + 1) / items_count * 100)
            await progress_callback(progress, f"Processed {i + 1}/{items_count} items")

    return {"processed_count": len(processed_items), "items": processed_items}