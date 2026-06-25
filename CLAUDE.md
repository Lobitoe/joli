# CLAUDE.md — Joli

Guidance for Claude Code (and humans) working in this repository.

## What this is

**Joli** is a culturally-intelligent beauty marketplace for the Canadian diaspora — connecting clients with braiders, locticians, barbers, nail techs, mehndi artists and bridal MUAs. Style-first discovery, style-based pricing, variable-length (up to 6–8h) bookings, deposit-protected no-show shield, and a fair commission model (10% only on a brand-new marketplace-sourced client; 0% on repeats and direct-link bookings).

The product spec lives in `memory/PRD.md`. Brand tokens are in `design_guidelines.json` (and the standalone `Joli-Brand-Guide.html` in the parent folder). This app was originally generated in Emergent (branded "Curlnect"), then renamed to Joli.

## Stack

- **Backend:** FastAPI (Python 3.11), MongoDB via Motor (async). JWT auth (PyJWT) with bcrypt password hashing. All routes mounted under `/api`.
- **Frontend:** React (Create React App + CRACO), React Router, Tailwind CSS, shadcn/ui (Radix) components, axios, sonner for toasts. PostHog analytics in `index.html`.
- **Infra:** Emergent base image (`fastapi_react_mongo_shadcn`). `emergentintegrations` is an Emergent-only Python package — **it will likely not install outside Emergent**; isolate/replace it if running locally.

## Repository layout

```
backend/
  server.py            # FastAPI app, mounts /api routers, startup indexes + seeds
  db.py                # Mongo client (needs MONGO_URL, DB_NAME)
  auth.py              # hash/verify password, JWT create/decode, get_current_user, require_role
  utils.py             # helpers: clean(), slot time math, enrich_practitioner()
  schemas.py           # all Pydantic request models
  seed.py              # demo users, practitioners, services, portfolio, blog posts (runs on startup)
  routers/             # auth_router, categories, practitioners, bookings, reviews,
                       #   favorites, verifications, blog, admin
  tests/               # pytest API tests
frontend/
  src/pages/           # one file per screen (Landing, Browse, Profile, Booking, dashboards, admin, blog…)
  src/components/      # Navbar, Footer, ProtectedRoute, BadgeChip, ui/ (shadcn)
  src/contexts/AuthContext.jsx
  src/lib/api.js       # axios instance; attaches Bearer token from localStorage("joli_token")
  public/index.html    # ⚠️ generic <title>Emergent | Fullstack App</title>, no real SEO meta
memory/PRD.md          # product requirements
design_guidelines.json # brand tokens
```

## Run locally

Backend:
```bash
cd backend
pip install -r requirements.txt          # NOTE: emergentintegrations may fail outside Emergent
# .env needs: MONGO_URL, DB_NAME, JWT_SECRET, ADMIN_EMAIL, ADMIN_PASSWORD
uvicorn server:app --reload --port 8000
```
Frontend:
```bash
cd frontend
npm install
# .env needs: REACT_APP_BACKEND_URL=http://localhost:8000
npm start
```
On startup the backend creates indexes and **runs `seed.py` every boot** — be aware it seeds demo data (idempotency: verify before relying on a clean DB).

## Conventions

- Mongo docs use a string `id` (uuid4), not the Mongo `_id` — always strip `_id` with `clean()` / `clean_list()` before returning.
- Auth: routes depend on `get_current_user`; role-gated routes use `require_role("admin")` etc. Frontend gates with `ProtectedRoute roles={...}`.
- Frontend talks only to `${REACT_APP_BACKEND_URL}/api`; token is read from `localStorage("joli_token")`.
- Tailwind brand colors are hard-coded hex (e.g. `#C8552F` terracotta, `#1F1A17` near-black, `#F7F1E8` cream). Prefer pulling these into tokens over time.
- Tests live in `backend/tests/` (pytest). `frontend/src/constants/testIds/` holds `data-testid` values used by tests — keep them in sync.

## Known issues / deliberate stubs (DO NOT assume these work)

These are demo stubs from the Emergent build — they look finished but aren't wired to the real world. See the audit docs in the parent folder for detail.

1. **Payments are mocked.** `routers/bookings.py` sets `deposit_paid: True` and `deposit_stripe_payment_id: "mock_pi_…"`. No Stripe, no payouts, no KYC.
2. **Notifications are mocked.** Booking creates rows in `db.notifications` (channel `sms+whatsapp`) but nothing is sent. No Twilio/WhatsApp.
3. **Image handling is URL-only.** Profile/portfolio/review/verification images are pasted URLs — no upload to storage. `VerificationPage.jsx` even says so in a demo note.
4. **Demo credentials are exposed.** `LoginPage.jsx` prints client/practitioner/**admin** logins in plain text; admin password falls back to a hard-coded literal if `ADMIN_PASSWORD` is unset.
5. **SEO/rendering.** `public/index.html` ships a generic title/meta and the app is client-rendered (CRA) — bad for Google and link previews.
6. **Auth is email/password**, not the PRD's phone-first OTP (WhatsApp number is captured on practitioner profiles only).

### Correctness/security to watch (found in code review)

- `POST /api/bookings` **does not re-validate the slot** against availability or existing bookings, so double-booking / past-date / out-of-hours bookings are possible. Validate server-side before insert.
- `client_source` is **client-supplied** in the booking body, so commission attribution (marketplace vs direct_link) can be gamed to avoid the 10%. Derive it server-side.
- JWT is stored in `localStorage` (XSS-exposable). Login has **no rate limiting**.
- Cancellation does not enforce the deposit-forfeiture policy or process refunds (ties into mocked payments).
- `list_practitioners` does N+1 queries per practitioner (thumbs/services/badges) — fine at demo scale, optimize later.

## What's solid (don't break it)

- The **commission engine** in `bookings.py` is correct: 25% deposit, 10% on first marketplace client else 0%, `payout = deposit − commission`, with `client_practitioner_relationships.is_commission_eligible` tracking. Practitioner + admin dashboards reflect it consistently.
- Cultural taxonomy, style-based pricing with durations/breaks, direct-link (`/p/{slug}`), reviews (completed-booking-gated, avg recompute), and the new **verification + badges** and **Journal/blog** systems all work.

## Working agreement

This repo must stay **in sync with what Emergent has deployed**. The current clone matches the pushed `main` (commit baseline noted at handoff). When fixing the items above, keep changes minimal and well-scoped so they can be reconciled with Emergent if needed.
