from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json

from graph import part_1_graph, config
from langchain.schema import AIMessage, HumanMessage
from langchain_core.messages import ToolMessage

# uvicorn server:app --host 0.0.0.0 --port 8000 --reload

app = FastAPI()

# Allow CORS for your Angular dev server
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{sessionId}")
async def websocket_endpoint(websocket: WebSocket, sessionId: str):
    await manager.connect(websocket)
    try:
        while True:
            user_message = await websocket.receive_text()
            # Create or update the config object using the sessionId
            thread_id = sessionId
            config = {
                "configurable": {
                    "user_id": "3442 587242",
                    "thread_id": thread_id,
                }
            }

            # Process the message using part_1_graph
            events = part_1_graph.stream({"messages": ("user", user_message)}, config, stream_mode="values")
            responses = []
            for event in events:
                if "messages" in event:
                    for m in event["messages"]:
                        if isinstance(m, AIMessage):
                            responses.append(m.content)
            final_response = responses[-1] if responses else "No response"
            await manager.send_personal_message(final_response, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A client disconnected.")

if __name__ == "__main__":
    uvicorn.run("server.server:app", host="0.0.0.0", port=8000, reload=True)