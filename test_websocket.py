#!/usr/bin/env python3
"""
WebSocket Test Script for FX OHLC Microservice

This script connects to the WebSocket endpoint and displays real-time tick data.
"""
import asyncio
import websockets
import json
from datetime import datetime


async def test_websocket(endpoint: str = "ticks", duration: int = 10):
    """
    Test WebSocket connection and receive real-time ticks.
    
    Args:
        endpoint: WebSocket endpoint (ticks, ohlc/minute, ohlc/hour, ohlc/day)
        duration: Number of messages to receive (default: 10)
    """
    uri = f"ws://localhost:8000/ws/{endpoint}"
    
    print(f"🔌 Connecting to WebSocket: {uri}")
    print(f"📊 Will receive {duration} ticks...\n")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            print("-" * 70)
            print(f"{'#':<4} {'Timestamp':<26} {'Symbol':<8} {'Price':<10}")
            print("-" * 70)
            
            tick_count = 0
            prices = []
            
            # Receive ticks
            for i in range(duration):
                message = await websocket.recv()
                tick = json.loads(message)
                
                tick_count += 1
                prices.append(tick['price'])
                
                # Format timestamp
                timestamp = tick['time']
                
                # Display tick
                print(f"{tick_count:<4} {timestamp:<26} {tick['symbol']:<8} ${tick['price']:.5f}")
            
            print("-" * 70)
            print("\n📈 Statistics:")
            print(f"  Total ticks received: {tick_count}")
            print(f"  Highest price: ${max(prices):.5f}")
            print(f"  Lowest price: ${min(prices):.5f}")
            print(f"  Average price: ${sum(prices)/len(prices):.5f}")
            print(f"  Price range: ${max(prices) - min(prices):.5f}")
            
            print("\n✅ WebSocket test completed successfully!")
            
    except websockets.exceptions.WebSocketException as e:
        print(f"\n❌ WebSocket error: {e}")
        print("\n💡 Make sure the service is running:")
        print("   docker-compose up -d")
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    import sys
    
    # Parse arguments
    endpoint = sys.argv[1] if len(sys.argv) > 1 else "ticks"
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    print(f"\n📡 WebSocket Endpoints Available:")
    print("   - ticks         (real-time tick data)")
    print("   - ohlc/minute   (minute OHLC updates)")
    print("   - ohlc/hour     (hourly OHLC updates)")
    print("   - ohlc/day      (daily OHLC updates)")
    print(f"\n🎯 Testing endpoint: {endpoint}\n")
    
    # Run test
    asyncio.run(test_websocket(endpoint, duration))
