from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Order(Base):
    __tablename__ = "order"

    name: Mapped[str] = mapped_column(String(50), primary_key=True)
    username = Column(String(50))
    port = Column(Integer)
    polled_time = Column(Integer)
    metric: Mapped["Metric"] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
