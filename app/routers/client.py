from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.metric import Metric
from app.models.order import Order
from app.schemas.client import MetricData, MetricResponse, OrderResponse
from app.utils.time_utils import get_time

router = APIRouter(prefix="/client", tags=["client"])


@router.get("/order", response_model=OrderResponse)
async def get_protected_data(
    request: Request, db_session: AsyncSession = Depends(get_db_session)
) -> OrderResponse:
    name = request.headers.get("name")
    username = request.headers.get("username")

    if not name:
        raise HTTPException(status_code=401, detail="Authentication required")

    resp = OrderResponse()

    if order := await db_session.get(Order, name):
        if order.port:
            resp.port = order.port
        order.polled_time = int(get_time())
        order.username = username
    else:
        record = Order(name=name, polled_time=int(get_time()), username=username)
        db_session.add(record)
    await db_session.commit()

    return resp


@router.put("/metric", response_model=MetricResponse)
async def update_metric(
    request: Request,
    metric_data: MetricData,
    db_session: AsyncSession = Depends(get_db_session),
) -> MetricResponse:
    name = request.headers.get("name")
    order = await db_session.get(Order, name)
    if name is None or order is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    metric_query = select(Metric).where(Metric.name == name)
    result = await db_session.execute(metric_query)
    metric = result.scalar_one_or_none()

    if metric is None:
        metric = Metric()
        metric.name = name
        db_session.add(metric)

    metric.cpu_usage = int(metric_data.cpu_usage)
    metric.memory_usage = int(metric_data.memory_usage)
    metric.disk_usage = int(metric_data.disk_usage)
    metric.temperature = int(metric_data.temperature)
    metric.uptime = int(metric_data.uptime)

    await db_session.commit()

    return MetricResponse(message="Metric updated successfully")
