import os, base64, httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="ANIMET Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_KEY = os.getenv("HF_API_KEY")
HF_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"

class GenerateRequest(BaseModel):
    prompt: str
    frame_num: int = 1
    total_frames: int = 1

@app.get("/")
def root():
    return {"status": "ANIMET backend running!"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/generate")
async def generate_frame(req: GenerateRequest):
    if not HF_KEY:
        raise Exception("HF_API_KEY not set")
    full_prompt = f"{req.prompt}, frame {req.frame_num} of {req.total_frames}, black and white manga art, detailed ink lines"
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            HF_URL,
            headers={"Authorization": f"Bearer {HF_KEY}"},
            json={"inputs": full_prompt},
        )
    image_b64 = base64.b64encode(response.content).decode("utf-8")
    return {"image_b64": image_b64, "frame_num": req.frame_num}
