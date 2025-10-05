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

    orders_result = await db_session.execute(select(Order).order_by(Order.name))
    orders = orders_result.scalars().all()
    for order in orders:
        resp_item = ManageDataResponseItem(
            name=order.name,
            polled_time=float(order.polled_time)
            if order.polled_time is not None
            else 0.0,
        )
        metric_result = await db_session.execute(
            select(Metric).where(Metric.name == order.name)
        )
        if metric := metric_result.scalars().first():
            resp_item.uptime = metric.uptime
            resp_item.cpu_usage = metric.cpu_usage
            resp_item.memory_usage = metric.memory_usage
            resp_item.disk_usage = metric.disk_usage
            resp_item.temperature = metric.temperature
        resp.data.append(resp_item)

    return JSONResponse(resp.model_dump())


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
    forwarder_id, forwarder_start = await forwarder_manager.create_forwarder(body.name)
    background_tasks.add_task(
        forwarder_start, forwarder_id, forwarder_manager.forwarders
    )
    return ManageConnectResponse(forwarder_id=forwarder_id)


@router.get("/forwarder/{forwarder_id}")
async def forwarder_status(
    forwarder_id: str, _: User = Depends(manager)
) -> StreamingResponse:
    if not forwarder_manager.is_forwarder_running(forwarder_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Forwarder not found"
        )

    return StreamingResponse(
        forwarder_manager.get_forwarder_responses(forwarder_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.delete("/forwarder/{forwarder_id}", response_model=ManageDeleteDataResponse)
async def cancel_forward_job(
    forwarder_id: str, _: User = Depends(manager)
) -> ManageDeleteDataResponse:
    if forwarder_manager.cancel_forwarder(forwarder_id):
        return ManageDeleteDataResponse(message="Forwarder cancelled successfully")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Forwarder not found"
    )
