from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.core.security import User, manager
from app.models.order import Order
from app.models.metric import Metric
from app.schemas.manage import ManageDataResponse, ManageDataResponseItem, ManageDeleteDataResponse, ManageDeleteData

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
