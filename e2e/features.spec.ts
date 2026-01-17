import { test, expect, Page } from '@playwright/test';

// Helper function to login
async function login(page: Page) {
  await page.goto('/login');
  await page.fill('input[name="username"]', 'admin');
  await page.fill('input[name="password"]', 'change_this_password');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/');
}

test.describe('Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('sidebar navigation links work', async ({ page }) => {
    // Dashboard
    await page.click('a[href="/"]');
    await expect(page).toHaveURL('/');

    // Content Queue
    await page.click('a[href="/queue"]');
    await expect(page).toHaveURL('/queue');
    await expect(page.getByRole('heading', { name: 'Content Queue' })).toBeVisible();

    // Documents
    await page.click('a[href="/documents"]');
    await expect(page).toHaveURL('/documents');
    await expect(page.getByRole('heading', { name: 'Document Management' })).toBeVisible();

    // Generate
    await page.click('a[href="/generate"]');
    await expect(page).toHaveURL('/generate');
    await expect(page.getByRole('heading', { name: 'Generate Content' })).toBeVisible();

    // Chat
    await page.click('a[href="/chat"]');
    await expect(page).toHaveURL('/chat');
    await expect(page.getByRole('heading', { name: 'Chat', exact: true })).toBeVisible();
  });

  test('all pages require authentication', async ({ page }) => {
    // Clear cookies to log out
    await page.context().clearCookies();

    const protectedPages = ['/queue', '/documents', '/generate', '/chat', '/calendar', '/history', '/settings'];

    for (const pagePath of protectedPages) {
      await page.goto(pagePath);
      await expect(page).toHaveURL(/\/login/);
    }
  });
});

test.describe('Chat Feature', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await page.goto('/chat');
  });

  test('chat page loads with welcome screen', async ({ page }) => {
    await expect(page.locator('text=Welcome to Content Manager Chat')).toBeVisible();
    await expect(page.getByRole('button', { name: 'New Conversation' })).toBeVisible();
  });

  test('new conversation button is visible', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'New Conversation' })).toBeVisible();
  });

  test('quick action buttons are visible', async ({ page }) => {
    await expect(page.locator('span:has-text("Ask a Question")')).toBeVisible();
    await expect(page.locator('span:has-text("Get Topic Ideas")')).toBeVisible();
    await expect(page.locator('button span:has-text("Generate Content")')).toBeVisible();
    await expect(page.locator('span:has-text("Explore a Section")')).toBeVisible();
  });

  test('conversations sidebar shows empty state initially', async ({ page }) => {
    await expect(page.locator('text=No conversations yet')).toBeVisible();
  });
});

test.describe('Content Generation', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await page.goto('/generate');
  });

  test('generate page loads with form elements', async ({ page }) => {
    await expect(page.locator('h3:has-text("Create Educational Content")')).toBeVisible();
    await expect(page.locator('label:has-text("Generation Mode")')).toBeVisible();
    await expect(page.locator('label:has-text("Content Type")')).toBeVisible();
  });

  test('generation mode dropdown has all options', async ({ page }) => {
    const modeSelect = page.locator('select').first();
    await expect(modeSelect).toBeVisible();

    // Check options exist
    await expect(modeSelect.locator('option[value="user_provided"]')).toHaveText('User Provided Topic');
    await expect(modeSelect.locator('option[value="bot_proposed"]')).toHaveText('Bot Suggested Topic');
    await expect(modeSelect.locator('option[value="historical"]')).toHaveText('Historical Event');
  });

  test('content type radio buttons are visible', async ({ page }) => {
    await expect(page.locator('input[value="tweet"]')).toBeVisible();
    await expect(page.locator('input[value="thread"]')).toBeVisible();
    await expect(page.locator('input[value="script"]')).toBeVisible();
  });

  test('topic input field is visible for user provided mode', async ({ page }) => {
    await expect(page.locator('input[placeholder*="Right to equality"]')).toBeVisible();
  });

  test('specific sections input is visible', async ({ page }) => {
    await expect(page.locator('input[placeholder*="9, 10, 11"]')).toBeVisible();
  });
});

