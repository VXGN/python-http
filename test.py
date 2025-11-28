from typing import Any
import time
import httpx
from rich import print
import asyncio
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://httpbin.org/"

async def fetch(c: httpx.AsyncClient) -> Any:
    try:
        r = await c.get(f"{BASE_URL}/get")
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        print(f"Error fetching data: {e}")
        return None

async def post(c: httpx.AsyncClient) -> Any:
    try:
        r = await c.post(f"{BASE_URL}/post")
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        print(f"Error posting data: {e}")
        return None

async def update(c: httpx.AsyncClient) -> Any:
    try:
        r = await c.put(f"{BASE_URL}/put")
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        print(f"Error updating data: {e}")
        return None

async def delete(c: httpx.AsyncClient) -> Any:
    try:
        r = await c.delete(f"{BASE_URL}/delete")
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        print(f"Error deleting data: {e}")
        return None

async def perform_operations(c: httpx.AsyncClient) -> None:
    """Perform all four operations concurrently"""
    await asyncio.gather(
        fetch(c),
        post(c),
        update(c),
        delete(c)
    )

async def async_worker(iterations: int) -> None:
    """Async worker that runs in a single thread"""
    async with httpx.AsyncClient() as c:
        tasks = [perform_operations(c) for _ in range(iterations)]
        await asyncio.gather(*tasks)

def thread_worker(iterations: int) -> None:
    """Thread worker that runs an async event loop"""
    asyncio.run(async_worker(iterations))

def main() -> None:
    start = time.perf_counter()
    
    num_threads = 4
    iterations_per_thread = 25
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(thread_worker, iterations_per_thread)
            for _ in range(num_threads)
        ]
        
        for future in futures:
            future.result()
    
    end = time.perf_counter()
    print(f"time taken {end - start:.2f} seconds")
    print(f"Used {num_threads} threads with {iterations_per_thread} iterations each")

if __name__ == '__main__':
    main()