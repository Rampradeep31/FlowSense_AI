from typing import List
from fastapi import WebSocket
import logging
import json

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection accepted. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket connection closed. Total active: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
        await websocket.send_text(message)

    async def broadcast(self, message: str) -> None:
        logger.info(f"Broadcasting message to {len(self.active_connections)} client(s)...")
        # Copy connections list to avoid modifying it during iteration if a disconnect is triggered
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send message over WebSocket, disconnecting client: {e}")
                self.disconnect(connection)

    async def broadcast_alert(self, alert_data: dict) -> None:
        """
        Broadcasts an alert payload as serialized JSON.
        """
        try:
            payload = json.dumps(alert_data, default=str)
            await self.broadcast(payload)
        except Exception as e:
            logger.error(f"Error compiling WebSocket alert broadcast: {e}")

manager = ConnectionManager()
