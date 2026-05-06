import { test, expect } from "@playwright/test";

test("user can create entry and see it in entries list", async ({ page }) => {
  const email = `autotest_${Date.now()}@example.com`;
  const password = "123456";

  await page.goto("/register");

  await page.getByPlaceholder("Email").fill(email);
  await page.getByPlaceholder("Пароль (мин. 6 символов)").fill(password);
  await page.getByRole("button", { name: "Создать аккаунт" }).click();

  await expect(page).toHaveURL(/entries/);

  await page.goto("/entries/new");

  const uniqueText = `Автотест запись ${Date.now()}`;

  await page.getByPlaceholder("Как ты сегодня?").fill(uniqueText);
  await page.getByPlaceholder(/теги через запятую/i).fill("autotest, lab5");
  await page.getByRole("button", { name: "Сохранить" }).click();

  await page.goto("/entries");

  await expect(page.getByText(uniqueText)).toBeVisible();
});