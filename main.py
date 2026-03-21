import os, base64, io
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root(): return {"status": "ANIMET backend running!"}

@app.get("/health")
def health(): return {"status": "ok"}

@app.post("/interpolate")
async def interpolate(panel1: UploadFile = File(...), panel2: UploadFile = File(...), num_frames: int = Form(default=15)):
    try:
        d1 = await panel1.read()
        d2 = await panel2.read()
        if len(d1) < 100 or len(d2) < 100: return {"error": "bad images", "frames": []}
        i1 = Image.open(io.BytesIO(d1)).convert("RGBA")
        i2 = Image.open(io.BytesIO(d2)).convert("RGBA").resize(i1.size)
        frames = []
        for i in range(num_frames):
            f = Image.blend(i1, i2, i/(num_frames-1))
            b = io.BytesIO()
            f.save(b, "PNG")
            frames.append(base64.b64encode(b.getvalue()).decode())
        return {"frames": frames, "count": len(frames)}
    except Exception as e: return {"error": str(e), "frames": []}
