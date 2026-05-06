import { test, expect } from "@playwright/test";
import path from "path";
import fs from "fs";

test("user can upload file for entry", async ({ page }) => {
  const email = `autotest_${Date.now()}@example.com`;
  const password = "123456";

  const filePath = path.join(process.cwd(), "e2e-test-file.txt");
  fs.writeFileSync(filePath, "Playwright file content", "utf-8");

  await page.goto("/register");

  await page.getByPlaceholder("Email").fill(email);
  await page.getByPlaceholder("Пароль (мин. 6 символов)").fill(password);
  await page.getByRole("button", { name: "Создать аккаунт" }).click();

  await expect(page).toHaveURL(/entries/);

  await page.goto("/entries/new");

  const uniqueText = `Запись с файлом ${Date.now()}`;
  await page.getByPlaceholder("Как ты сегодня?").fill(uniqueText);
  await page.getByPlaceholder(/теги через запятую/i).fill("file, autotest");
  await page.getByRole("button", { name: "Сохранить" }).click();

  await page.goto("/entries");

  const fileInput = page.locator('input[type="file"]').first();
  await fileInput.setInputFiles(filePath);

  await page.getByRole("button", { name: "Загрузить файл" }).first().click();

  await expect(page.getByText("e2e-test-file.txt")).toBeVisible();

  fs.unlinkSync(filePath);
});