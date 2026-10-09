import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.goto('/login');
});

test('shows the guest login form', async ({ page }) => {
  await expect(
    page.getByRole('heading', { name: 'GUEST LOGIN' })
  ).toBeVisible();

  await expect(
    page.getByPlaceholder('+94 77 123 4567')
  ).toBeVisible();

  await expect(
    page.getByRole('button', { name: 'SEND OTP', exact: true })
  ).toBeEnabled();
});

test('rejects a short phone number without calling the API', async ({ page }) => {
  const requests: string[] = [];

  page.on('request', request => {
    if (['fetch', 'xhr'].includes(request.resourceType())) {
      requests.push(request.url());
    }
  });

  await page.getByPlaceholder('+94 77 123 4567').fill('123');
  await page.getByRole('button', { name: 'SEND OTP', exact: true }).click();

  await expect(
    page.getByText('Please enter a valid phone number', { exact: true })
  ).toBeVisible();

  await expect(
    page.getByRole('button', { name: 'SEND OTP', exact: true })
  ).toBeVisible();

  expect(requests).toEqual([]);
});
