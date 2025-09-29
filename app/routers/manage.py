import asyncio
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.core.security import User, manager
from app.models.order import Order
from app.models.metric import Metric
from app.schemas.manage import (
    ManageDataResponse,
    ManageDataResponseItem,
    ManageDeleteDataResponse,
    ManageDeleteData,
    ManageConnectData,
    ManageConnectResponse,
)
from app.schemas.task import TaskCancelResponse
from app.services.task_manager import task_manager
from app.services.sse_service import SSEService
from app.services.forwarder import forwarder_manager


router = APIRouter(prefix="/manage", tags=["manage"])


@router.get("/data", response_model=ManageDataResponse)
async def get_all_orders(
    _: User = Depends(manager), db_session: AsyncSession = Depends(get_db_session)
) -> JSONResponse:

    resp = ManageDataResponse()

    orders = await db_session.execute(select(Order).order_by(Order.name))
    orders = orders.scalars().all()
    for order in orders:
        resp_item = ManageDataResponseItem(name=order.name, polled_time=order.polled_time)
        if metric := await db_session.execute(select(Metric).where(Metric.name == order.name)):
            metric = metric.scalars().first()
            resp_item.uptime = metric.uptime
            resp_item.cpu_usage = metric.cpu_usage
            resp_item.memory_usage = metric.memory_usage
            resp_item.disk_usage = metric.disk_usage
            resp_item.temperature = metric.temperature
        resp.data.append(resp_item)

    return JSONResponse(resp.model_dump_snake_case())


@router.delete("/data", response_model=ManageDeleteDataResponse)
async def delete_order_data(
    data: ManageDeleteData, _: User = Depends(manager), db_session: AsyncSession = Depends(get_db_session)
) -> ManageDeleteDataResponse:

    order = await db_session.get(Order, data.name)
    if order:
        await db_session.delete(order)
        await db_session.commit()
        return ManageDeleteDataResponse(message=f"Data for '{data.name}' deleted successfully")

    return JSONResponse(
        ManageDeleteDataResponse(message="No data found to delete").model_dump_snake_case(), status_code=204
    )


@router.post("/connect")
async def initiate_connection(
    body: ManageConnectData, background_tasks: BackgroundTasks, _: User = Depends(manager)
) -> ManageConnectResponse:
    job_id, forwarder_start = await forwarder_manager.create_job(body.name)
    background_tasks.add_task(forwarder_start, forwarder_manager.get_job(job_id))
    return ManageConnectResponse(job_id=job_id)


# @router.post("/tasks", response_model=TaskResponse)
# async def create_task(
#     task: TaskCreate,
#     _: User = Depends(manager)
# ) -> JSONResponse:
#     """Create and start a new background task"""

#     # Validate task type
#     if task.task_type not in TASK_REGISTRY:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Invalid task type. Available types: {list(TASK_REGISTRY.keys())}"
#         )

#     try:
#         # Get task function based on type
#         if task.task_type == "long_running":
#             duration = task.parameters.get("duration", 10) if task.parameters else 10
#             task_id = await task_manager.create_task(
#                 example_long_running_task,
#                 duration=duration,
#                 name=task.name,
#                 task_name=task.name
#             )
#         elif task.task_type == "data_processing":
#             items_count = task.parameters.get("items_count", 100) if task.parameters else 100
#             task_id = await task_manager.create_task(
#                 example_data_processing_task,
#                 items_count=items_count,
#                 task_name=task.name
#             )
#         else:
#             raise HTTPException(status_code=400, detail="Task type not implemented")

#         # Get initial task status
#         task_result = task_manager.get_task_status(task_id)
#         if not task_result:
#             raise HTTPException(status_code=500, detail="Failed to create task")

#         response = TaskResponse(
#             task_id=task_result.task_id,
#             name=task.name,
#             status=task_result.status,
#             progress=task_result.progress,
#             message=task_result.message,
#             result=task_result.result,
#             error=task_result.error,
#             created_at=task_result.created_at,
#             started_at=task_result.started_at,
#             completed_at=task_result.completed_at
#         )

#         return JSONResponse(response.model_dump(), status_code=201)

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


# @router.get("/tasks", response_model=TaskListResponse)
# async def list_tasks(_: User = Depends(manager)) -> JSONResponse:
#     """List all tasks"""

#     tasks = task_manager.list_tasks()
#     task_responses = []

#     for task_result in tasks.values():
#         task_responses.append(TaskResponse(
#             task_id=task_result.task_id,
#             name=task_result.name,
#             status=task_result.status,
#             progress=task_result.progress,
#             message=task_result.message,
#             result=task_result.result,
#             error=task_result.error,
#             created_at=task_result.created_at,
#             started_at=task_result.started_at,
#             completed_at=task_result.completed_at
#         ))

#     response = TaskListResponse(tasks=task_responses)
#     return JSONResponse(response.model_dump())


# @router.get("/tasks/{task_id}", response_model=TaskResponse)
# async def get_task_status(
#     task_id: str,
#     _: User = Depends(manager)
# ) -> JSONResponse:
#     """Get status of a specific task"""

#     task_result = task_manager.get_task_status(task_id)
#     if not task_result:
#         raise HTTPException(status_code=404, detail="Task not found")

#     response = TaskResponse(
#         task_id=task_result.task_id,
#         name=task_result.name,
#         status=task_result.status,
#         progress=task_result.progress,
#         message=task_result.message,
#         result=task_result.result,
#         error=task_result.error,
#         created_at=task_result.created_at,
#         started_at=task_result.started_at,
#         completed_at=task_result.completed_at
#     )

#     return JSONResponse(response.model_dump())


@router.get("/forwarder/{task_id}")
async def stream_task_status(task_id: str, _: User = Depends(manager)) -> StreamingResponse:
    """Stream task status updates via Server-Sent Events"""

    if not forwarder_manager.is_job_running(task_id):
        raise HTTPException(status_code=404, detail="Task not found")

    return StreamingResponse(
        forwarder_manager.get_job_updates(task_id),
    )

# @router.get("/tasks/types/available")
# async def get_available_task_types(_: User = Depends(manager)) -> JSONResponse:
#     """Get list of available task types"""

#     return JSONResponse({
#         "task_types": {
#             task_type: info["description"]
#             for task_type, info in TASK_REGISTRY.items()
#         }
#     })
