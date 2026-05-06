from fastapi import APIRouter, Query
from backend.app.services.weather_service import WeatherService

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/")
async def get_weather(city: str = Query(..., min_length=2, max_length=100)):
    service = WeatherService()
    return await service.get_weather_by_city(city)