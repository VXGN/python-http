from typing import Any
import time
import httpx
from rich import print

BASE_URL = "https://httpbin.org/"

def fetch(c: httpx.Client) -> Any:
    try:
        r.raise_for_status()
        r = c.get(f"{BASE_URL}/get")
        return r.json()
    except httpx.HTTPStatusError as e:
        print(f"Error fetching data: {e}")
        return None

def post(c: httpx.Client) -> Any:
    try:
        r = c.post(f"{BASE_URL}/post")
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        print (f"Error posting data: {e}")
        return None

def update(c: httpx.Client) -> Any:
    try:
        r = c.put(f"{BASE_URL}/put")
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        print(f"Error updating data: {e}")
        return None

def delete (c: httpx.Client) -> Any:
    try:
        r = c.delete(f"{BASE_URL}/delete")
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        print(f"Error deleting data: {e}")
        return None

def main() -> None:
    start = time.perf_counter()
    
    with httpx.Client() as c:
        print("Get :", fetch(c))
        print("Post :", post(c))
        print("Put :", update(c))
        print("Delete :", delete(c))
        
    end = time.perf_counter()

    print(f"time taken {end - start:.2f} seconds")

if __name__ == '__main__':
    main()