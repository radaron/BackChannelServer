import asyncio
import json
from typing import AsyncGenerator
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from app.services.task_manager import task_manager, TaskResult
from app.schemas.task import TaskEventData
import logging

logger = logging.getLogger(__name__)


class SSEService:
    """Service for handling Server-Sent Events"""

    @staticmethod
    def format_sse_data(event_type: str, data: dict) -> str:
        """Format data for SSE transmission"""
        return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

    @staticmethod
    async def task_status_stream(task_id: str) -> AsyncGenerator[str, None]:
        """
        Generate SSE stream for task status updates
        """
        try:
            # Check if task exists
            task_result = task_manager.get_task_status(task_id)
            if not task_result:
                raise HTTPException(status_code=404, detail="Task not found")

            # Send initial status
            event_data = TaskEventData(
                task_id=task_result.task_id,
                status=task_result.status,
                progress=task_result.progress,
                message=task_result.message,
                result=task_result.result,
                error=task_result.error
            )

            yield SSEService.format_sse_data("task_status", event_data.model_dump())

            # If task is already completed, send final event and return
            if task_result.status.value in ["completed", "failed", "cancelled"]:
                yield SSEService.format_sse_data("task_complete", {
                    "task_id": task_id,
                    "final_status": task_result.status.value
                })
                return

            # Get task update queue
            update_queue = await task_manager.get_task_updates(task_id)
            if not update_queue:
                yield SSEService.format_sse_data("error", {
                    "message": "Unable to get task updates"
                })
                return

            # Stream updates
            while True:
                try:
                    # Wait for updates with timeout
                    task_update = await asyncio.wait_for(update_queue.get(), timeout=30.0)

                    # Send update
                    event_data = TaskEventData(
                        task_id=task_update.task_id,
                        status=task_update.status,
                        progress=task_update.progress,
                        message=task_update.message,
                        result=task_update.result,
                        error=task_update.error
                    )

                    yield SSEService.format_sse_data("task_status", event_data.model_dump())

                    # If task is completed, send final event and break
                    if task_update.status.value in ["completed", "failed", "cancelled"]:
                        yield SSEService.format_sse_data("task_complete", {
                            "task_id": task_id,
                            "final_status": task_update.status.value
                        })
                        break

                except asyncio.TimeoutError:
                    # Send heartbeat to keep connection alive
                    yield SSEService.format_sse_data("heartbeat", {
                        "timestamp": str(asyncio.get_event_loop().time())
                    })
                    continue

        except asyncio.CancelledError:
            logger.info("SSE stream cancelled for task %s", task_id)
            yield SSEService.format_sse_data("connection_closed", {
                "task_id": task_id,
                "message": "Connection closed"
            })
        except Exception as e:
            logger.error("Error in SSE stream for task %s: %s", task_id, str(e))
            yield SSEService.format_sse_data("error", {
                "task_id": task_id,
                "message": f"Stream error: {str(e)}"
            })

    @staticmethod
    def create_sse_response(task_id: str) -> StreamingResponse:
        """Create a StreamingResponse for SSE"""
        return StreamingResponse(
            SSEService.task_status_stream(task_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control",
            }
        )


# Example of how to use with different task types
TASK_REGISTRY = {
    "long_running": {
        "function": "example_long_running_task",
        "description": "A long running task that takes specified duration"
    },
    "data_processing": {
        "function": "example_data_processing_task",
        "description": "Process a specified number of data items"
    }
}