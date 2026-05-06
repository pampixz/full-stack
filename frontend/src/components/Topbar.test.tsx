import { describe, test, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Topbar from "./Topbar";

describe("Topbar", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test("shows login button when user is not authenticated", () => {
    render(
      <MemoryRouter>
        <Topbar />
      </MemoryRouter>
    );

    expect(screen.getByText("Войти")).toBeInTheDocument();
  });

  test("shows logout button when user is authenticated", () => {
    localStorage.setItem("access_token", "fake-token");

    render(
      <MemoryRouter>
        <Topbar />
      </MemoryRouter>
    );

    expect(screen.getByText("Выйти")).toBeInTheDocument();
  });
});