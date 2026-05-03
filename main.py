from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
import os

app = FastAPI()

# This list tracks anyone currently looking at your website
viewers = []

@app.get("/")
async def health_check():
    return {"status": "Relay is Online"}

@app.websocket("/stream")
async def stream_endpoint(websocket: WebSocket):
    """ This is where the Shadow PC connects to send video """
    await websocket.accept()
    print("Shadow PC Connected")
    try:
        while True:
            # Receive the JPG bytes from Shadow PC
            data = await websocket.receive_bytes()
            # Send those bytes to every browser tab watching the feed
            for viewer in viewers:
                try:
                    await viewer.send_bytes(data)
                except:
                    viewers.remove(viewer)
    except WebSocketDisconnect:
        print("Shadow PC Disconnected")

@app.websocket("/view")
async def view_endpoint(websocket: WebSocket):
    """ This is where your Vercel website connects to see the video """
    await websocket.accept()
    viewers.append(websocket)
    print(f"New Viewer Connected. Total: {len(viewers)}")
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        viewers.remove(websocket)
        print("Viewer Disconnected")

if __name__ == "__main__":
    # Render provides the port via an environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
