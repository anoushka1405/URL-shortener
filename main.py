from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import engine, Base
from dependencies import get_db
from models import URL
from schemas import (
    ShortenRequest,
    ShortenResponse,
    AnalyticsResponse,
)
from config import BASE_URL
from services.base62 import encode_base62
from services.redis import get_cached_url, set_cached_url

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "URL shortener is alive"}


@app.post("/shorten", response_model=ShortenResponse)
def shorten_url(request: ShortenRequest, db: Session = Depends(get_db)):
    # Insert URL with a temporary placeholder
    new_url = URL(
        long_url=str(request.long_url),
        short_code="placeholder"
    )

    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    # Generate Base62 short code from database ID
    new_url.short_code = encode_base62(new_url.id)
    db.commit()
    db.refresh(new_url)

    return ShortenResponse(
        short_code=new_url.short_code,
        short_url=f"{BASE_URL}/{new_url.short_code}"
    )


@app.get("/{short_code}")
def redirect_to_long_url(short_code: str, db: Session = Depends(get_db)):

    # 1. Check Redis
    cached_url = get_cached_url(short_code)

    # 2. Always fetch the database row for analytics
    url_entry = db.query(URL).filter(URL.short_code == short_code).first()

    if url_entry is None:
        raise HTTPException(
            status_code=404,
            detail="Short code not found"
        )

    # 3. Decide which URL to use
    if cached_url:
        long_url = cached_url
    else:
        long_url = url_entry.long_url
        set_cached_url(
            short_code,
            long_url
        )

    # 4. Update analytics
    url_entry.click_count += 1
    db.commit()

    # 5. Redirect
    return RedirectResponse(
        url=long_url,
        status_code=302
    )

@app.get("/analytics/{short_code}", response_model=AnalyticsResponse)
def get_analytics(short_code: str, db: Session = Depends(get_db)):
    url_entry = db.query(URL).filter(URL.short_code == short_code).first()

    if url_entry is None:
        raise HTTPException(
            status_code=404,
            detail="Short code not found"
        )

    return AnalyticsResponse(
        short_code=url_entry.short_code,
        long_url=url_entry.long_url,
        click_count=url_entry.click_count,
        created_at=url_entry.created_at
    )