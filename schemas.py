from pydantic import BaseModel, HttpUrl
from datetime import datetime


class ShortenRequest(BaseModel):
    long_url: HttpUrl


class ShortenResponse(BaseModel):
    short_code: str
    short_url: str

class AnalyticsResponse(BaseModel):
    short_code: str
    long_url: HttpUrl
    click_count: int
    created_at: datetime