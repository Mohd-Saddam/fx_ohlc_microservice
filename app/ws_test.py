"""Static HTML page for WebSocket testing."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["WebSocket Testing"])


@router.get("/ws-test", response_class=HTMLResponse)
async def websocket_test_page():
    """
    Interactive WebSocket testing page.
    
    Access at: http://localhost:8000/ws-test
    """
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebSocket Test - FX OHLC Microservice</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .content {
            padding: 30px;
        }
        
        .endpoint-selector {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .endpoint-btn {
            padding: 15px 20px;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .endpoint-btn:hover {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .endpoint-btn.active {
            background: #667eea;
            color: white;
        }
        
        .endpoint-btn .icon {
            font-size: 18px;
        }
        
        .controls {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-connect {
            background: #10b981;
            color: white;
        }
        
        .btn-connect:hover {
            background: #059669;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
        }
        
        .btn-disconnect {
            background: #ef4444;
            color: white;
        }
        
        .btn-disconnect:hover {
            background: #dc2626;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
        }
        
        .btn-clear {
            background: #6b7280;
            color: white;
        }
        
        .btn-clear:hover {
            background: #4b5563;
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none !important;
        }
        
        .status {
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .status.disconnected {
            background: #fef2f2;
            color: #dc2626;
        }
        
        .status.connected {
            background: #f0fdf4;
            color: #10b981;
        }
        
        .status .pulse {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: currentColor;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: #f9fafb;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .messages {
            background: #1f2937;
            color: #f9fafb;
            padding: 20px;
            border-radius: 8px;
            height: 400px;
            overflow-y: auto;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 13px;
            line-height: 1.6;
        }
        
        .messages::-webkit-scrollbar {
            width: 8px;
        }
        
        .messages::-webkit-scrollbar-track {
            background: #374151;
            border-radius: 4px;
        }
        
        .messages::-webkit-scrollbar-thumb {
            background: #667eea;
            border-radius: 4px;
        }
        
        .message {
            margin-bottom: 12px;
            padding: 8px 12px;
            border-radius: 4px;
            background: #374151;
        }
        
        .message-time {
            color: #9ca3af;
            font-size: 11px;
            margin-right: 8px;
        }
        
        .message-type {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            margin-right: 8px;
        }
        
        .message-type.info {
            background: #3b82f6;
            color: white;
        }
        
        .message-type.success {
            background: #10b981;
            color: white;
        }
        
        .message-type.error {
            background: #ef4444;
            color: white;
        }
        
        .message-type.data {
            background: #8b5cf6;
            color: white;
        }
        
        .message-content {
            color: #f9fafb;
        }
        
        .json {
            color: #a78bfa;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔌 WebSocket Test Console</h1>
            <p>FX OHLC Microservice - Real-time Data Streaming</p>
        </div>
        
        <div class="content">
            <h3 style="margin-bottom: 15px; color: #374151;">Select WebSocket Endpoint:</h3>
            <div class="endpoint-selector">
                <button class="endpoint-btn active" onclick="selectEndpoint('ticks')">
                    <span class="icon">📊</span>
                    <span>Real-time Ticks</span>
                </button>
                <button class="endpoint-btn" onclick="selectEndpoint('ohlc/minute')">
                    <span class="icon">⏱️</span>
                    <span>Minute OHLC</span>
                </button>
                <button class="endpoint-btn" onclick="selectEndpoint('ohlc/hour')">
                    <span class="icon">⏰</span>
                    <span>Hourly OHLC</span>
                </button>
                <button class="endpoint-btn" onclick="selectEndpoint('ohlc/day')">
                    <span class="icon">📅</span>
                    <span>Daily OHLC</span>
                </button>
            </div>
            
            <div class="controls">
                <button class="btn btn-connect" onclick="connect()" id="connectBtn">
                    🔌 Connect
                </button>
                <button class="btn btn-disconnect" onclick="disconnect()" id="disconnectBtn" disabled>
                    🔌 Disconnect
                </button>
                <button class="btn btn-clear" onclick="clearMessages()">
                    🗑️ Clear
                </button>
                <div class="status disconnected" id="status">
                    <span class="pulse"></span>
                    <span>Disconnected</span>
                </div>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value" id="messageCount">0</div>
                    <div class="stat-label">Messages</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="avgPrice">-</div>
                    <div class="stat-label">Avg Price</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="minPrice">-</div>
                    <div class="stat-label">Min Price</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="maxPrice">-</div>
                    <div class="stat-label">Max Price</div>
                </div>
            </div>
            
            <h3 style="margin-bottom: 15px; color: #374151;">Messages:</h3>
            <div class="messages" id="messages"></div>
        </div>
    </div>
    
    <script>
        let ws = null;
        let selectedEndpoint = 'ticks';
        let messageCount = 0;
        let prices = [];
        
        function selectEndpoint(endpoint) {
            selectedEndpoint = endpoint;
            document.querySelectorAll('.endpoint-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.closest('.endpoint-btn').classList.add('active');
            
            if (ws && ws.readyState === WebSocket.OPEN) {
                disconnect();
                addMessage('info', `Switched to ${endpoint} endpoint. Click Connect to reconnect.`);
            }
        }
        
        function connect() {
            const wsUrl = `ws://${window.location.host}/ws/${selectedEndpoint}`;
            addMessage('info', `Connecting to ${wsUrl}...`);
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                addMessage('success', 'Connected successfully!');
                updateStatus(true);
                document.getElementById('connectBtn').disabled = true;
                document.getElementById('disconnectBtn').disabled = false;
            };
            
            ws.onmessage = (event) => {
                messageCount++;
                const data = JSON.parse(event.data);
                
                // Track prices for statistics
                if (data.price) {
                    prices.push(data.price);
                } else if (data.close) {
                    prices.push(data.close);
                }
                
                updateStats();
                addMessage('data', JSON.stringify(data, null, 2));
            };
            
            ws.onerror = (error) => {
                addMessage('error', 'WebSocket error occurred');
                console.error('WebSocket error:', error);
            };
            
            ws.onclose = () => {
                addMessage('info', '🔌 Disconnected');
                updateStatus(false);
                document.getElementById('connectBtn').disabled = false;
                document.getElementById('disconnectBtn').disabled = true;
            };
        }
        
        function disconnect() {
            if (ws) {
                ws.close();
                ws = null;
            }
        }
        
        function updateStatus(connected) {
            const statusEl = document.getElementById('status');
            if (connected) {
                statusEl.className = 'status connected';
                statusEl.innerHTML = '<span class="pulse"></span><span>Connected</span>';
            } else {
                statusEl.className = 'status disconnected';
                statusEl.innerHTML = '<span class="pulse"></span><span>Disconnected</span>';
            }
        }
        
        function updateStats() {
            document.getElementById('messageCount').textContent = messageCount;
            
            if (prices.length > 0) {
                const avg = prices.reduce((a, b) => a + b) / prices.length;
                const min = Math.min(...prices);
                const max = Math.max(...prices);
                
                document.getElementById('avgPrice').textContent = avg.toFixed(5);
                document.getElementById('minPrice').textContent = min.toFixed(5);
                document.getElementById('maxPrice').textContent = max.toFixed(5);
            }
        }
        
        function addMessage(type, content) {
            const messagesEl = document.getElementById('messages');
            const messageEl = document.createElement('div');
            messageEl.className = 'message';
            
            const time = new Date().toLocaleTimeString();
            const isJson = content.startsWith('{') || content.startsWith('[');
            
            messageEl.innerHTML = `
                <span class="message-time">[${time}]</span>
                <span class="message-type ${type}">${type.toUpperCase()}</span>
                <span class="message-content ${isJson ? 'json' : ''}">${content}</span>
            `;
            
            messagesEl.appendChild(messageEl);
            messagesEl.scrollTop = messagesEl.scrollHeight;
        }
        
        function clearMessages() {
            document.getElementById('messages').innerHTML = '';
            messageCount = 0;
            prices = [];
            updateStats();
            document.getElementById('avgPrice').textContent = '-';
            document.getElementById('minPrice').textContent = '-';
            document.getElementById('maxPrice').textContent = '-';
        }
        
        // Auto-connect on page load
        window.addEventListener('load', () => {
            addMessage('info', 'WebSocket test console ready. Click Connect to start.');
        });
    </script>
</body>
</html>
    """
