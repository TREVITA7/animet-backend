import os, base64, io
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import json

app = FastAPI(title="ANIMET Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ANIMET backend running!"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/interpolate")
async def interpolate(
    panel1: UploadFile = File(...),
    panel2: UploadFile = File(...),
    num_frames: int = Form(default=15)
):
    img1 = Image.open(io.BytesIO(await panel1.read())).convert("RGBA")
    img2 = Image.open(io.BytesIO(await panel2.read())).convert("RGBA")
    img2 = img2.resize(img1.size)

    frames = []
    for i in range(num_frames):
        alpha = i / (num_frames - 1)
        frame = Image.blend(img1, img2, alpha)
        buf = io.BytesIO()
        frame.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        frames.append(b64)

    return {"frames": frames, "count": len(frames)}
