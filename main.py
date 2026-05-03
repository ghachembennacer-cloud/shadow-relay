import os, uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()
viewers = []
broadcaster = None

@app.websocket("/stream")
async def stream_endpoint(websocket: WebSocket):
    global broadcaster
    await websocket.accept()
    broadcaster = websocket
    try:
        while True:
            msg = await websocket.receive()
            data = msg.get("bytes") or msg.get("text")
            for v in viewers:
                await (v.send_bytes(data) if isinstance(data, bytes) else v.send_text(data))
    except WebSocketDisconnect: broadcaster = None

@app.websocket("/view")
async def view_endpoint(websocket: WebSocket):
    await websocket.accept()
    viewers.append(websocket)
    try:
        while True:
            # Receive input from Website and send to Shadow PC
            control_data = await websocket.receive_text()
            if broadcaster:
                await broadcaster.send_text(control_data)
    except WebSocketDisconnect: viewers.remove(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
