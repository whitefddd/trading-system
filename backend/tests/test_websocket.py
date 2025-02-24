import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://127.0.0.1:8000/api/ws/btcusdt"
    
    async with websockets.connect(uri) as websocket:
        print("已连接到 WebSocket 服务器")
        
        try:
            while True:
                # 接收消息
                message = await websocket.recv()
                data = json.loads(message)
                print(f"收到价格更新: {data}")
        except websockets.exceptions.ConnectionClosed:
            print("连接已关闭")

# 运行测试
asyncio.get_event_loop().run_until_complete(test_websocket()) 