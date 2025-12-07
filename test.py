import asyncio
import time
import httpx
from tqdm.asyncio import tqdm
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = "https://httpbin.org"
JWT_URL = os.getenv("JWT_URL")
JWT_USERNAME = os.getenv("JWT_USERNAME")
JWT_PASSWORD = os.getenv("JWT_PASSWORD")

class HTTPError(Exception):
    pass

async def get_jwt_token(client: httpx.AsyncClient) -> str:
    response = await client.post(JWT_URL, data={"username": JWT_USERNAME, "password": JWT_PASSWORD})
    response.raise_for_status()
    token = response.json().get("access_token")
    if not token:
        raise HTTPError("Failed to get JWT token")
    return token

async def fetch(c: httpx.AsyncClient, token: str) -> Optional[str]:
    try:
        response = await c.get(f"{BASE_URL}/get", headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()
        return response.text
    except:
        return None

async def post(c: httpx.AsyncClient, token: str) -> Optional[str]:
    try:
        response = await c.post(f"{BASE_URL}/post", headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()
        return response.text
    except:
        return None

async def patch(c: httpx.AsyncClient, token: str) -> Optional[str]:
    try:
        response = await c.patch(f"{BASE_URL}/patch", headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()
        return response.text
    except:
        return None

async def update(c: httpx.AsyncClient, token: str) -> Optional[str]:
    try:
        response = await c.put(f"{BASE_URL}/put", headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()
        return response.text
    except:
        return None

async def delete(c: httpx.AsyncClient, token: str) -> Optional[str]:
    try:
        response = await c.delete(f"{BASE_URL}/delete", headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()
        return response.text
    except:
        return None

async def worker(iterations: int, client: httpx.AsyncClient, semaphore: asyncio.Semaphore, token: str):
    async def limited_request(coro):
        async with semaphore:
            return await coro
    
    tasks = []
    for _ in range(iterations):
        tasks.extend([
            limited_request(fetch(client, token)),
            limited_request(post(client, token)),
            limited_request(patch(client, token)),
            limited_request(update(client, token)),
            limited_request(delete(client, token)),
        ])
    
    results = []
    for coro in tqdm.as_completed(tasks, total=len(tasks), desc="Processing requests"):
        result = await coro
        results.append(result)
    
    return results

async def main_async():
    start = time.perf_counter()
    
    async with httpx.AsyncClient(
        http2=True,
        limits=httpx.Limits(
            max_connections=100,
            max_keepalive_connections=20,
            keepalive_expiry=30.0
        ),
        timeout=httpx.Timeout(
            10.0,
            connect=5.0
        ),
    ) as client:
        token = await get_jwt_token(client)
        semaphore = asyncio.Semaphore(50)
        workers = [worker(25, client, semaphore, token) for _ in range(4)]
        all_results = await asyncio.gather(*workers)
        
        total_requests = sum(len(results) for results in all_results)
        successful = sum(1 for results in all_results for r in results if r is not None)
        failed = total_requests - successful
        
        elapsed = time.perf_counter() - start
        print(f"\n{'='*50}")
        print(f"Time taken: {elapsed:.2f} seconds")
        print(f"Total requests: {total_requests}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Requests/second: {total_requests/elapsed:.2f}")
        print(f"{'='*50}")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
