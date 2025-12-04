"""
REST API endpoints for tick data management (POST/PUT/DELETE).


Primary Use Cases:
- Testing: Manual tick insertion for development
- External Feeds: Integration with third-party data sources  
- Historical Backfill: Bulk import of historical data
- Data Correction: Update/delete erroneous ticks

Production Notes:
- Primary ingestion: Redis Pub/Sub (internal, automated, 1000s ticks/sec)
- Secondary ingestion: These APIs (manual, external, lower throughput)
- Warning: Modifying historical tick data affects OHLC aggregates
- Recommendation: Use for testing/backfill, not real-time production ingestion

CQRS Benefits:
- Separation: Write endpoints isolated from read endpoints
- Scalability: Can scale write and read independently
- Flexibility: Multiple write sources (Redis + API)
- Performance: Writes don't block OHLC queries
"""
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy import select, delete, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Tick
from app.schemas import TickCreate, TickUpdate, TickResponse
from app.redis_pubsub import publish_tick

router = APIRouter(prefix="/ticks", tags=["Tick Management"])


@router.post("/", response_model=TickResponse, status_code=201)
async def create_tick(
    tick: TickCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new tick (manual insertion).
    
    **Use Case:** 
    - Testing
    - External data feed integration
    - Historical data backfill
    
    **Note:** In production, ticks are ingested via Redis Pub/Sub.
    This endpoint allows manual insertion when needed.
    
    **Example:**
    ```json
    {
        "time": "2025-12-05T10:30:00Z",
        "symbol": "EURUSD",
        "price": 1.1234
    }
    ```
    """
    try:
        # Create tick object
        db_tick = Tick(
            time=tick.time,
            symbol=tick.symbol,
            price=tick.price
        )
        
        # Add to database
        db.add(db_tick)
        await db.commit()
        await db.refresh(db_tick)
        
        # Publish to Redis for WebSocket streaming (optional)
        try:
            await publish_tick({
                "time": tick.time.isoformat(),
                "symbol": tick.symbol,
                "price": tick.price
            })
        except Exception as e:
            # Redis publish is optional, don't fail the request
            pass
        
        return TickResponse(
            time=db_tick.time,
            symbol=db_tick.symbol,
            price=db_tick.price
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to create tick: {str(e)}")


@router.post("/bulk", response_model=dict, status_code=201)
async def create_ticks_bulk(
    ticks: List[TickCreate],
    db: AsyncSession = Depends(get_db)
):
    """
    Create multiple ticks in bulk (batch insertion).
    
    **Use Case:**
    - Historical data backfill
    - Bulk import from external source
    - Performance testing
    
    **Example:**
    ```json
    [
        {"time": "2025-12-05T10:30:00Z", "symbol": "EURUSD", "price": 1.1234},
        {"time": "2025-12-05T10:30:01Z", "symbol": "EURUSD", "price": 1.1235},
        {"time": "2025-12-05T10:30:02Z", "symbol": "EURUSD", "price": 1.1233}
    ]
    ```
    
    **Returns:**
    ```json
    {
        "created": 3,
        "message": "Successfully created 3 ticks"
    }
    ```
    """
    try:
        # Create tick objects
        db_ticks = [
            Tick(time=tick.time, symbol=tick.symbol, price=tick.price)
            for tick in ticks
        ]
        
        # Bulk insert
        db.add_all(db_ticks)
        await db.commit()
        
        return {
            "created": len(db_ticks),
            "message": f"Successfully created {len(db_ticks)} ticks"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Bulk insert failed: {str(e)}")


@router.get("/", response_model=List[TickResponse])
async def get_ticks(
    symbol: str = Query(..., description="Currency pair symbol (e.g., EURUSD)"),
    start: datetime = Query(..., description="Start time (ISO 8601, UTC)"),
    end: datetime = Query(..., description="End time (ISO 8601, UTC)"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of ticks to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get raw tick data for a time range.
    
    **Use Case:**
    - Retrieve raw tick data
    - Debugging
    - Data verification
    
    **Example:**
    ```
    GET /ticks/?symbol=EURUSD&start=2025-12-05T10:00:00Z&end=2025-12-05T11:00:00Z&limit=1000
    ```
    
    **Returns:** Array of tick objects with time, symbol, price
    """
    try:
        query = select(Tick).where(
            and_(
                Tick.symbol == symbol,
                Tick.time >= start,
                Tick.time < end
            )
        ).order_by(Tick.time.asc()).limit(limit)
        
        result = await db.execute(query)
        ticks = result.scalars().all()
        
        return [
            TickResponse(time=tick.time, symbol=tick.symbol, price=tick.price)
            for tick in ticks
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ticks: {str(e)}")


@router.put("/", response_model=TickResponse)
async def update_tick(
    time: datetime = Query(..., description="Tick timestamp (ISO 8601, UTC)"),
    symbol: str = Query(..., description="Currency pair symbol"),
    tick_update: TickUpdate = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing tick's price.
    
    **Use Case:**
    - Correction of erroneous data
    - Price adjustment
    
    **Warning:** Modifying historical tick data affects OHLC aggregations.
    Use with caution in production.
    
    **Example:**
    ```
    PUT /ticks/?time=2025-12-05T10:30:00Z&symbol=EURUSD
    Body: {"price": 1.1240}
    ```
    """
    try:
        # Find the tick
        query = select(Tick).where(
            and_(
                Tick.time == time,
                Tick.symbol == symbol
            )
        )
        result = await db.execute(query)
        tick = result.scalar_one_or_none()
        
        if not tick:
            raise HTTPException(
                status_code=404,
                detail=f"Tick not found for symbol={symbol} at time={time}"
            )
        
        # Update price
        tick.price = tick_update.price
        await db.commit()
        await db.refresh(tick)
        
        return TickResponse(
            time=tick.time,
            symbol=tick.symbol,
            price=tick.price
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update tick: {str(e)}")


@router.delete("/", response_model=dict)
async def delete_ticks(
    symbol: str = Query(..., description="Currency pair symbol"),
    start: datetime = Query(..., description="Start time (ISO 8601, UTC)"),
    end: datetime = Query(..., description="End time (ISO 8601, UTC)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete ticks within a time range.
    
    **Use Case:**
    - Remove erroneous data
    - Data cleanup
    - Testing
    
    **Warning:** This operation is irreversible and affects OHLC aggregations.
    
    **Example:**
    ```
    DELETE /ticks/?symbol=EURUSD&start=2025-12-05T10:00:00Z&end=2025-12-05T11:00:00Z
    ```
    
    **Returns:**
    ```json
    {
        "deleted": 3600,
        "message": "Deleted 3600 ticks for EURUSD between 2025-12-05T10:00:00Z and 2025-12-05T11:00:00Z"
    }
    ```
    """
    try:
        # Delete ticks in range
        delete_query = delete(Tick).where(
            and_(
                Tick.symbol == symbol,
                Tick.time >= start,
                Tick.time < end
            )
        )
        
        result = await db.execute(delete_query)
        await db.commit()
        
        deleted_count = result.rowcount
        
        return {
            "deleted": deleted_count,
            "message": f"Deleted {deleted_count} ticks for {symbol} between {start} and {end}"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete ticks: {str(e)}")


@router.delete("/{symbol}/{time}", response_model=dict)
async def delete_single_tick(
    symbol: str,
    time: datetime,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a single tick by symbol and timestamp.
    
    **Use Case:**
    - Remove specific erroneous tick
    - Precision data cleanup
    
    **Example:**
    ```
    DELETE /ticks/EURUSD/2025-12-05T10:30:00Z
    ```
    """
    try:
        delete_query = delete(Tick).where(
            and_(
                Tick.symbol == symbol,
                Tick.time == time
            )
        )
        
        result = await db.execute(delete_query)
        await db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Tick not found for symbol={symbol} at time={time}"
            )
        
        return {
            "deleted": 1,
            "message": f"Deleted tick for {symbol} at {time}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete tick: {str(e)}")
