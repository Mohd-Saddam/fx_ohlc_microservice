"""
Pydantic schemas for request/response validation.

Provides type validation and serialization for API endpoints,
preventing invalid data from entering the system.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class TickCreate(BaseModel):
    """Schema for creating a new tick."""
    time: datetime
    symbol: str = Field(default="EURUSD", max_length=10)
    price: float = Field(gt=0, description="Price must be positive")


class TickUpdate(BaseModel):
    """Schema for updating a tick."""
    price: float = Field(gt=0, description="Updated price must be positive")


class TickResponse(BaseModel):
    """Schema for tick response."""
    model_config = ConfigDict(from_attributes=True)
    
    time: datetime
    symbol: str
    price: float


class OHLCResponse(BaseModel):
    """Schema for OHLC response."""
    model_config = ConfigDict(from_attributes=True)
    
    bucket: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    tick_count: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    database: str
    redis: str
    version: str


class WebSocketMessage(BaseModel):
    """WebSocket message schema."""
    type: str
    data: dict
    timestamp: datetime


class ConnectionStatsResponse(BaseModel):
    """WebSocket connection statistics."""
    connections: dict
    total: int
    timestamp: datetime