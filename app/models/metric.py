from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Metric(Base):
    __tablename__ = "metric"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        ForeignKey("order.name", ondelete="CASCADE", onupdate="CASCADE")
    )
    order: Mapped["Order"] = relationship(back_populates="metric")
    uptime = Column(Integer)
    cpu_usage = Column(Integer)
    memory_usage = Column(Integer)
    disk_usage = Column(Integer)
    temperature = Column(Integer)
