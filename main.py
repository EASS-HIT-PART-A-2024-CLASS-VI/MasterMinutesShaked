from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
from transformers import AutoModelForCausalLM, AutoTokenizer
import requests
import asyncio
import httpx
import uvicorn
import time
import subprocess
import sys
import torch
import os

# xAI API details
XAI_API_URL = "https://api.x.ai/v1/chat/completions"
XAI_API_KEY = os.getenv("XAI_API_KEY", "xai-8R9u7ALNZuXiLlLmUapvAnD2GgzH9wp6SeTic9lgS2miNkajisEGBBXAqa7kBb2tEmXZKPtSft02oxuX")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Loading models...")
    asyncio.create_task(initialize_models())
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

# Global state tracking
MODEL_STATE = {
    "ready": False,
    "loading": False,
    "error": None
}

# Load Hugging Face model and tokenizer
hf_model_name = "distilgpt2" #"microsoft/phi-2"
tokenizer = None
hf_model = None

def get_device():
    """Get appropriate device with fallback to CPU."""
    if torch.cuda.is_available():
        return "cuda"
    elif hasattr(torch, 'mps') and torch.backends.mps.is_available():
        return "mps"
    return "cpu"

async def initialize_models():
    global MODEL_STATE, tokenizer, hf_model
    if not MODEL_STATE["loading"]:
        MODEL_STATE["loading"] = True
        try:
            print(f"Loading {hf_model_name} model...")
            device = get_device()
            print(f"Using device: {device}")
            
            tokenizer = AutoTokenizer.from_pretrained(
                hf_model_name,
                trust_remote_code=True,
                local_files_only=False
            )
            
            model_kwargs = {
                "trust_remote_code": True,
                "torch_dtype": torch.float32,
                "local_files_only": False
            }
            
            # Only set device_map if not using CPU
            if device != "cpu":
                model_kwargs["device_map"] = device
            
            hf_model = AutoModelForCausalLM.from_pretrained(
                hf_model_name,
                **model_kwargs
            )
            
            # Manually move model to device if using CPU
            if device == "cpu":
                hf_model = hf_model.to(device)
            
            MODEL_STATE["ready"] = True
            MODEL_STATE["error"] = None
            print("Model loaded successfully")
        except Exception as e:
            MODEL_STATE["error"] = str(e)
            print(f"Model initialization failed: {e}", file=sys.stderr)
            raise
        finally:
            MODEL_STATE["loading"] = False

async def wait_for_model_ready(timeout: int = 300) -> bool:
    start_time = time.time()
    while time.time() - start_time < timeout:
        if MODEL_STATE["ready"]:
            return True
        await asyncio.sleep(1)
    return False

@app.on_event("startup")
async def startup_event():
    # Initialize model
    asyncio.create_task(initialize_models())
    
    # Wait for model to be ready
    if not await wait_for_model_ready():
        print("Model failed to initialize within timeout")
        sys.exit(1)

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy" if MODEL_STATE["ready"] else "initializing",
        "model_ready": MODEL_STATE["ready"],
        "model_loading": MODEL_STATE["loading"],
        "error": MODEL_STATE["error"]
    }

@app.get("/wait")
async def wait_for_model(timeout: int = 30) -> Dict[str, str]:
    start_time = time.time()
    while not MODEL_STATE["ready"]:
        if time.time() - start_time > timeout:
            raise HTTPException(status_code=504, detail="Model initialization timeout")
        await asyncio.sleep(1)
    return {"status": "ready"}

# Request schema
class HuggingFaceQueryRequest(BaseModel):
    input_text: str
    max_length: int = 50

class XAIQueryRequest(BaseModel):
    messages: list
    model: str = "grok-beta"
    stream: bool = False
    temperature: float = 0

# Increase generation timeout
GENERATION_TIMEOUT = 180.0  # 3 minutes

@app.post("/huggingface/query")
async def query_huggingface_model(request: HuggingFaceQueryRequest) -> Dict[str, str]:
    if not MODEL_STATE["ready"]:
        raise HTTPException(status_code=503, detail="Model not ready")
    
    try:
        inputs = tokenizer.encode(request.input_text, return_tensors="pt")
        attention_mask = inputs.new_ones(inputs.shape)
        
        outputs = await asyncio.wait_for(
            asyncio.to_thread(
                hf_model.generate,
                inputs,
                attention_mask=attention_mask,
                max_length=request.max_length,
                num_return_sequences=2,
                pad_token_id=tokenizer.eos_token_id,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.1,
                no_repeat_ngram_size=2,
                early_stopping=True
            ),
            timeout=GENERATION_TIMEOUT
        )
        
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return {"generated_text": generated_text}
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail=f"Generation timeout after {GENERATION_TIMEOUT}s")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/xai/query")
async def query_xai_model(request: XAIQueryRequest) -> Dict[str, Any]:
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {XAI_API_KEY}"
        }
        async with httpx.AsyncClient(timeout=60.0) as client:  # Increased timeout
            response = await client.post(XAI_API_URL, headers=headers, json=request.model_dump())
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="xAI API timeout")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    try:
        # Check if port is in use
        import socket
        s = socket.socket()
        try:
            s.bind(("127.0.0.1", 1236))
        finally:
            s.close()
        
        uvicorn.run(app, host="127.0.0.1", port=1236)
    except Exception as e:
        print(f"Server startup failed: {e}")
        exit(1)