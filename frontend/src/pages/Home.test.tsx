import { describe, test, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Home from "./Home";

vi.mock("../shared/api", () => ({
  api: {
    get: vi.fn(),
  },
}));

import { api } from "../shared/api";

describe("Home page", () => {
  test("shows loading state initially", () => {
    (api.get as any).mockReturnValue(new Promise(() => {}));

    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>
    );

    expect(screen.getByText(/Загрузка данных о погоде/i)).toBeInTheDocument();
  });

  test("shows weather data on success", async () => {
    (api.get as any).mockResolvedValue({
      data: {
        city: "Moscow",
        country: "RU",
        temperature: 10,
        feels_like: 8,
        description: "пасмурно",
        humidity: 70,
        wind_speed: 4,
        icon: "04d",
      },
    });

    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Moscow/i)).toBeInTheDocument();
      expect(screen.getByText(/Температура: 10°C/i)).toBeInTheDocument();
    });
  });

  test("shows error state when weather request fails", async () => {
    (api.get as any).mockRejectedValue({
      response: {
        data: {
          detail: "External weather service is unavailable",
        },
      },
    });

    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(
        screen.getByText(/Не удалось получить актуальную погоду/i)
      ).toBeInTheDocument();
    });
  });
});