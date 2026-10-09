import { test, expect } from '@playwright/test';

test('successful login opens dashboard and logout clears token', async ({ page }) => {
  const phone = '+94770000000';
  const token = 'test-guest-token';
  let bookingsRequested = false;

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
      expect(request.postDataJSON()).toEqual({ phone, otp: '789123' });
      await route.fulfill({
        status: 200,
        json: { token },
      });
      return;
    }

    if (path === '/api/v1/booking/' && request.method() === 'GET') {
      expect(request.headers()['authorization']).toBe(`Bearer ${token}`);
      bookingsRequested = true;
      await route.fulfill({ status: 200, json: [] });
      return;
    }

    await route.abort();
  });

  await page.goto('/login');
  await page.getByPlaceholder('+94 77 123 4567').fill(phone);
  await page.getByRole('button', { name: 'SEND OTP', exact: true }).click();

  const otpField = page.getByPlaceholder(
    'Enter the 6-digit code (demo: 789123)'
  );
  await expect(otpField).toBeVisible();
  await otpField.fill('789123');

  await page.getByRole('button', {
    name: 'VERIFY & LOGIN',
    exact: true,
  }).click();

  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(
    page.getByRole('heading', { name: 'MY ACCOUNT', exact: true })
  ).toBeVisible();

  await expect(
    page.getByText('You have no upcoming or past reservations.', {
      exact: true,
    })
  ).toBeVisible();

  expect(bookingsRequested).toBe(true);
  expect(
    await page.evaluate(() => localStorage.getItem('guest_token'))
  ).toBe(token);

  await page.getByRole('button', { name: 'LOGOUT', exact: true }).click();

  await expect(page).toHaveURL('http://127.0.0.1:3000/');
  expect(
    await page.evaluate(() => localStorage.getItem('guest_token'))
  ).toBeNull();
});

test('dashboard redirects guests without a token to login', async ({ page }) => {
  await page.route('**/api/v1/**', route => route.abort());

  await page.goto('/dashboard');

  await expect(page).toHaveURL(/\/login$/);
  await expect(
    page.getByRole('heading', { name: 'GUEST LOGIN', exact: true })
  ).toBeVisible();
});
