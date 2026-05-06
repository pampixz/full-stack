import { test, expect } from "@playwright/test";

test("register and login flow works", async ({ page }) => {
  const email = `autotest_${Date.now()}@example.com`;
  const password = "123456";

  await page.goto("/register");

  await page.getByPlaceholder("Email").fill(email);
  await page.getByPlaceholder("Пароль (мин. 6 символов)").fill(password);
  await page.getByRole("button", { name: "Создать аккаунт" }).click();

  await expect(page).toHaveURL(/entries/);
  await expect(page.getByRole("heading", { name: "Мои записи" })).toBeVisible();
});