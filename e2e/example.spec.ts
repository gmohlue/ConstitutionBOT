import { test, expect } from '@playwright/test';
import path from 'path';

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

test('can login with valid credentials', async ({ page }) => {
  await page.goto('/login');
  // Wait for login form to be ready
  await expect(page.locator('input[name="username"]')).toBeVisible();
  await page.fill('input[name="username"]', 'admin');
  await page.fill('input[name="password"]', 'change_this_password');
  await page.click('button[type="submit"]');

  // Wait for redirect with extended timeout for slower environments
  await expect(page).toHaveURL('/', { timeout: 10000 });
  await expect(page).toHaveTitle(/Dashboard/);
});

test('can upload document', async ({ page }) => {
  // Login first
  await page.goto('/login');
  await expect(page.locator('input[name="username"]')).toBeVisible();
  await page.fill('input[name="username"]', 'admin');
  await page.fill('input[name="password"]', 'change_this_password');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/', { timeout: 10000 });

  // Navigate to documents page
  await page.goto('/documents');
  await expect(page.locator('h3:has-text("Upload Document")')).toBeVisible({ timeout: 10000 });

  // Upload the SA Constitution PDF
  const filePath = path.resolve(__dirname, '../data/constitution/uploads/SAConstitution-web-eng.pdf');
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles(filePath);

  // Wait for upload to complete and verify success
  await expect(page.locator('text=Document loaded')).toBeVisible({ timeout: 30000 });
  await expect(page.locator('text=sections indexed')).toBeVisible({ timeout: 10000 });
});
