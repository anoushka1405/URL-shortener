from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import random
import string

app = FastAPI()

url_store = {}

class ShortenRequest(BaseModel):
    long_url: str

def generate_short_code(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))

@app.get("/")
def read_root():
    return {"message": "URL shortener is alive"}

@app.post("/shorten")
def shorten_url(request: ShortenRequest):
    short_code = generate_short_code()
    url_store[short_code] = request.long_url
    return {"short_code": short_code, "short_url": f"http://127.0.0.1:8000/{short_code}"}

@app.get("/{short_code}")
def redirect_to_long_url(short_code: str):
    long_url = url_store.get(short_code)
    if long_url is None:
        raise HTTPException(status_code=404, detail="short code not found")
    return RedirectResponse(url=long_url, status_code=302)