import { defineConfig, devices } from '@playwright/test';

const startFrontend = process.env.E2E_START_FRONTEND === '1';

export default defineConfig({
  testDir: './tests',
  timeout: 60000,
  expect: {
    timeout: 20000,
  },
  workers: 1,
  use: {
    baseURL: 'http://127.0.0.1:3000',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: startFrontend
    ? {
        command: 'npm run dev -- --hostname 127.0.0.1 --port 3000',
        cwd: '../frontend',
        url: 'http://127.0.0.1:3000',
        reuseExistingServer: false,
        timeout: 120000,
      }
    : undefined,
});