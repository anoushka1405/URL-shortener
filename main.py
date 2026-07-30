from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import string

app = FastAPI()

url_store = {}
BASE62_ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase

# temporary stand-in for a real database auto-increment ID
next_id = 1

class ShortenRequest(BaseModel):
    long_url: str

def encode_base62(num: int) -> str:
    if num == 0:
        return BASE62_ALPHABET[0]
    digits = []
    while num > 0:
        remainder = num % 62
        digits.append(BASE62_ALPHABET[remainder])
        num = num // 62
    digits = digits[::-1]
    return "".join(digits)

@app.get("/")
def read_root():
    return {"message": "URL shortener is alive"}

@app.post("/shorten")
def shorten_url(request: ShortenRequest):
    global next_id
    short_code = encode_base62(next_id)
    url_store[short_code] = request.long_url
    next_id += 1
    return {"short_code": short_code, "short_url": f"http://127.0.0.1:8000/{short_code}"}

@app.get("/{short_code}")
def redirect_to_long_url(short_code: str):
    long_url = url_store.get(short_code)
    if long_url is None:
        raise HTTPException(status_code=404, detail="short code not found")
    return RedirectResponse(url=long_url, status_code=302)