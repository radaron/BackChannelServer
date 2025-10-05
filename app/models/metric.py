from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.order import Order


class Metric(Base):
    __tablename__ = "metric"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        ForeignKey("order.name", ondelete="CASCADE", onupdate="CASCADE")
    )
    order: Mapped["Order"] = relationship(back_populates="metric")
    uptime: Mapped[Optional[int]] = mapped_column(Integer)
    cpu_usage: Mapped[Optional[int]] = mapped_column(Integer)
    memory_usage: Mapped[Optional[int]] = mapped_column(Integer)
    disk_usage: Mapped[Optional[int]] = mapped_column(Integer)
    temperature: Mapped[Optional[int]] = mapped_column(Integer)
