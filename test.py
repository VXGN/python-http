from typing import Any
import time
import httpx
from rich import print

BASE_URL = "https://httpbin.org/"

def fetch(c: httpx.Client) -> Any:
    r = c.get(f"{BASE_URL}/get")
    return r.json()

def post(c: httpx.Client) -> Any:
    r = c.post(f"{BASE_URL}/post")
    return r.json()

def update(c: httpx.Client) -> Any:
    r = c.put(f"{BASE_URL}/put")
    return r.json()

def delete (c: httpx.Client) -> Any:
    r = c.delete(f"{BASE_URL}/delete")
    return r.json()

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