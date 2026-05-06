import os
import asyncio
import httpx
from fastapi import HTTPException


class WeatherService:
    GEO_URL = "http://api.openweathermap.org/geo/1.0/direct"
    WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise HTTPException(
                status_code=500,
                detail="OPENWEATHER_API_KEY is not configured"
            )

    async def _get_with_retry(
        self,
        client: httpx.AsyncClient,
        url: str,
        params: dict,
        retries: int = 2,
    ):
        for attempt in range(retries + 1):
            try:
                response = await client.get(url, params=params, timeout=8.0)

                if response.status_code == 401:
                    raise HTTPException(
                        status_code=502,
                        detail="Invalid weather API key"
                    )

                if response.status_code == 404:
                    raise HTTPException(
                        status_code=404,
                        detail="City not found"
                    )

                if response.status_code == 429:
                    raise HTTPException(
                        status_code=502,
                        detail="Weather API rate limit exceeded"
                    )

                response.raise_for_status()
                return response.json()

            except HTTPException:
                raise
            except httpx.TimeoutException:
                if attempt < retries:
                    await asyncio.sleep(1)
                else:
                    raise HTTPException(
                        status_code=502,
                        detail="Weather API timeout"
                    )
            except httpx.HTTPError:
                if attempt < retries:
                    await asyncio.sleep(1)
                else:
                    raise HTTPException(
                        status_code=502,
                        detail="External weather service is unavailable"
                    )

    async def get_weather_by_city(self, city: str) -> dict:
        async with httpx.AsyncClient() as client:
            geo_data = await self._get_with_retry(
                client,
                self.GEO_URL,
                {
                    "q": city,
                    "limit": 1,
                    "appid": self.api_key,
                },
            )

            if not geo_data:
                raise HTTPException(status_code=404, detail="City not found")

            location = geo_data[0]
            lat = location["lat"]
            lon = location["lon"]

            weather_data = await self._get_with_retry(
                client,
                self.WEATHER_URL,
                {
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key,
                    "units": "metric",
                    "lang": "ru",
                },
            )

            return {
                "city": location["name"],
                "country": location.get("country"),
                "temperature": weather_data["main"]["temp"],
                "feels_like": weather_data["main"]["feels_like"],
                "description": weather_data["weather"][0]["description"],
                "humidity": weather_data["main"]["humidity"],
                "wind_speed": weather_data["wind"]["speed"],
                "icon": weather_data["weather"][0]["icon"],
            }