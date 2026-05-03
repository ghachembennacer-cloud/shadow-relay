import os
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

app = FastAPI()
viewers = []
broadcaster = None

@app.websocket("/stream")
async def stream_endpoint(websocket: WebSocket):
    global broadcaster
    await websocket.accept()
    broadcaster = websocket
    print("[*] Shadow PC Connected")
    try:
        while True:
            message = await websocket.receive()
            # Forward images (bytes) or info (text) to all viewers
            data = message.get("bytes") or message.get("text")
            if data:
                for viewer in viewers:
                    if viewer.client_state == WebSocketState.CONNECTED:
                        try:
                            if isinstance(data, bytes):
                                await viewer.send_bytes(data)
                            else:
                                await viewer.send_text(data)
                        except:
                            viewers.remove(viewer)
    except WebSocketDisconnect:
        broadcaster = None
        print("[!] Shadow PC Disconnected")

@app.websocket("/view")
async def view_endpoint(websocket: WebSocket):
    await websocket.accept()
    viewers.append(websocket)
    print(f"[*] New Viewer. Total: {len(viewers)}")
    try:
        while True:
            # Listen for mouse/keyboard from website
            control_data = await websocket.receive_text()
            if broadcaster:
                await broadcaster.send_text(control_data)
    except WebSocketDisconnect:
        viewers.remove(websocket)

if __name__ == "__main__":
    # The ws_max_size is CRITICAL for 1080p/720p images
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), ws_max_size=16777216)
