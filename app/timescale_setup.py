"""
TimescaleDB-specific setup: hypertables and continuous aggregates.

Configures TimescaleDB extensions, creates hypertables for time-series data,
and sets up continuous aggregates with refresh policies for real-time OHLC calculations.
"""
import logging
from sqlalchemy import text
from app.database import engine

logger = logging.getLogger(__name__)


async def setup_timescaledb():
    """
    Set up TimescaleDB extensions, hypertables, and continuous aggregates. 
    This runs after table creation. 
    """
    async with engine.begin() as conn:
        try:
            # 1. Enable TimescaleDB extension
            logger.info("Enabling TimescaleDB extension...")
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
            
            # 2. Convert table to hypertable (check if table exists first)
            logger.info("Creating hypertable for eurusd_ticks...")
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'eurusd_ticks'
                );
            """))
            table_exists = result.scalar()
            
            if table_exists:
                # Try to create hypertable only if table exists
                try:
                    await conn.execute(text("""
                        SELECT create_hypertable(
                            'eurusd_ticks',
                            'time',
                            chunk_time_interval => INTERVAL '1 day',
                            if_not_exists => TRUE
                        );
                    """))
                    logger.info("Hypertable created successfully")
                except Exception as e:
                    if "already a hypertable" in str(e):
                        logger.info("Hypertable already exists, skipping")
                    else:
                        raise
            else:
                logger.warning("Table eurusd_ticks does not exist yet, skipping hypertable creation")
                return  # Exit early if table doesn't exist
            
            # 3. Create continuous aggregate for minute OHLC with REAL-TIME aggregation
            logger.info("Creating continuous aggregate for minute OHLC...")
            await conn.execute(text("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS eurusd_ohlc_minute
                WITH (timescaledb.continuous, timescaledb.materialized_only = false) AS
                SELECT
                    time_bucket('1 minute', time) AS bucket,
                    symbol,
                    first(price, time) AS open,
                    max(price) AS high,
                    min(price) AS low,
                    last(price, time) AS close,
                    count(*) AS tick_count
                FROM eurusd_ticks
                GROUP BY bucket, symbol
                WITH NO DATA;
            """))
            
            # 4. Create continuous aggregate for hourly OHLC with REAL-TIME aggregation
            logger.info("Creating continuous aggregate for hourly OHLC...")
            await conn.execute(text("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS eurusd_ohlc_hour
                WITH (timescaledb.continuous, timescaledb.materialized_only = false) AS
                SELECT
                    time_bucket('1 hour', time) AS bucket,
                    symbol,
                    first(price, time) AS open,
                    max(price) AS high,
                    min(price) AS low,
                    last(price, time) AS close,
                    count(*) AS tick_count
                FROM eurusd_ticks
                GROUP BY bucket, symbol
                WITH NO DATA;
            """))
            
            # 5. Create continuous aggregate for daily OHLC with REAL-TIME aggregation
            logger.info("Creating continuous aggregate for daily OHLC...")
            await conn.execute(text("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS eurusd_ohlc_day
                WITH (timescaledb.continuous, timescaledb.materialized_only = false) AS
                SELECT
                    time_bucket('1 day', time) AS bucket,
                    symbol,
                    first(price, time) AS open,
                    max(price) AS high,
                    min(price) AS low,
                    last(price, time) AS close,
                    count(*) AS tick_count
                FROM eurusd_ticks
                GROUP BY bucket, symbol
                WITH NO DATA;
            """))
            
            # 6. Add refresh policies for real-time updates
            logger.info("Setting up refresh policies...")
            
            # Minute OHLC: refresh every 5 seconds for near real-time
            await conn.execute(text("""
                SELECT add_continuous_aggregate_policy('eurusd_ohlc_minute',
                    start_offset => INTERVAL '1 hour',
                    end_offset => INTERVAL '1 second',
                    schedule_interval => INTERVAL '5 seconds',
                    if_not_exists => TRUE
                );
            """))
            
            # Hourly OHLC: refresh every 30 seconds
            await conn.execute(text("""
                SELECT add_continuous_aggregate_policy('eurusd_ohlc_hour',
                    start_offset => INTERVAL '1 day',
                    end_offset => INTERVAL '1 second',
                    schedule_interval => INTERVAL '30 seconds',
                    if_not_exists => TRUE
                );
            """))
            
            # Daily OHLC: refresh every 5 minutes
            await conn.execute(text("""
                SELECT add_continuous_aggregate_policy('eurusd_ohlc_day',
                    start_offset => INTERVAL '7 days',
                    end_offset => INTERVAL '1 minute',
                    schedule_interval => INTERVAL '5 minutes',
                    if_not_exists => TRUE
                );
            """))
            
            # 7.  Create indexes on continuous aggregates
            logger.info("Creating indexes on continuous aggregates...")
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_minute_bucket 
                ON eurusd_ohlc_minute (bucket DESC, symbol);
            """))
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_hour_bucket 
                ON eurusd_ohlc_hour (bucket DESC, symbol);
            """))
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_day_bucket 
                ON eurusd_ohlc_day (bucket DESC, symbol);
            """))
            
            # 8. Set up compression policy (optional, for production efficiency)
            logger.info("Setting up compression policy...")
            await conn.execute(text("""
                ALTER TABLE eurusd_ticks SET (
                    timescaledb.compress,
                    timescaledb.compress_segmentby = 'symbol',
                    timescaledb.compress_orderby = 'time DESC'
                );
            """))
            
            await conn.execute(text("""
                SELECT add_compression_policy('eurusd_ticks', 
                    INTERVAL '7 days',
                    if_not_exists => TRUE
                );
            """))
            
            # 9. Add retention policy (optional, for data lifecycle management)
            logger.info("Setting up retention policy...")
            await conn.execute(text("""
                SELECT add_retention_policy('eurusd_ticks', 
                    INTERVAL '90 days',
                    if_not_exists => TRUE
                );
            """))
            
            logger.info("TimescaleDB setup completed successfully!")
            
        except Exception as e:
            logger.error(f"Error setting up TimescaleDB: {e}")
            raise


async def setup_custom_day_aggregate():
    """
    Create a custom function for daily OHLC with offset (e.g., day starts at 10 PM).
    """
    async with engine.begin() as conn:
        try:
            logger.info("Creating custom day OHLC function...")
            await conn.execute(text("""
                CREATE OR REPLACE FUNCTION get_custom_day_ohlc(
                    start_time TIMESTAMPTZ,
                    end_time TIMESTAMPTZ,
                    day_start_hour INT DEFAULT 22
                )
                RETURNS TABLE (
                    bucket TIMESTAMPTZ,
                    symbol VARCHAR,
                    open DOUBLE PRECISION,
                    high DOUBLE PRECISION,
                    low DOUBLE PRECISION,
                    close DOUBLE PRECISION,
                    tick_count BIGINT
                ) AS $$
                DECLARE
                    origin_point TIMESTAMPTZ;
                BEGIN
                    -- Calculate fixed origin point: epoch time + day_start_hour offset
                    -- This ensures consistent bucket alignment regardless of query time
                    origin_point := ('1970-01-01 00:00:00'::TIMESTAMPTZ + 
                                    INTERVAL '1 hour' * day_start_hour);
                    
                    RETURN QUERY
                    SELECT
                        time_bucket('1 day', time, origin_point) AS bucket,
                        t.symbol,
                        first(t.price, t.time) AS open,
                        max(t.price) AS high,
                        min(t.price) AS low,
                        last(t.price, t.time) AS close,
                        count(*)::BIGINT AS tick_count
                    FROM eurusd_ticks t
                    WHERE t.time >= start_time AND t.time < end_time
                    GROUP BY bucket, t.symbol
                    ORDER BY bucket ASC;
                END;
                $$ LANGUAGE plpgsql;
            """))
            
            logger.info("Custom day OHLC function created!")
            
        except Exception as e:
            logger.error(f"Error creating custom day function: {e}")
            raise