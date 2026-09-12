# SkyNest — Hotel Booking Frontend

Next.js 14 frontend for **SkyNest** luxury hotels (Colombo · Kandy · Galle).
Built with the App Router, Tailwind CSS, and TypeScript.

---

## Tech Stack

| Tool | Version |
|---|---|
| Next.js | 14.2.5 |
| React | 18 |
| Tailwind CSS | 3.4 |
| TypeScript | 5 |
| react-icons | 5 |
| react-hot-toast | 2 |

---

## Getting Started

```bash
# 1. Install dependencies
npm install

# 2. Set environment variable (already in .env.local)
#    NEXT_PUBLIC_API_URL=http://localhost:8000

# 3. Start dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Booking Flow

```
/ (Landing)
  └─ /booking              ← Select branch (Colombo / Kandy / Galle)
       └─ /booking/colombo ← Multi-step wizard:
       └─ /booking/kandy       Step 1: Check-in / Check-out / Guests
       └─ /booking/galle       Step 2: Available rooms (from backend)
                               Step 3: Optional amenities
                               Step 4: Phone number → OTP verification
                               Step 5: Booking confirmation + OTP reminder
```

---

## Backend API Contract

The frontend calls these endpoints (base URL from `NEXT_PUBLIC_API_URL`):

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/rooms/availability` | Check available rooms |
| `GET` | `/api/amenities?branch=<b>` | Fetch add-on amenities |
| `POST` | `/api/otp/send` | Send OTP to phone |
| `POST` | `/api/otp/verify` | Verify OTP |
| `POST` | `/api/booking/create` | Create booking record |

### POST `/api/rooms/availability`
**Request:**
```json
{
  "branch": "colombo",
  "checkIn": "2026-10-01",
  "checkOut": "2026-10-05",
  "adults": 2,
  "children": 1
}
```
**Response:**
```json
{
  "available": true,
  "hasMembership": false,
  "rooms": [
    {
      "id": "room-101",
      "type": "Deluxe",
      "name": "Deluxe City View",
      "description": "...",
      "pricePerNight": 25000,
      "totalPrice": 100000,
      "nights": 4,
      "maxCapacity": 3,
      "features": ["King Bed", "City View", "Free Wi-Fi", "Mini Bar"],
      "image": "https://...",
      "isBestseller": true,
      "membershipPrice": 20000,
      "membershipDiscount": 20
    }
  ]
}
```
When no rooms available:
```json
{
  "available": false,
  "rooms": [],
  "message": "No rooms available for 8 guests. Maximum capacity per room is 4."
}
```

### POST `/api/otp/send`
```json
{ "phone": "+94771234567" }
```
Response: `{ "success": true, "message": "OTP sent" }`

> The backend should also perform a **membership lookup** by phone number during availability check (the `hasMembership` field in the availability response).

### POST `/api/booking/create`
```json
{
  "branch": "colombo",
  "checkIn": "2026-10-01",
  "checkOut": "2026-10-05",
  "adults": 2,
  "children": 1,
  "roomId": "room-101",
  "amenityIds": ["breakfast", "airport"],
  "phone": "+94771234567"
}
```
Response: `{ "success": true, "bookingRef": "SKN-2026-7834", "message": "Booking confirmed" }`

---

## Project Structure

```
skynest/
├── app/
│   ├── layout.tsx                  # Root layout (Navbar + toast)
│   ├── page.tsx                    # Landing / Hero page
│   ├── globals.css
│   └── booking/
│       ├── page.tsx                # Branch selection
│       └── [branch]/
│           └── page.tsx            # Booking wizard (thin server wrapper)
├── components/
│   ├── Providers.tsx               # Client-side toast provider
│   ├── Navbar.tsx                  # Fixed top navigation
│   ├── StepIndicator.tsx           # Progress steps bar
│   ├── BranchCard.tsx             # Branch selection card
│   ├── BookingWizard.tsx          # ★ Main multi-step booking wizard
│   ├── BookingForm.tsx            # Step 1 — dates + guests
│   ├── RoomCard.tsx               # Step 2 — individual room card
│   ├── AmenitiesSelector.tsx      # Step 3 — optional add-ons
│   ├── PhoneOTPForm.tsx           # Step 4 — phone + OTP + create booking
│   └── BookingSummary.tsx         # Step 5 — final summary
├── lib/
│   ├── types.ts                    # All TypeScript interfaces
│   └── api.ts                      # Backend API functions
├── .env.local                      # NEXT_PUBLIC_API_URL
└── tailwind.config.ts
```

---

## Color Palette

| Token | Hex | Usage |
|---|---|---|
| `skynest-blue` | `#0EA5E9` | Primary CTA, accents |
| `skynest-blue-hover` | `#0284C7` | Button hover |
| `skynest-blue-light` | `#BAE6FD` | Light text on dark bg |
| `skynest-blue-pale` | `#F0F9FF` | Page backgrounds |
| `skynest-navy` | `#0F172A` | Navbar, card headers, dark sections |
| `skynest-navy-light` | `#1E293B` | Borders, dividers on dark |
| `skynest-muted` | `#64748B` | Secondary text |

---

## Replacing Placeholder Images

All images currently use Unsplash URLs. To replace with your own:
1. Add image files to `public/images/`
2. Update `src` props in `app/booking/page.tsx` (branch images) and `app/page.tsx` (hero)
3. Remove the `remotePatterns` entry from `next.config.js` if you no longer need Unsplash

---

## Building for Production

```bash
npm run build
npm run start
```

Or deploy to Vercel — just push to your repo and it will auto-deploy.
Set `NEXT_PUBLIC_API_URL` as an environment variable in your Vercel project settings.
