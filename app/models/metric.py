from sqlalchemy import Integer, Column, ForeignKey
from sqlalchemy.orm import (
    relationship,
    Mapped,
    mapped_column,
)

from app.core.database import Base


class Metric(Base):
    __tablename__ = 'metric'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        ForeignKey("order.name", ondelete='CASCADE', onupdate='CASCADE')
    )
    order: Mapped['Order'] = relationship(back_populates="metric")
    uptime = Column(Integer)
    cpu_usage = Column(Integer)
    memory_usage = Column(Integer)
    disk_usage = Column(Integer)
    temperature = Column(Integer)
