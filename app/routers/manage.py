from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import User, manager
from app.models.metric import Metric
from app.models.order import Order
from app.schemas.manage import (
    ManageConnectData,
    ManageConnectResponse,
    ManageDataResponse,
    ManageDataResponseItem,
    ManageDeleteData,
    ManageDeleteDataResponse,
)
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
        resp_item = ManageDataResponseItem(
            name=order.name, polled_time=order.polled_time
        )
        if metric := await db_session.execute(
            select(Metric).where(Metric.name == order.name)
        ):
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
    data: ManageDeleteData,
    _: User = Depends(manager),
    db_session: AsyncSession = Depends(get_db_session),
) -> ManageDeleteDataResponse:
    order = await db_session.get(Order, data.name)
    if order:
        await db_session.delete(order)
        await db_session.commit()
        return ManageDeleteDataResponse(
            message=f"Data for '{data.name}' deleted successfully"
        )

    return ManageDeleteDataResponse(message="No data found to delete")


@router.post("/connect")
async def initiate_connection(
    body: ManageConnectData,
    background_tasks: BackgroundTasks,
    _: User = Depends(manager),
) -> ManageConnectResponse:
    job_id, forwarder_start = await forwarder_manager.create_job(body.name)
    background_tasks.add_task(forwarder_start, job_id, forwarder_manager.jobs)
    return ManageConnectResponse(job_id=job_id)


@router.get("/forwarder/{job_id}")
async def forward_job_status(
    job_id: str, _: User = Depends(manager)
) -> StreamingResponse:
    if not forwarder_manager.is_job_running(job_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    return StreamingResponse(
        forwarder_manager.get_job_updates(job_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.delete("/forwarder/{job_id}", response_model=ManageDeleteDataResponse)
async def cancel_forward_job(
    job_id: str, _: User = Depends(manager)
) -> ManageDeleteDataResponse:
    if forwarder_manager.cancel_job(job_id):
        return ManageDeleteDataResponse(message="Job cancelled successfully")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
