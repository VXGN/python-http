import asyncio
import time
import httpx

BASE_URL = "https://httpbin.org"

async def fetch(c): return (await c.get(f"{BASE_URL}/get")).text
async def post(c): return (await c.post(f"{BASE_URL}/post")).text
async def update(c): return (await c.put(f"{BASE_URL}/put")).text
async def delete(c): return (await c.delete(f"{BASE_URL}/delete")).text

async def perform_operations(c):
    await asyncio.gather(fetch(c), post(c), update(c), delete(c))

async def worker(iterations, client):
    tasks = []
    for _ in range(iterations):
        tasks += [
            asyncio.create_task(fetch(client)),
            asyncio.create_task(post(client)),
            asyncio.create_task(update(client)),
            asyncio.create_task(delete(client)),
        ]
    await asyncio.gather(*tasks)

async def main_async():
    start = time.perf_counter()

    async with httpx.AsyncClient(
        http2=False,
        limits=httpx.Limits(max_connections=1000, max_keepalive_connections=200),
        timeout=5.0,
    ) as client:
        await asyncio.gather(*(worker(25, client) for _ in range(4)))

    print(f"time taken {time.perf_counter() - start:.2f} seconds")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
