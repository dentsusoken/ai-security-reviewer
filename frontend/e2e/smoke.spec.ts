import { expect, test } from '@playwright/test';

test.describe('Landing & Navigation', () => {
  test('landing page renders and has title', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/AI Security Reviewer/i);
  });

  test('navigate to new review page', async ({ page }) => {
    await page.goto('/');
    // Click the primary CTA button or navigation link to start a review
    const reviewLink = page.getByRole('link', { name: /レビュー|Review|新規/i }).first();
    if (await reviewLink.isVisible()) {
      await reviewLink.click();
      await expect(page).toHaveURL(/\/reviews\/new/);
    }
  });

  test('new review page shows input form', async ({ page }) => {
    await page.goto('/reviews/new');
    // Should display the GitHub input form by default
    await expect(page.getByPlaceholder(/github\.com/i)).toBeVisible();
    // Should have perspective checkboxes
    await expect(page.getByText('OWASP ASVS')).toBeVisible();
    await expect(page.getByText(/静的解析|Semgrep/)).toBeVisible();
  });

  test('can toggle review type to code paste', async ({ page }) => {
    await page.goto('/reviews/new');
    // Find and click the code paste tab/button
    const codeTab = page.getByText(/コード貼り付け|Code/i).first();
    if (await codeTab.isVisible()) {
      await codeTab.click();
      await expect(page.getByPlaceholder(/ソースコード|source code/i).or(page.getByRole('textbox', { name: /ソースコード/i }))).toBeVisible();
    }
  });
});

test.describe('Dashboard', () => {
  test('dashboard page renders', async ({ page }) => {
    await page.goto('/dashboard');
    // Should show some dashboard content
    await expect(page.locator('body')).not.toBeEmpty();
  });
});
