import asyncio
import time
import httpx
import asyncpg
import aioredis
from tqdm.asyncio import tqdm
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = "https://httpbin.org"
JWT_URL = os.getenv("JWT_URL")
JWT_USERNAME = os.getenv("JWT_USERNAME")
JWT_PASSWORD = os.getenv("JWT_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
CDN_UPLOAD_URL = os.getenv("CDN_UPLOAD_URL")

class HTTPError(Exception):
    pass

async def get_redis():
    return await aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", decode_responses=True)

async def get_db_pool():
    return await asyncpg.create_pool(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        min_size=2,
        max_size=10
    )

async def get_jwt_token(client: httpx.AsyncClient, redis):
    token = await redis.get("jwt")
    if token:
        return token
    r = await client.post(JWT_URL, data={"username": JWT_USERNAME, "password": JWT_PASSWORD})
    r.raise_for_status()
    token = r.json().get("access_token")
    if not token:
        raise HTTPError("Failed to get JWT token")
    await redis.set("jwt", token, ex=3600)
    return token

async def fetch(c, token):
    try:
        r = await c.get(f"{BASE_URL}/get", headers={"Authorization": f"Bearer {token}"})
        r.raise_for_status()
        return r.text
    except:
        return None

async def post(c, token):
    try:
        r = await c.post(f"{BASE_URL}/post", headers={"Authorization": f"Bearer {token}"})
        r.raise_for_status()
        return r.text
    except:
        return None

async def patch(c, token):
    try:
        r = await c.patch(f"{BASE_URL}/patch", headers={"Authorization": f"Bearer {token}"})
        r.raise_for_status()
        return r.text
    except:
        return None

async def update(c, token):
    try:
        r = await c.put(f"{BASE_URL}/put", headers={"Authorization": f"Bearer {token}"})
        r.raise_for_status()
        return r.text
    except:
        return None

async def delete(c, token):
    try:
        r = await c.delete(f"{BASE_URL}/delete", headers={"Authorization": f"Bearer {token}"})
        r.raise_for_status()
        return r.text
    except:
        return None

async def head(c, token):
    try:
        r = await c.head(f"{BASE_URL}/get", headers={"Authorization": f"Bearer {token}"})
        r.raise_for_status()
        return str(r.headers)
    except:
        return None

async def upload_file(c, token):
    try:
        files = {"file": ("upload.txt", b"cdn test", "text/plain")}
        r = await c.post(CDN_UPLOAD_URL, files=files, headers={"Authorization": f"Bearer {token}"})
        r.raise_for_status()
        return r.text
    except:
        return None

async def worker(iterations, client, semaphore, token, db_pool, redis):
    async def limited(coro):
        async with semaphore:
            return await coro

    tasks = []
    for _ in range(iterations):
        tasks.extend([
            limited(fetch(client, token)),
            limited(post(client, token)),
            limited(patch(client, token)),
            limited(update(client, token)),
            limited(delete(client, token)),
            limited(head(client, token)),
            limited(upload_file(client, token)),
        ])

    results = []
    for coro in tqdm.as_completed(tasks, total=len(tasks), desc="Processing"):
        results.append(await coro)

    return results

async def main_async():
    start = time.perf_counter()

    redis = await get_redis()
    db_pool = await get_db_pool()

    async with httpx.AsyncClient(
        http2=True,
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20, keepalive_expiry=30.0),
        timeout=httpx.Timeout(10.0, connect=5.0),
    ) as client:
        token = await get_jwt_token(client, redis)
        semaphore = asyncio.Semaphore(50)
        workers = [worker(10, client, semaphore, token, db_pool, redis) for _ in range(4)]
        all_results = await asyncio.gather(*workers)

        total = sum(len(r) for r in all_results)
        success = sum(1 for r in all_results for x in r if x is not None)
        failed = total - success
        elapsed = time.perf_counter() - start

        print("\n" + "="*50)
        print(f"Time taken: {elapsed:.2f}")
        print(f"Total requests: {total}")
        print(f"Successful: {success}")
        print(f"Failed: {failed}")
        print(f"Requests/sec: {total/elapsed:.2f}")
        print("="*50)

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
