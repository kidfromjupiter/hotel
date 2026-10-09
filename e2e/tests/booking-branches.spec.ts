import { test, expect } from '@playwright/test';

for (const { id, city } of [
  { id: 'colombo', city: 'Colombo' },
  { id: 'kandy', city: 'Kandy' },
  { id: 'galle', city: 'Galle' },
]) {
  test(`selecting ${city} opens its reservation page`, async ({ page }) => {
    await page.route('**/api/v1/**', route => route.abort());
    await page.goto('/booking');

    await expect(
      page.getByRole('heading', { name: 'Select Your Branch', exact: true })
    ).toBeVisible();

    await expect(
      page.getByRole('heading', { name: `SkyNest ${city}`, exact: true })
    ).toBeVisible();

    const branchLink = page.locator(`a[href="/booking/${id}"]`);
    await expect(branchLink).toHaveText('Select This Branch');
    await branchLink.click();

    await expect(page).toHaveURL(
      new RegExp(`/booking/${id}$`),
        { timeout: 20000 }
    );
    await expect(
      page.getByRole('heading', { level: 1 })
    ).toContainText(`SkyNest ${city}`);

    await expect(
      page.getByRole('link', { name: 'All Branches', exact: true })
    ).toBeVisible();
  });
}