test.describe('Content Queue', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await page.goto('/queue');
  });

  test('queue page loads with header', async ({ page }) => {
    await expect(page.locator('text=Review and approve content before posting')).toBeVisible();
  });

  test('generate new content link is visible', async ({ page }) => {
    await expect(page.locator('a[href="/generate"]:has-text("Generate New Content")')).toBeVisible();
  });

  test('filter tabs are visible', async ({ page }) => {
    // Use more specific selectors for filter tab buttons
    const filterNav = page.locator('nav.-mb-px');
    await expect(filterNav.locator('button:has-text("Pending")')).toBeVisible();
    await expect(filterNav.locator('button:has-text("Approved")')).toBeVisible();
    await expect(filterNav.locator('button:has-text("Scheduled")')).toBeVisible();
    await expect(filterNav.locator('button:has-text("All")')).toBeVisible();
  });

  test('search input is visible', async ({ page }) => {
    await expect(page.locator('input[placeholder*="Search by topic"]')).toBeVisible();
  });

  test('content type filter dropdown is visible', async ({ page }) => {
    const typeFilter = page.locator('select:has(option[value="tweet"])');
    await expect(typeFilter).toBeVisible();
    await expect(typeFilter.locator('option[value=""]')).toHaveText('All types');
    await expect(typeFilter.locator('option[value="tweet"]')).toHaveText('Tweet');
    await expect(typeFilter.locator('option[value="thread"]')).toHaveText('Thread');
    await expect(typeFilter.locator('option[value="script"]')).toHaveText('Script');
  });

  test('can switch between filter tabs', async ({ page }) => {
    const filterNav = page.locator('nav.-mb-px');

    // Click Approved tab
    await filterNav.locator('button:has-text("Approved")').click();
    await expect(filterNav.locator('button:has-text("Approved")')).toHaveClass(/border-green-500/);

    // Click Scheduled tab
    await filterNav.locator('button:has-text("Scheduled")').click();
    await expect(filterNav.locator('button:has-text("Scheduled")')).toHaveClass(/border-green-500/);

    // Click All tab
    await filterNav.locator('button:has-text("All")').click();
    await expect(filterNav.locator('button:has-text("All")')).toHaveClass(/border-green-500/);

    // Click back to Pending
    await filterNav.locator('button:has-text("Pending")').click();
    await expect(filterNav.locator('button:has-text("Pending")')).toHaveClass(/border-green-500/);
  });
});

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('dashboard shows stats cards', async ({ page }) => {
    // Stats cards have specific dt labels
    await expect(page.locator('dt:has-text("Pending Content")')).toBeVisible();
    await expect(page.locator('dt:has-text("Total Posts")')).toBeVisible();
    await expect(page.locator('dt:has-text("Document")')).toBeVisible();
  });

  test('quick actions are visible', async ({ page }) => {
    // Check for links to main features in main content area
    await expect(page.locator('main a[href="/generate"]').first()).toBeVisible();
  });
});

test.describe('Settings Page', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await page.goto('/settings');
  });

  test('settings page loads', async ({ page }) => {
    await expect(page).toHaveURL('/settings');
    await expect(page.getByRole('heading', { name: 'Settings', exact: true })).toBeVisible();
  });
});

test.describe('History Page', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await page.goto('/history');
  });

  test('history page loads', async ({ page }) => {
    await expect(page).toHaveURL('/history');
    await expect(page.getByRole('heading', { name: 'Post History' })).toBeVisible();
  });
});

test.describe('Calendar Page', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await page.goto('/calendar');
  });

  test('calendar page loads', async ({ page }) => {
    await expect(page).toHaveURL('/calendar');
    await expect(page.getByRole('heading', { name: 'Content Calendar' })).toBeVisible();
  });
});

test.describe('Logout', () => {
  test('can logout successfully', async ({ page }) => {
    await login(page);

    // Click logout
    await page.goto('/logout');

    // Should redirect to login
    await expect(page).toHaveURL(/\/login/);

    // Try to access protected page
    await page.goto('/');
    await expect(page).toHaveURL(/\/login/);
  });
});
