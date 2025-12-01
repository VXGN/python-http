from typing import Any
import time
import httpx
from rich import print
import asyncio

BASE_URL = "https://httpbin.org/"


async def fetch(c: httpx.AsyncClient) -> Any:
    try:
        r = await c.get(f"{BASE_URL}/get")
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

async def post(c: httpx.AsyncClient) -> Any:
    try:
        r = await c.post(f"{BASE_URL}/post")
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

async def update(c: httpx.AsyncClient) -> Any:
    try:
        r = await c.put(f"{BASE_URL}/put")
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

async def delete(c: httpx.AsyncClient) -> Any:
    try:
        r = await c.delete(f"{BASE_URL}/delete")
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

async def perform_operations(c: httpx.AsyncClient) -> None:
    await asyncio.gather(
        fetch(c),
        post(c),
        update(c),
        delete(c),
    )

async def worker(total: int) -> None:
    async with httpx.AsyncClient() as c:
        await asyncio.gather(*(perform_operations(c) for _ in range(total)))

async def main_async() -> None:
    start = time.perf_counter()

    workers = 4
    iterations = 25

    await asyncio.gather(*(worker(iterations) for _ in range(workers)))

    end = time.perf_counter()
    print(f"time taken {end - start:.2f} seconds")
    print(f"Used {workers} workers with {iterations} iterations each")

def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
