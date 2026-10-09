import { test, expect } from '@playwright/test';

test('guest completes a two-night Colombo booking', async ({ page }) => {
  const checkIn = new Date(Date.now() + 7 * 86400000)
    .toISOString().slice(0, 10);
  const checkOut = new Date(Date.now() + 9 * 86400000)
    .toISOString().slice(0, 10);

  const phone = '+94770000000';
  const reference = 'TEST-SKN-001';
  const calls: string[] = [];

  await page.route('**/api/v1/**', async route => {
    const request = route.request();
    const url = new URL(request.url());
    const path = url.pathname;

    if (path === '/api/v1/rooms' && request.method() === 'GET') {
      expect(url.searchParams.get('branch')).toBe('colombo');
      expect(url.searchParams.get('check_in')).toBe(checkIn);
      expect(url.searchParams.get('check_out')).toBe(checkOut);
      expect(url.searchParams.get('adults')).toBe('1');
      expect(url.searchParams.get('children')).toBe('0');

      calls.push('rooms');
      await route.fulfill({
        status: 200,
        json: [{
          room_number: 101,
          room_type_id: 'Standard Room',
          branch_id: 1,
          branch_name: 'Colombo',
          daily_rate: 20000,
          price_per_night: 20000,
          capacity: 2,
          room_status: 'Available',
        }],
      });
      return;
    }

    if (path === '/api/v1/otp/send' && request.method() === 'POST') {
      expect(request.postDataJSON()).toEqual({ phone });
      calls.push('send');
      await route.fulfill({
        status: 200,
        json: { success: true, message: 'Test code sent' },
      });
      return;
    }

    if (path === '/api/v1/otp/verify' && request.method() === 'POST') {
      expect(request.postDataJSON()).toEqual({ phone, otp: '789123' });
      calls.push('verify');
      await route.fulfill({
        status: 200,
        json: { success: true, has_membership: false },
      });
      return;
    }

    if (path === '/api/v1/bookings/' && request.method() === 'POST') {
      expect(calls).toEqual(['rooms', 'send', 'verify']);
      expect(request.postDataJSON()).toEqual({
        branch: 'colombo',
        checkIn,
        checkOut,
        adults: 1,
        children: 0,
        nights: 2,
        roomId: '101',
        roomType: 'Standard Room',
        totalPrice: 40000,
        phone,
      });

      calls.push('book');
      await route.fulfill({
        status: 201,
        json: { success: true, bookingRef: reference },
      });
      return;
    }

    await route.abort();
  });

  await page.goto('/booking/colombo');

  await expect(
    page.getByRole('heading', { name: 'Booking Details', exact: true })
  ).toBeVisible();

  // The current date inputs have no associated labels.
  const dates = page.locator('input[type="date"]');

  await dates.nth(0).fill(checkIn);
  await dates.nth(1).fill(checkOut);

  await expect(dates.nth(0)).toHaveValue(checkIn);
  await expect(dates.nth(1)).toHaveValue(checkOut);

  await page.getByRole('button', {
    name: 'CHECK AVAILABILITY',
    exact: true,
  }).click();

  await expect(
    page.getByRole('heading', { name: 'Available Rooms', exact: true })
  ).toBeVisible();

  await expect(
    page.getByRole('heading', { name: 'Standard Room', exact: true })
  ).toBeVisible();

  await page.getByRole('button', {
    name: 'Select This Room',
    exact: true,
  }).click();

  await expect(
    page.getByRole('heading', {
      name: 'Booking Summary & Review',
      exact: true,
    })
  ).toBeVisible();

  await expect(page.getByText('2 Nights Stay', { exact: true }))
    .toBeVisible();

  const totalRow = page.getByText('Calculated Total', { exact: true })
    .locator('..').locator('..');
  await expect(totalRow).toContainText('40,000');

  await page.getByRole('button', { name: 'Continue', exact: true }).click();

  await expect(
    page.getByRole('heading', { name: 'Phone Verification', exact: true })
  ).toBeVisible();

  await page.getByPlaceholder('7X XXX XXXX').fill('770000000');
  await page.getByRole('button', {
    name: 'Send Verification Code',
    exact: true,
  }).click();

  await expect(
    page.getByRole('heading', {
      name: 'Enter Verification Code',
      exact: true,
    })
  ).toBeVisible();

  await page.locator('main input[inputmode="numeric"][maxlength="6"]')
    .fill('789123');

  await page.getByRole('button', {
    name: 'Verify & Confirm Booking',
    exact: true,
  }).click();

  await expect(
    page.getByRole('heading', { name: 'Booking Confirmed!', exact: true })
  ).toBeVisible();

  await expect(page.getByText(reference, { exact: true })).toBeVisible();
  await expect(page.getByText(phone, { exact: true })).toHaveCount(2);

  expect(calls).toEqual(['rooms', 'send', 'verify', 'book']);
});
