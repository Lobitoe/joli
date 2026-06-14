# Curlnect — Multicultural Beauty Marketplace MVP

## Original Problem Statement (paraphrased from PRD)
A culturally-intelligent two-sided marketplace for mobile and independent beauty/grooming professionals serving communities of colour in Canada (Calgary/Edmonton launch). Replaces Instagram DMs with structured discovery, style-specific portfolios, deposit-based booking, and business management for braiders, locticians, barbers, nail techs, mehndi artists, threading specialists, bridal MUAs.

## User Choices (Session 1)
- Auth: email/password JWT (a)
- Payments: mocked Stripe Connect (deposit_paid auto-set, fake payment IDs)
- Notifications: mocked SMS/WhatsApp (logged to db.notifications)
- Scope: FULL MVP
- Images: URL-based (Unsplash CDN for seeds, URL input for practitioner uploads)

## Architecture (this implementation)
- Backend: FastAPI + Motor (MongoDB async), JWT auth (HS256, 7-day exp), bcrypt password hashing
- Frontend: React (CRA) + react-router-dom v7 + Tailwind + sonner (toasts) + lucide-react icons
- DB: MongoDB collections: users, practitioners, service_categories, services, portfolio_items, availability, bookings, reviews, favorites, notifications, client_practitioner_relationships
- All ObjectIds are coerced/excluded via clean() helpers; UUIDs used for `id` fields

## User Personas
1. Practitioner — braider/barber/nail tech/MUA/mehndi artist/threading specialist
2. Client — books services, leaves reviews
3. Admin — monitors GMV, commission revenue, supply/demand

## Core Requirements (static)
- Style-specific portfolio (variable durations, cultural taxonomy)
- 25% deposit-based bookings with mocked Stripe
- Commission: 10% first marketplace booking, 0% repeat, 0% direct_link forever
- Direct booking link (`/p/{slug}`) — zero commission
- Reviews with ratings
- Three dashboards (client, practitioner, admin)

## What's been implemented (Session 1, completed today)
- ✅ Auth (register/login/logout/me) — JWT in localStorage + httpOnly cookie fallback
- ✅ 44 seeded service categories across braiding, locs, natural hair, weaves/wigs, barber, nails, mehndi, threading, bridal
- ✅ 5 seeded practitioners (Blessing braider YYC, Kofi mobile barber YYC, Linh nail tech YEG, Priya bridal YYC, Fatima threading YEG) + 2 client accounts + admin
- ✅ Landing page (hero + search + 4 category cards + featured practitioners + value props + CTA)
- ✅ Browse page (4 live filters: city, category, service mode, type) wired via URL params
- ✅ Practitioner profile (portfolio gallery with category tabs, services menu grouped by category, reviews, favorite, share)
- ✅ Booking flow (date picker, slot computation, location toggle for mobile services, notes, mock deposit pay, confirmation screen)
- ✅ Client dashboard (upcoming, past, cancel, "mark done" demo helper, leave review modal, favorites, SMS log)
- ✅ Practitioner dashboard (gross GMV, net payout, upcoming, rating, direct booking link with copy, quick actions, recent alerts)
- ✅ Practitioner onboarding form (profile, type, location, service mode, neighbourhoods, payments, instagram, whatsapp, cancellation policy)
- ✅ Services Manager (CRUD with category picker + price/duration)
- ✅ Portfolio Manager (URL-based add/delete with category tagging)
- ✅ Availability Manager (weekly schedule editor 0-6 day grid)
- ✅ Admin dashboard (GMV, commission revenue, supply mix, recent bookings)
- ✅ Direct booking link page `/p/{slug}` with 0% commission tag
- ✅ How It Works marketing page
- ✅ Commission engine: first marketplace booking = 10%, repeat = 0%, direct_link = 0% (always)
- ✅ Slot computation engine (30-min granularity, overlap detection against existing confirmed bookings, availability lookup)
- ✅ Mock SMS/WhatsApp log written for both parties on every booking
- ✅ Tested end-to-end: 100% frontend tests pass, 19/20 backend tests pass (1 false-fail in test script)

## Prioritized backlog (P0/P1/P2 for future sessions)
**P0** (recommended next)
- Real Stripe Connect integration (when keys available) — deposit charge + remainder card-tap + payout to practitioner Connect account
- Image uploads (Cloudinary or base64-to-Mongo) instead of URL paste
- Phone OTP signup (Twilio) — per PRD's phone-first preference
- Instagram portfolio import (PRD V2)

**P1**
- Real SMS/WhatsApp delivery via Twilio
- 24h + 2h reminder cron job
- Bridal multi-event packages with sequenced trial/ceremony/reception
- Practitioner public availability calendar grid (currently slot-only)
- Search by style autocomplete

**P2**
- Reviews with photo uploads (currently URLs only)
- Bookings export CSV for practitioners
- Multi-language UI (FR, HI, PA, UR per practitioner.languages already in DB)
- Maps integration for service area visualisation
- Email receipts (SendGrid)

## Known mocks (HIGHLIGHTED)
- 💰 **STRIPE CONNECT — MOCKED**: deposits are auto-marked paid; no real card charged.
- 📱 **SMS / WHATSAPP — MOCKED**: notifications written to `db.notifications` only; no Twilio call.

## Next Action Items
- Confirm with user whether to integrate real Stripe Connect or continue mocked
- Confirm Twilio for OTP/SMS
- Validate UX on a real mobile device with one of the seeded practitioner accounts
