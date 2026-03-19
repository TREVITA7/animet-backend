from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
import base64

app = FastAPI(title="ANIMET Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_KEY = os.environ.get("HF_API_KEY", "")
HF_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

class GenerateRequest(BaseModel):
    prompt: str
    frame_num: int = 1
    total_frames: int = 15

@app.get("/")
def root():
    return {"status": "ANIMET backend running!"}

@app.get("/health")
def health():
    return {"status": "ok", "hf_key_set": bool(HF_KEY)}

@app.post("/generate")
async def generate_frame(req: GenerateRequest):
    if not HF_KEY:
        raise HTTPException(status_code=500, detail="HF API key not configured")
    full_prompt = f"{req.prompt}, frame {req.frame_num} of {req.total_frames}, black and white manga art, detailed ink lines, dynamic action"
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            HF_URL,
            headers={"Authorization": f"Bearer {HF_KEY}", "Content-Type": "application/json"},
            json={"inputs": full_prompt, "parameters": {"num_inference_steps": 4, "width": 512, "height": 320}},
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text[:200])
        image_b64 = base64.b64encode(response.content).decode("utf-8")
        return {"image_b64": image_b64, "frame_num": req.frame_num}
