import pytest
import httpx
from fastapi import HTTPException

from backend.app.services.weather_service import WeatherService


class MockResponse:
    def __init__(self, status_code: int, json_data: dict | list):
        self.status_code = status_code
        self._json_data = json_data

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                message="HTTP error",
                request=None,
                response=None,
            )


@pytest.fixture
def weather_service(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "fake_key")
    return WeatherService()


@pytest.mark.asyncio
async def test_get_weather_by_city_success(weather_service, monkeypatch):
    geo_response = [
        {
            "name": "Moscow",
            "country": "RU",
            "lat": 55.75,
            "lon": 37.62,
        }
    ]

    weather_response = {
        "main": {
            "temp": 12.5,
            "feels_like": 10.0,
            "humidity": 60,
        },
        "weather": [
            {
                "description": "пасмурно",
                "icon": "04d",
            }
        ],
        "wind": {
            "speed": 4.5,
        },
    }

    calls = {"count": 0}

    async def mock_get(self, url, params=None, timeout=None):
        calls["count"] += 1
        if calls["count"] == 1:
            return MockResponse(200, geo_response)
        return MockResponse(200, weather_response)

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    result = await weather_service.get_weather_by_city("Moscow")

    assert result["city"] == "Moscow"
    assert result["country"] == "RU"
    assert result["temperature"] == 12.5
    assert result["feels_like"] == 10.0
    assert result["description"] == "пасмурно"
    assert result["humidity"] == 60
    assert result["wind_speed"] == 4.5
    assert result["icon"] == "04d"


@pytest.mark.asyncio
async def test_get_weather_city_not_found(weather_service, monkeypatch):
    async def mock_get(self, url, params=None, timeout=None):
        return MockResponse(200, [])

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    with pytest.raises(HTTPException) as exc:
        await weather_service.get_weather_by_city("UnknownCity")

    assert exc.value.status_code == 404
    assert exc.value.detail == "City not found"


@pytest.mark.asyncio
async def test_invalid_api_key(weather_service, monkeypatch):
    async def mock_get(self, url, params=None, timeout=None):
        return MockResponse(401, {"message": "Invalid API key"})

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    with pytest.raises(HTTPException) as exc:
        await weather_service.get_weather_by_city("Moscow")

    assert exc.value.status_code == 502
    assert exc.value.detail == "Invalid weather API key"


@pytest.mark.asyncio
async def test_rate_limit_exceeded(weather_service, monkeypatch):
    async def mock_get(self, url, params=None, timeout=None):
        return MockResponse(429, {"message": "Too many requests"})

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    with pytest.raises(HTTPException) as exc:
        await weather_service.get_weather_by_city("Moscow")

    assert exc.value.status_code == 502
    assert exc.value.detail == "Weather API rate limit exceeded"


@pytest.mark.asyncio
async def test_weather_api_timeout(weather_service, monkeypatch):
    async def mock_get(self, url, params=None, timeout=None):
        raise httpx.TimeoutException("Timeout")

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    with pytest.raises(HTTPException) as exc:
        await weather_service.get_weather_by_city("Moscow")

    assert exc.value.status_code == 502
    assert exc.value.detail == "Weather API timeout"