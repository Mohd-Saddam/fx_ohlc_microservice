"""
Key Features:
- GET-only endpoints (no POST/PUT/DELETE)
- Queries TimescaleDB continuous aggregates
- Real-time data (materialized_only = false)
- Automatic refresh policies (5s, 30s, 5min)
- Zero-lag aggregation

CQRS Benefits:
- Read operations don't block writes
- Optimized queries (pre-aggregated data)
- Scalable (can add read replicas)
- Independent from write complexity

Data Flow:
1. Writes happen via Redis Pub/Sub or POST /ticks/
2. Data stored in eurusd_ticks hypertable
3. Continuous aggregates auto-refresh (5s, 30s, 5min)
4. These endpoints query aggregates (fast, pre-computed)
5. Real-time mode merges materialized + raw data (zero lag)
"""
import logging
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List
from app.database import get_db
from app.schemas import OHLCResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ohlc", tags=["OHLC (Read-Only Queries)"])


@router.get("/minute", response_model=List[OHLCResponse])
async def get_minute_ohlc(
    start: datetime = Query(..., description="Start time in UTC (ISO 8601)", example="2025-12-04T17:00:00Z"),
    end: datetime = Query(..., description="End time in UTC (ISO 8601)", example="2025-12-04T18:00:00Z"),
    symbol: str = Query("EURUSD", max_length=10),
    limit: int = Query(1000, ge=1, le=10000, description="Max number of rows to return (default: 1000, max: 10000)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get minute-level OHLC data from continuous aggregate.
    Real-time updates via TimescaleDB refresh policy (5s interval).
    
    **Time Range Limits**:
    - Maximum range: ~7 days (10,080 minutes)
    - Use pagination (limit) for large queries
    - All times must be in UTC timezone
    
    **Example**:
        GET /ohlc/minute?start=2025-12-04T17:00:00Z&end=2025-12-04T18:00:00Z&symbol=EURUSD
    """
    try:
        # Validate time range (max 7 days for minute data)
        time_diff = (end - start).total_seconds()
        max_minutes = 7 * 24 * 60  # 7 days in minutes
        if time_diff > max_minutes * 60:  # Convert to seconds
            raise HTTPException(
                status_code=400,
                detail=f"Time range too large. Maximum: 7 days ({max_minutes} minutes). Your range: {time_diff / 3600:.1f} hours"
            )
        
        stmt = text("""
            SELECT bucket, symbol, open, high, low, close, tick_count
            FROM eurusd_ohlc_minute
            WHERE bucket >= :start AND bucket < :end AND symbol = :symbol
            ORDER BY bucket ASC
            LIMIT :limit
        """)
        
        result = await db. execute(stmt, {"start": start, "end": end, "symbol": symbol, "limit": limit})
        rows = result.fetchall()
        
        return [
            OHLCResponse(
                bucket=row[0],
                symbol=row[1],
                open=row[2],
                high=row[3],
                low=row[4],
                close=row[5],
                tick_count=row[6]
            )
            for row in rows
        ]
    except Exception as e:
        logger. error(f"Error fetching minute OHLC: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router. get("/hour", response_model=List[OHLCResponse])
async def get_hourly_ohlc(
    start: datetime = Query(..., description="Start time in UTC (ISO 8601)", example="2025-12-03T00:00:00Z"),
    end: datetime = Query(..., description="End time in UTC (ISO 8601)", example="2025-12-04T23:00:00Z"),
    symbol: str = Query("EURUSD", max_length=10),
    limit: int = Query(1000, ge=1, le=10000, description="Max number of rows to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get hourly OHLC data from continuous aggregate. 
    Real-time updates via TimescaleDB refresh policy (30s interval).
    
    **Time Range Limits**:
    - Maximum range: 180 days (~4320 hours)
    - All times must be in UTC timezone
    
    **Example**:
        GET /ohlc/hour?start=2025-12-03T00:00:00Z&end=2025-12-04T00:00:00Z&symbol=EURUSD
    """
    try:
        # Validate time range (max 180 days for hourly data)
        time_diff = (end - start).total_seconds()
        max_hours = 180 * 24  # 180 days in hours
        if time_diff > max_hours * 3600:  # Convert to seconds
            raise HTTPException(
                status_code=400,
                detail=f"Time range too large. Maximum: 180 days ({max_hours} hours). Your range: {time_diff / 86400:.1f} days"
            )
        
        stmt = text("""
            SELECT bucket, symbol, open, high, low, close, tick_count
            FROM eurusd_ohlc_hour
            WHERE bucket >= :start AND bucket < :end AND symbol = :symbol
            ORDER BY bucket ASC
            LIMIT :limit
        """)
        
        result = await db.execute(stmt, {"start": start, "end": end, "symbol": symbol, "limit": limit})
        rows = result. fetchall()
        
        return [
            OHLCResponse(
                bucket=row[0],
                symbol=row[1],
                open=row[2],
                high=row[3],
                low=row[4],
                close=row[5],
                tick_count=row[6]
            )
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error fetching hourly OHLC: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/day", response_model=List[OHLCResponse])
async def get_daily_ohlc(
    start: datetime = Query(..., description="Start time in UTC (ISO 8601)", example="2025-12-01T00:00:00Z"),
    end: datetime = Query(... , description="End time in UTC (ISO 8601)", example="2025-12-04T00:00:00Z"),
    symbol: str = Query("EURUSD", max_length=10),
    limit: int = Query(365, ge=1, le=3650, description="Max number of rows (default: 365 days, max: 10 years)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get daily OHLC data from continuous aggregate. 
    Standard midnight-to-midnight boundaries (UTC).
    
    **Time Range Limits**:
    - Maximum range: 10 years (3650 days)
    - All times must be in UTC timezone
    
    **Example**:
        GET /ohlc/day?start=2025-12-01T00:00:00Z&end=2025-12-04T00:00:00Z&symbol=EURUSD
    """
    try:
        # Validate time range (max 10 years for daily data)
        time_diff = (end - start).total_seconds()
        max_days = 3650  # 10 years
        if time_diff > max_days * 86400:  # Convert to seconds
            raise HTTPException(
                status_code=400,
                detail=f"Time range too large. Maximum: 10 years ({max_days} days). Your range: {time_diff / 86400:.1f} days"
            )
        
        stmt = text("""
            SELECT bucket, symbol, open, high, low, close, tick_count
            FROM eurusd_ohlc_day
            WHERE bucket >= :start AND bucket < :end AND symbol = :symbol
            ORDER BY bucket ASC
            LIMIT :limit
        """)
        
        result = await db.execute(stmt, {"start": start, "end": end, "symbol": symbol, "limit": limit})
        rows = result. fetchall()
        
        return [
            OHLCResponse(
                bucket=row[0],
                symbol=row[1],
                open=row[2],
                high=row[3],
                low=row[4],
                close=row[5],
                tick_count=row[6]
            )
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error fetching daily OHLC: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router. get("/custom-day", response_model=List[OHLCResponse])
async def get_custom_day_ohlc(
    start: datetime = Query(..., description="Start time in UTC (ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ)", example="2025-12-01T00:00:00Z"),
    end: datetime = Query(..., description="End time in UTC (ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ)", example="2025-12-05T00:00:00Z"),
    day_start_hour: int = Query(22, ge=0, le=23, description="Hour when day starts in UTC (0-23). Example: 22 = 10 PM UTC"),
    symbol: str = Query("EURUSD", max_length=10),
    db: AsyncSession = Depends(get_db)
):
    """
    Get daily OHLC with custom day start time (UTC timezone).
    
    **Important**: 
    - All times are in UTC timezone
    - day_start_hour is in UTC (22 = 10 PM UTC, not local time)
    - Buckets are aligned to UTC time boundaries
    
    **Example**: day_start_hour=22 means day runs from 10 PM UTC to 10 PM UTC (24 hours).
    
    **Usage**:
        GET /ohlc/custom-day?start=2025-12-01T00:00:00Z&end=2025-12-05T00:00:00Z&day_start_hour=22&symbol=EURUSD
        
    **Date Format Requirements**:
    - Must include full datetime: YYYY-MM-DDTHH:MM:SSZ
    - Must include 'T' separator between date and time
    - Must include 'Z' suffix for UTC timezone
    - Wrong: 2025-12-01
    - Correct: 2025-12-01T00:00:00Z
    """
    try:
        # Validate timezone awareness
        if start.tzinfo is None or end.tzinfo is None:
            raise HTTPException(
                status_code=422,
                detail="Datetime must be timezone-aware (use 'Z' suffix for UTC or provide timezone offset)"
            )
        
        # Validate time range (max 10 years for daily data)
        time_diff = (end - start).total_seconds()
        max_days = 3650  # 10 years
        if time_diff > max_days * 86400:  # Convert to seconds
            raise HTTPException(
                status_code=400,
                detail=f"Time range too large. Maximum: 10 years ({max_days} days). Your range: {time_diff / 86400:.1f} days"
            )
        
        stmt = text("""
            SELECT * FROM get_custom_day_ohlc(:start, :end, :day_start_hour)
            WHERE symbol = :symbol
            ORDER BY bucket ASC
            LIMIT 3650
        """)
        
        result = await db.execute(stmt, {
            "start": start,
            "end": end,
            "day_start_hour": day_start_hour,
            "symbol": symbol
        })
        rows = result.fetchall()
        
        return [
            OHLCResponse(
                bucket=row[0],
                symbol=row[1],
                open=row[2],
                high=row[3],
                low=row[4],
                close=row[5],
                tick_count=row[6]
            )
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error fetching custom day OHLC: {e}")
        raise HTTPException(status_code=500, detail=str(e))