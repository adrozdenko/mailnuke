# MailNuke MVP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Plan ID:** `plan-1775829511959-26ed9f`
**Goal:** Ship MailNuke MVP — freemium SaaS Gmail cleanup tool
**Architecture:** Next.js 15 frontend (Vercel) + FastAPI backend (Railway) + existing Python async engine + Supabase PostgreSQL
**Tech Stack:** Next.js 15, Tailwind, shadcn/ui, NextAuth.js, FastAPI, WebSocket, Stripe, Supabase

## Milestones

Each milestone is independently deployable. Order matters — each builds on the previous.

### M1: Monorepo Scaffold
**Files:** Root package.json, turborepo.json, frontend/, backend/
**What:** Restructure into monorepo. Move existing Python engine into backend/engine/. Scaffold Next.js app in frontend/. Root turborepo config.
**Verify:** `npm run dev` starts both, `cd backend && pytest` passes 119 tests

### M2: Landing Page
**Skill:** `frontend-design` (Claude ecosystem skill for production-grade UI)
**Files:** frontend/app/(marketing)/page.tsx, components/
**What:** Use the `frontend-design` skill to build a distinctive, high-quality landing page. Brief the skill with: product name (MailNuke), value prop (nuke 17,000 emails in 12 seconds), 3-step flow (Sign in > Pick preset > Nuke), pricing (Free vs Pro $5/mo), FAQ, social proof section, CTA "Nuke My Inbox". The skill handles design philosophy, responsive layout, animations, and component architecture.
**Verify:** Lighthouse >90, responsive, visually distinctive (not generic SaaS template)

### M3: Google OAuth + User Model
**Files:** frontend/app/api/auth/[...nextauth]/route.ts, backend/app/auth/, backend/app/models/
**What:** NextAuth.js Google provider with gmail.modify scope + offline access. Supabase users table. Encrypted refresh token storage. FastAPI JWT validation via fastapi-nextauth-jwt. Protected /dashboard routes.
**Verify:** Sign in works, user + token in DB

### M4: Dashboard Shell + Preset Selector
**Files:** frontend/app/(app)/dashboard/, backend/app/routes/presets.py
**What:** Sidebar + main area layout. GET /api/presets returns 6 FilterConfig presets. Preset cards with selection state.
**Verify:** Dashboard loads, presets display, selection works

### M5: Dry Run Preview
**Files:** backend/app/routes/cleanup.py, frontend/app/(app)/dashboard/preview/
**What:** POST /api/cleanup/preview — builds Gmail creds from stored refresh token, runs QueryBuilder, returns estimated count. Frontend preview card with "Nuke" button. Free tier usage check.
**Verify:** Preview count matches Gmail, free tier limit works

### M6: Live Deletion with WebSocket Progress
**Files:** backend/app/routes/cleanup_ws.py, frontend/components/NukeProgress.tsx
**What:** WebSocket endpoint ws:///api/cleanup/run. Runs DeletionOrchestrator with progress callback sending JSON frames. Frontend live progress bar + emails/sec counter. Store job in cleanup_jobs table. Increment monthly usage.
**Verify:** Live updates in browser, job in DB

### M7: Stripe Billing
**Files:** backend/app/routes/billing.py, frontend/app/(marketing)/pricing/
**What:** Stripe checkout for Pro ($5/mo, $48/yr). Webhook handles subscription lifecycle. Updates user.tier. Customer portal.
**Verify:** Checkout → webhook → tier updated → cancel → downgraded

### M8: Polish + Deploy
**Files:** Various
**What:** Error boundaries, loading states, toasts. Privacy policy + ToS pages. Production env vars on Vercel + Railway. Custom domain. Google OAuth verification submission. E2E manual test.
**Verify:** Full flow works in production

## Dependency Graph

```
M1 (scaffold)
 ├── M2 (landing) — independent, can parallel with M3
 ├── M3 (auth + DB)
 │    ├── M4 (dashboard)
 │    │    ├── M5 (preview)
 │    │    │    └── M6 (live deletion)
 │    │    └── M7 (billing) — parallel with M5/M6
 │    └── M7 (billing)
 └── M8 (polish) — after everything

Parallelizable: M2 || M3, then M5 || M7
Sequential: M1 → M3 → M4 → M5 → M6
```

## Database Schema (Supabase)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    google_refresh_token TEXT NOT NULL, -- encrypted
    tier TEXT DEFAULT 'free' CHECK (tier IN ('free', 'pro')),
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    monthly_usage INT DEFAULT 0,
    usage_reset_at TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE cleanup_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    preset TEXT NOT NULL,
    query TEXT NOT NULL,
    count_deleted INT DEFAULT 0,
    count_errors INT DEFAULT 0,
    duration_seconds FLOAT,
    status TEXT DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed')),
    created_at TIMESTAMPTZ DEFAULT now()
);
```

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/presets | JWT | List all 6 filter presets |
| POST | /api/cleanup/preview | JWT | Dry run — returns estimated count |
| WS | /api/cleanup/run | JWT | Live deletion with progress frames |
| GET | /api/cleanup/history | JWT | User's past cleanup jobs |
| POST | /api/billing/checkout | JWT | Create Stripe checkout session |
| POST | /api/billing/webhook | Stripe sig | Handle subscription events |
| GET | /api/billing/portal | JWT | Redirect to Stripe customer portal |

## Environment Variables

### Frontend (.env.local)
```
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=<random>
GOOGLE_CLIENT_ID=<from Google Cloud Console>
GOOGLE_CLIENT_SECRET=<from Google Cloud Console>
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=<stripe>
```

### Backend (.env)
```
DATABASE_URL=<supabase connection string>
NEXTAUTH_SECRET=<same as frontend>
STRIPE_SECRET_KEY=<stripe>
STRIPE_WEBHOOK_SECRET=<stripe>
ENCRYPTION_KEY=<for refresh token encryption>
```
