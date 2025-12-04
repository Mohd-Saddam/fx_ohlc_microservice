"""
SQLAlchemy models for FX tick data and OHLC aggregations.

Defines the tick table structure which TimescaleDB converts to a hypertable
for efficient time-series storage and querying.
"""
from sqlalchemy import (
    Column,
    String,
    Float,
    Index,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from app.database import Base


class Tick(Base):
    """
    Raw tick data model - TimescaleDB hypertable for time-series storage.
    
    Stores individual price updates at 1-second intervals. TimescaleDB
    automatically partitions by time for optimized queries and compression.
    """
    __tablename__ = "eurusd_ticks"
    
    time = Column(
        TIMESTAMP(timezone=True),
        primary_key=True,
        nullable=False,
        comment="Timestamp of the tick (primary key, partitioned by TimescaleDB)"
    )
    symbol = Column(
        String(10),
        primary_key=True,
        nullable=False,
        default="EURUSD",
        comment="Currency pair symbol"
    )
    price = Column(
        Float,
        nullable=False,
        comment="Price at this timestamp"
    )
    
    # Composite index for common query patterns
    __table_args__ = (
        Index('idx_symbol_time', 'symbol', 'time'),
        CheckConstraint('price > 0', name='positive_price'),
        {
            'comment': 'Raw FX tick data - converted to TimescaleDB hypertable'
        }
    )
    
    def __repr__(self):
        return f"<Tick(time={self.time}, symbol={self.symbol}, price={self.price})>"


# Note: OHLC aggregations are handled via TimescaleDB continuous aggregates
# These are created in timescale_setup.py after the hypertable is set up