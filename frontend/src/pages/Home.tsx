import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import Seo from "../shared/Seo";
import { api } from "../shared/api";

type WeatherData = {
  city: string;
  country: string;
  temperature: number;
  feels_like: number;
  description: string;
  humidity: number;
  wind_speed: number;
  icon: string;
};

export default function Home() {
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loadingWeather, setLoadingWeather] = useState(true);
  const [weatherError, setWeatherError] = useState<string | null>(null);

  useEffect(() => {
    loadWeather();
  }, []);

  const loadWeather = async () => {
    try {
      setLoadingWeather(true);
      setWeatherError(null);

      const res = await api.get("/weather", {
        params: {
          city: "Moscow",
        },
      });

      setWeather(res.data);
    } catch (err: any) {
      console.error("Weather error:", err);
      setWeatherError(
        err?.response?.data?.detail || "Не удалось получить данные о погоде"
      );
      setWeather(null);
    } finally {
      setLoadingWeather(false);
    }
  };

  return (
    <section>
      <Seo
        title="Whisper Mood — дневник настроения и поддержка"
        description="Whisper Mood — веб-приложение для ведения дневника настроения, хранения личных записей, участия в комнатах поддержки и планирования встреч."
        canonical="/"
        ogTitle="Whisper Mood — дневник настроения"
        ogDescription="Личный дневник настроения, записи, поддержка и встречи в одном приложении."
      />

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "WebApplication",
            name: "Whisper Mood",
            applicationCategory: "HealthApplication",
            operatingSystem: "Web",
            description:
              "Whisper Mood — приложение для личных записей, тегирования, комнат поддержки и встреч.",
            url: "http://localhost:5173/",
          }),
        }}
      />

      <header>
        <h1>Дневник настроения 🕊</h1>
        <p>
          Whisper Mood — приложение для личных записей, тегирования,
          комнат поддержки и встреч.
        </p>
      </header>

      <section className="card" style={{ marginBottom: 20 }}>
        <h2 style={{ marginTop: 0 }}>Погода в Москве</h2>

        {loadingWeather && <p>Загрузка данных о погоде...</p>}

        {!loadingWeather && weatherError && (
          <div>
            <p className="muted">Не удалось получить актуальную погоду.</p>
            <p className="muted">{weatherError}</p>
          </div>
        )}

        {!loadingWeather && !weatherError && weather && (
          <div>
            <p>
              <strong>{weather.city}</strong>
              {weather.country ? `, ${weather.country}` : ""}
            </p>
            <p>Температура: {weather.temperature}°C</p>
            <p>Ощущается как: {weather.feels_like}°C</p>
            <p>Состояние: {weather.description}</p>
            <p>Влажность: {weather.humidity}%</p>
            <p>Скорость ветра: {weather.wind_speed} м/с</p>
          </div>
        )}
      </section>

      <section>
        <h2>Основные возможности</h2>
        <ul className="cards">
          <li>
            <Link to="/entries/new">Создать запись</Link>
          </li>
          <li>
            <Link to="/entries">Мои записи</Link>
          </li>
          <li>
            <Link to="/rooms">Комнаты поддержки</Link>
          </li>
          <li>
            <Link to="/meetings">Встречи</Link>
          </li>
        </ul>
      </section>

      <section>
        <h2>Для чего подходит приложение</h2>
        <p>
          Сервис помогает фиксировать эмоции, сохранять личные заметки,
          структурировать мысли по тегам и использовать дополнительные
          инструменты поддержки.
        </p>
      </section>
    </section>
  );
}