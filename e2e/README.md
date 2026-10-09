# Frontend browser tests

These 12 Playwright tests cover the homepage, guest login/logout,
OTP validation, branch selection, and a booking flow.

OTP, booking, and dashboard API responses are mocked.
These tests do not verify real SMS delivery or database persistence.

## Install

From the e2e directory:

```sh
npm ci
npx playwright install chromium
```

## Test an already running frontend

Start the project's frontend using Docker or another terminal.
Wait until http://127.0.0.1:3000/login loads, then run:

```sh
npm test
```

## Let Playwright start the frontend

Install frontend dependencies first with npm ci in the frontend directory.
Ensure port 3000 is free and no other frontend uses the same .next directory.

PowerShell:

```powershell
$env:E2E_START_FRONTEND = '1'
npm.cmd test
Remove-Item Env:E2E_START_FRONTEND
```

Linux/macOS:

```sh
E2E_START_FRONTEND=1 npm test
```

## Watch a test

```sh
npx playwright test tests/booking-flow.spec.ts --debug
```