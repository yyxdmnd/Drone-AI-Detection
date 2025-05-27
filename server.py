from fastapi import FastAPI, WebSocket
import yolov8

app = FastAPI()

@app.websocket("/video")
async def video_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_bytes()
        # 使用YOLOv8进行污水检测
        results = yolov8.detect(data)
        # 返回检测结果
        await websocket.send_json(results)

# ... existing code ... 