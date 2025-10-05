from typing import TYPE_CHECKING, Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.metric import Metric


class Order(Base):
    __tablename__ = "order"

    name: Mapped[str] = mapped_column(String(50), primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(50))
    port: Mapped[Optional[int]] = mapped_column(Integer)
    polled_time: Mapped[Optional[int]] = mapped_column(Integer)
    metric: Mapped["Metric"] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
