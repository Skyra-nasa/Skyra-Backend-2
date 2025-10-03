from pydantic import BaseModel, Field
from datetime import date

class WeatherRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    future_date: date

class ExportResponse(BaseModel):
    filename: str
    content: str  # Base64 or CSV/JSON string
