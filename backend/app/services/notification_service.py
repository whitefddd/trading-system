from fastapi import WebSocket
import json
from typing import Dict, Set

class NotificationService:
    active_connections: Dict[str, Set[WebSocket]] = {}
    
    @staticmethod
    async def connect(websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in NotificationService.active_connections:
            NotificationService.active_connections[user_id] = set()
        NotificationService.active_connections[user_id].add(websocket)
    
    @staticmethod
    async def broadcast_message(message: dict, user_id: str = None):
        if user_id:
            connections = NotificationService.active_connections.get(user_id, set())
        else:
            connections = {ws for conns in NotificationService.active_connections.values() for ws in conns}
            
        for connection in connections:
            try:
                await connection.send_json(message)
            except:
                await NotificationService.disconnect(connection) 