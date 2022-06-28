from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from models import DBSession, History


app = FastAPI()


html = "error"
with open("index.html") as f:
    html = f.read()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, client_id: str, message: str):
        # TODO: handel error
        with DBSession() as session:
            session.add(History(
                client_id=client_id,
                message=message
            ))
            session.commit()
        for connection in self.active_connections:
            await connection.send_text(f"Client #{client_id}: {message}")


manager = ConnectionManager()


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    # TODO: handel error
    with DBSession() as session:
        message_historys = session.query(History).limit(10).all()
        for message_history in message_historys:
            await manager.send_personal_message(
                f"{message_history.client_id}: {message_history.message}",
                websocket
            )
        if message_historys:
            await manager.send_personal_message(
                "----------------------------------------",
                websocket
            )
    await manager.broadcast(client_id, f"Client #{client_id} joined this chat")
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(client_id, f"Client #{client_id} say: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(client_id, " left the chat")
