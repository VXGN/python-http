import asyncio
import time
import httpx
from tqdm.asyncio import tqdm
from typing import Optional

BASE_URL = "https://httpbin.org"

class HTTPError(Exception):
    """Custom HTTP error"""
    pass

async def fetch(c: httpx.AsyncClient) -> Optional[str]:
    try:
        response = await c.get(f"{BASE_URL}/get")
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as e:
        print(f"HTTP error {e.response.status_code}: {e}")
        return None
    except httpx.TimeoutException:
        print("Request timed out")
        return None
    except httpx.RequestError as e:
        print(f"Request error: {e}")
        return None

async def post(c: httpx.AsyncClient) -> Optional[str]:
    try:
        response = await c.post(f"{BASE_URL}/post")
        response.raise_for_status()
        return response.text
    except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.RequestError) as e:
        print(f"POST error: {e}")
        return None

async def patch(c: httpx.AsyncClient) -> Optional[str]:
    try:
        response = await c.patch(f"{BASE_URL}/patch")
        response.raise_for_status()
        return response.text
    except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.RequestError) as e:
        print(f"PATCH error: {e}")
        return None

async def update(c: httpx.AsyncClient) -> Optional[str]:
    try:
        response = await c.put(f"{BASE_URL}/put")
        response.raise_for_status()
        return response.text
    except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.RequestError) as e:
        print(f"PUT error: {e}")
        return None

async def delete(c: httpx.AsyncClient) -> Optional[str]:
    try:
        response = await c.delete(f"{BASE_URL}/delete")
        response.raise_for_status()
        return response.text
    except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.RequestError) as e:
        print(f"DELETE error: {e}")
        return None

async def worker(iterations: int, client: httpx.AsyncClient, semaphore: asyncio.Semaphore):
    """Worker to perform multiple HTTP operations"""
    async def limited_request(coro):
        async with semaphore:
            return await coro
    
    tasks = []
    for _ in range(iterations):
        tasks.extend([
            limited_request(fetch(client)),
            limited_request(post(client)),
            limited_request(patch(client)),
            limited_request(update(client)),
            limited_request(delete(client)),
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
        semaphore = asyncio.Semaphore(50)
        
        workers = [worker(25, client, semaphore) for _ in range(4)]
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
