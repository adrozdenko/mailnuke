# MailNuke — Product Design

## Overview

**What:** Freemium SaaS that nukes unwanted Gmail emails at 83+ emails/second.
**Who:** Anyone drowning in newsletter/promo/notification email bloat.
**How:** Sign in with Google, pick a preset, watch thousands of emails vanish.
**Moat:** 10x faster than competitors. Batch async engine vs single-threaded.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND                          │
│              Next.js + Tailwind CSS                  │
│              Deployed on Vercel                      │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────────┐ │
│  │ Landing  │ │  Auth    │ │     Dashboard         │ │
│  │  Page    │ │ (Google  │ │  - Preset selector    │ │
│  │          │ │  OAuth)  │ │  - Dry run preview    │ │
│  │          │ │          │ │  - Live progress      │ │
│  │          │ │          │ │  - History / stats    │ │
│  │          │ │          │ │  - Inbox analytics    │ │
│  └──────────┘ └──────────┘ └──────────────────────┘ │
└──────────────────┬──────────────────────────────────┘
                   │ REST API + WebSocket (live progress)
                   │
┌──────────────────▼──────────────────────────────────┐
│                    BACKEND                           │
│              FastAPI (Python)                        │
│              Deployed on Railway / Fly.io            │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │           Existing Engine (v2.0.0)            │   │
│  │  QueryBuilder → EmailDeleter → Orchestrator   │   │
│  │  PerformanceTracker → FilterConfig            │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────────┐ │
│  │  Auth    │ │  Jobs    │ │     User Model        │ │
│  │ (Google  │ │ (async   │ │  - email              │ │
│  │  OAuth2) │ │  queue)  │ │  - tier (free/pro)    │ │
│  │          │ │          │ │  - usage this month    │ │
│  │          │ │          │ │  - cleanup history     │ │
│  └──────────┘ └──────────┘ └──────────────────────┘ │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │              Database (Postgres)              │   │
│  │  users, cleanup_jobs, job_results, payments   │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | Next.js 15 + Tailwind CSS | SSR landing page + SPA dashboard, deploy to Vercel |
| Backend | FastAPI | Async Python, matches existing engine, WebSocket support |
| Database | PostgreSQL (Supabase or Neon) | Users, jobs, history. Managed, free tier |
| Auth | Google OAuth 2.0 (via NextAuth.js) | Users already have Google accounts. One click. |
| Payments | Stripe | Freemium billing, simple subscription |
| Job Queue | Background Tasks (FastAPI) or Celery | Cleanup jobs run async, report progress via WebSocket |
| Deployment | Vercel (frontend) + Railway/Fly.io (backend) | Cheap, scales, no DevOps |
| Monitoring | Sentry + PostHog | Errors + product analytics |

## User Flow

### First Visit
1. Land on mailnuke.io (or .app)
2. See hero: "17,000 emails deleted in 12 seconds"
3. Click "Nuke My Inbox" (CTA)
4. Google OAuth sign-in (request gmail.modify scope)
5. Land on dashboard

### Dashboard
1. See inbox summary: total emails, top senders, category breakdown
2. Pick a preset (or build custom filter)
3. Click "Preview" — dry run shows count + sample senders
4. Click "Nuke" — live progress bar, emails/sec counter
5. See results: X deleted, Y preserved, Z seconds

### Upgrade Flow
1. Free user hits limit (500 emails or 1 cleanup/month)
2. Banner: "Upgrade to Pro for unlimited cleanups"
3. Stripe checkout — $5/month or $48/year
4. Unlocked: unlimited, custom filters, scheduled cleanup, analytics

## Pages

### Landing Page
- Hero with animated counter (emails deleted)
- 3-step explainer (Sign in → Pick preset → Nuke)
- Speed comparison vs competitors
- Testimonials / social proof
- Pricing table (Free vs Pro)
- FAQ (safety, privacy, data handling)
- Footer (privacy policy, terms, contact)

### Dashboard
- **Sidebar:** Presets list, custom filter builder, history, settings
- **Main area:** 
  - Inbox overview cards (total, by category, storage used)
  - Selected preset details + dry run count
  - "Nuke" button (big, red, satisfying)
  - Live progress (WebSocket): progress bar + emails/sec + current batch
  - Results summary after completion

### History
- Past cleanup runs with date, preset, count deleted, duration
- Cumulative stats: total emails ever deleted, storage freed

### Settings
- Connected Google account
- Subscription tier
- Scheduled cleanup toggle (Pro only)
- Danger zone: disconnect account, delete data

## Pricing

| | Free | Pro ($5/mo) |
|---|------|-------------|
| Cleanups | 1 per month | Unlimited |
| Presets | Default only | All 6 + custom |
| Max emails per run | 500 | Unlimited |
| Dry run preview | Yes | Yes |
| Scheduled cleanup | No | Weekly/monthly auto |
| Inbox analytics | No | Top senders, storage breakdown |
| Email age filter | 6 months+ only | Any age |

## Google OAuth Verification (Required for Launch)

| Step | Effort | Timeline |
|------|--------|----------|
| Brand verification | Submit app name + logo | 2-3 days |
| Privacy policy page | Write and publish on domain | 1 day |
| Sensitive scope verification (gmail.modify) | Demo video + justification | 3-5 days |
| Domain verification | DNS TXT record | 1 hour |
| **Total** | | **~1-2 weeks** |

Note: gmail.modify is a sensitive scope (not restricted). No security assessment needed unless we use mail.google.com full access.

## MVP Scope

### Phase 1: MVP (ship in 2-3 weeks)
- Landing page with pricing
- Google OAuth sign-in
- Dashboard with 6 presets
- Dry run preview
- Live progress (WebSocket)
- Results summary
- Free tier (500 emails, 1/month)
- Stripe integration for Pro

### Phase 2: Growth
- Inbox analytics (top senders chart, category breakdown)
- Custom filter builder UI
- Scheduled cleanup (cron)
- Email notifications ("Your monthly cleanup is ready")

### Phase 3: Scale
- Multi-provider (Outlook, Yahoo)
- Team plans
- API access
- Chrome extension

## Risks

| Risk | Mitigation |
|------|-----------|
| Google revokes OAuth approval | Keep scope minimal (gmail.modify only), fast verification |
| User deletes important email, blames us | Dry run by default, "moved to trash" (30-day recovery), clear warnings |
| Low conversion free→pro | A/B test the limit (500 vs 1000), show "X more emails waiting" |
| Competitor copies engine | Speed is code-level moat, not easy to replicate |
| GDPR/privacy concerns | Never store email content, only metadata (sender, count). Clear privacy policy. |

## Data We Store (and Don't Store)

**We store:**
- User email address
- OAuth refresh token (encrypted)
- Cleanup job history (preset used, count deleted, timestamp)
- Subscription status

**We never store:**
- Email content
- Email subjects
- Attachment data
- Contact lists
