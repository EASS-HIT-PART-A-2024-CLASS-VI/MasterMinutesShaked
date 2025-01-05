import pytest
import httpx
import subprocess
import time
import signal
import os
import asyncio
import logging
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base URL of the FastAPI server
BASE_URL = "http://127.0.0.1:1236"

@pytest.mark.asyncio
async def wait_for_server_ready(url: str, timeout: int = 60) -> bool:
    """Wait for server to be ready and model to be initialized."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{url}/health")
                if response.status_code == 200:
                    data = response.json()
                    if data["model_ready"]:
                        logger.info("Server and model are ready!")
                        return True
                    logger.info(f"Waiting for model initialization... Status: {data['status']}")
                await asyncio.sleep(2)
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            await asyncio.sleep(2)
    return False

@pytest.fixture(scope="module", autouse=True)
async def ensure_server_ready():
    """Ensure server and model are ready before running tests."""
    retry_count = 0
    while retry_count < 30:  # 30 seconds max wait
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{BASE_URL}/health")
                if response.status_code == 200:
                    data = response.json()
                    if data["model_ready"]:
                        return  # Server is ready
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
        await asyncio.sleep(1)
        retry_count += 1
    
    raise Exception("Server not ready within timeout")

@pytest.fixture(scope="module", autouse=True)
async def setup_test_environment():
    logger.info("Starting test environment setup...")
    
    # Kill any existing processes
    subprocess.run("pkill -f 'uvicorn.*:1236'", shell=True)
    time.sleep(2)
    
    # Start server
    process = subprocess.Popen(["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "1236"])
    time.sleep(5)  # Give time for uvicorn to start
    
    # Wait for server and model
    logger.info("Waiting for server and model to be ready...")
    if not await wait_for_server_ready(BASE_URL, timeout=180):  # 3 minutes timeout
        process.terminate()
        raise Exception("Server/model initialization timeout")
    
    yield process
    
    # Cleanup
    logger.info("Cleaning up...")
    process.terminate()
    time.sleep(1)
    process.kill()
    process.wait()

def print_separator():
    print("\n" + "="*100)
    print(" "*40 + "MODEL COMPARISON")
    print("="*100 + "\n")

def print_model_section(name: str):
    print(f"\n{'-'*40} {name} {'-'*40}\n")

# @pytest.mark.asyncio
# async def test_huggingface_query():
#     url = f"{BASE_URL}/huggingface/query"
#     # Shorter prompt to reduce generation time
#     prompt = """Create Elon Musk's optimal daily schedule focusing on: gym, meetings, coding, family time. 
#     Keep it concise and efficient."""
    
#     payload = {
#         "input_text": prompt,
#         "max_length": 200  # Reduced for faster response
#     }
    
#     print_model_section("PHI-2 MODEL")
#     print("Input Prompt:\n", prompt.strip(), "\n")
    
#     async with httpx.AsyncClient(timeout=240.0) as client:  # 4 minutes timeout
#         try:
#             response = await client.post(url, json=payload)
#             assert response.status_code == 200, f"Failed with status {response.status_code}: {response.text}"
#             data = response.json()
#             assert "generated_text" in data, "Response missing 'generated_text'"
#             print("\nGenerated Schedule:")
#             print("-" * 50)
#             print(data["generated_text"].strip())
#             print("-" * 50)
#         except Exception as e:
#             print(f"\nError details: {str(e)}")
#             raise

@pytest.mark.asyncio
async def test_xai_query():
    url = f"{BASE_URL}/xai/query"
    # Shorter prompt for Grok
    system_prompt = """You are a time management expert who creates efficient schedules like Elon Musk."""
    
    user_prompt = """Create a concise daily schedule with specific times for:
    1. Gym workout
    2. Key meetings
    3. Teaching
    4. Focus work"""
    
    payload = {
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "model": "grok-beta",
        "stream": False,
        "temperature": 0
    }
    
    print_model_section("GROK MODEL")
    print("System Context:\n", system_prompt.strip(), "\n")
    print("User Query:\n", user_prompt.strip(), "\n")
    
    async with httpx.AsyncClient(timeout=90.0) as client:  # 90 seconds timeout
        try:
            response = await client.post(url, json=payload)
            assert response.status_code == 200, f"Failed with status {response.status_code}"
            data = response.json()
            assert "choices" in data, "Response missing 'choices'"
            assert len(data["choices"]) > 0, "No choices returned"
            print("\nRecommended Schedule:")
            print("-" * 50)
            print(data["choices"][0]["message"]["content"].strip())
            print("-" * 50)
        except Exception as e:
            print(f"\nError details: {str(e)}")
            raise

# @pytest.mark.asyncio
# async def test_health_check():
#     async with httpx.AsyncClient() as client:
#         response = await client.get(f"{BASE_URL}/health")
#         assert response.status_code == 200
#         data = response.json()
#         assert data["status"] == "healthy"
#         assert data["model_ready"] is True