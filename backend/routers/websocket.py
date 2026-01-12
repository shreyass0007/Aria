from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from backend.dependencies import get_connection_manager
from backend.websocket_manager import ConnectionManager

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, manager: ConnectionManager = Depends(get_connection_manager)):
    await manager.connect(websocket)
    try:
        while True:
            # We just listen to keep connection alive, 
            # primarily we send data FROM the server TO the client.
            # But we could handle client messages here too (e.g. heartbeat)
            data = await websocket.receive_text()
            # echo back or ignore
            # await manager.broadcast({"message": f"Client said: {data}"})
            pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
