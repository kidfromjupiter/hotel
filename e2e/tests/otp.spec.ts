import { test, expect } from '@playwright/test';

const phone = '+94770000000';
const otpPlaceholder = 'Enter the 6-digit code (demo: 789123)';

test.beforeEach(async ({ page }) => {
  // Intercept API calls before loading the page.
  await page.route('**/api/v1/**', async route => {
    const request = route.request();
    const path = new URL(request.url()).pathname;

    if (path === '/api/v1/otp/send' && request.method() === 'POST') {
      expect(request.postDataJSON()).toEqual({ phone });

      await route.fulfill({
        status: 200,
        json: { message: 'Test OTP sent' },
      });
      return;
    }

    if (path === '/api/v1/otp/verify' && request.method() === 'POST') {
      expect(request.postDataJSON()).toEqual({
        phone,
        otp: '000000',
      });

      await route.fulfill({
        status: 400,
        json: { message: 'Invalid OTP' },
      });
      return;
    }

    // Prevent any unexpected API call from reaching the backend.
    await route.abort();
  });

  await page.goto('/login');
});

async function openOtpForm(page: import('@playwright/test').Page) {
  await page.getByPlaceholder('+94 77 123 4567').fill(phone);
  await page.getByRole('button', {
    name: 'SEND OTP',
    exact: true,
  }).click();

  await expect(page.getByPlaceholder(otpPlaceholder)).toBeVisible();
}

test('sending OTP opens the code entry form', async ({ page }) => {
  await openOtpForm(page);

  await expect(
    page.getByText('Test OTP sent', { exact: true })
  ).toBeVisible();

  await expect(
    page.getByRole('button', { name: 'VERIFY & LOGIN', exact: true })
  ).toBeEnabled();
});

test('short OTP is rejected without a verification request', async ({ page }) => {
  await openOtpForm(page);

  let verificationRequests = 0;
  page.on('request', request => {
    if (new URL(request.url()).pathname === '/api/v1/otp/verify') {
      verificationRequests++;
    }
  });

  await page.getByPlaceholder(otpPlaceholder).fill('12');
  await page.getByRole('button', {
    name: 'VERIFY & LOGIN',
    exact: true,
  }).click();

  await expect(
    page.getByText('Please enter a valid OTP', { exact: true })
  ).toBeVisible();

  expect(verificationRequests).toBe(0);
});

test('invalid OTP response keeps the guest on login', async ({ page }) => {
  await openOtpForm(page);

  await page.getByPlaceholder(otpPlaceholder).fill('000000');
  await page.getByRole('button', {
    name: 'VERIFY & LOGIN',
    exact: true,
  }).click();

  await expect(
    page.getByText('Invalid OTP', { exact: true })
  ).toBeVisible();

  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByPlaceholder(otpPlaceholder)).toBeVisible();

  expect(
    await page.evaluate(() => localStorage.getItem('guest_token'))
  ).toBeNull();
});
