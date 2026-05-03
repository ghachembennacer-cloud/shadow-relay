import os
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

# This list tracks active browser connections (viewers)
viewers = []

@app.get("/")
async def root():
    return {"message": "Shadow Relay is Online"}

@app.websocket("/stream")
async def stream_endpoint(websocket: WebSocket):
    """
    Shadow PC connects here to send video frames.
    """
    await websocket.accept()
    print("[*] Shadow PC Linked to Relay.")
    try:
        while True:
            # Receive JPEG bytes from the Shadow PC Broadcaster
            data = await websocket.receive_bytes()
            
            # Instantly push those bytes to every connected viewer
            for viewer in viewers:
                try:
                    await viewer.send_bytes(data)
                except:
                    # Remove broken viewer connections
                    viewers.remove(viewer)
    except WebSocketDisconnect:
        print("[!] Shadow PC Disconnected.")

@app.websocket("/view")
async def view_endpoint(websocket: WebSocket):
    """
    Your Vercel Website connects here to receive video frames.
    """
    await websocket.accept()
    viewers.append(websocket)
    print(f"[*] New Viewer Connected. Total viewers: {len(viewers)}")
    try:
        while True:
            # Keep the socket open by listening for 'ping'
            await websocket.receive_text()
    except WebSocketDisconnect:
        viewers.remove(websocket)
        print("[*] Viewer Disconnected.")

if __name__ == "__main__":
    # Render assigns a dynamic port via the PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)