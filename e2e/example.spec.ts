import { test, expect } from '@playwright/test';

test('homepage redirects to login', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/Content Manager/);
  await expect(page).toHaveURL(/\/login/);
});

test('login form is visible', async ({ page }) => {
  await page.goto('/login');
  await expect(page.locator('input[name="username"]')).toBeVisible();
  await expect(page.locator('input[name="password"]')).toBeVisible();
  await expect(page.locator('button[type="submit"]')).toBeVisible();
});
