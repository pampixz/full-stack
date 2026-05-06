import { describe, test, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import ProtectedRoute from "./ProtectedRoute";

function renderWithRouter(role: string | null, token: string | null) {
  if (token) {
    localStorage.setItem("access_token", token);
  } else {
    localStorage.removeItem("access_token");
  }

  if (role) {
    localStorage.setItem("role", role);
  } else {
    localStorage.removeItem("role");
  }

  return render(
    <MemoryRouter initialEntries={["/entries"]}>
      <Routes>
        <Route element={<ProtectedRoute roles={["user", "admin"]} />}>
          <Route path="/entries" element={<div>Entries Page</div>} />
        </Route>
        <Route path="/login" element={<div>Login Page</div>} />
      </Routes>
    </MemoryRouter>
  );
}

describe("ProtectedRoute", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test("redirects to login when no token", () => {
    renderWithRouter(null, null);
    expect(screen.getByText("Login Page")).toBeInTheDocument();
  });

  test("allows access with correct role and token", () => {
    renderWithRouter("user", "fake-token");
    expect(screen.getByText("Entries Page")).toBeInTheDocument();
  });

  test("blocks access with wrong role", () => {
    localStorage.setItem("access_token", "fake-token");
    localStorage.setItem("role", "guest");

    render(
      <MemoryRouter initialEntries={["/entries"]}>
        <Routes>
          <Route element={<ProtectedRoute roles={["admin"]} />}>
            <Route path="/entries" element={<div>Entries Page</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText(/403/i)).toBeInTheDocument();
  });
});