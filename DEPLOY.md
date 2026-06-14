# Deploying DynoDoc (free tier)

**Stack:** Neon (Postgres) · Render (FastAPI API) · Vercel (React SPA) · OpenAI (LLM) · GitHub Actions (nightly payout cron).

There's a small chicken-and-egg: the API needs the SPA's URL (CORS, post-login) and the SPA needs the API's URL. So we deploy the API first with placeholders, deploy the SPA, then fill in the real URLs. Follow the order below.

---

## 1. Database — Neon

1. Create a project at [neon.tech](https://neon.tech) (free tier).
2. Copy the connection string. It looks like `postgresql://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require`.
3. **Convert it to the async driver** DynoDoc uses — replace the scheme and drop the query:
   ```
   postgresql+asyncpg://user:pass@ep-xxx.region.aws.neon.tech/dbname
   ```
   (asyncpg handles SSL automatically for Neon; you don't need `?sslmode=require`.)
   Save this as your `DYNODOC_DATABASE_URL`.

## 2. API — Render

1. Push this repo to GitHub (the PR branch merged to `main`).
2. On [render.com](https://render.com): **New → Blueprint**, point it at the repo. It reads [`render.yaml`](./render.yaml) and creates the `dynodoc-api` web service.
3. When prompted, fill the `sync: false` env vars:
   | Var | Value |
   |---|---|
   | `DYNODOC_DATABASE_URL` | the asyncpg URL from step 1 |
   | `DYNODOC_SESSION_SECRET` | `openssl rand -hex 32` |
   | `DYNODOC_CORS_ORIGINS` | `["https://PLACEHOLDER.vercel.app"]` (fix in step 4) |
   | `DYNODOC_GOOGLE_CLIENT_ID` / `_SECRET` | from step 3 |
   | `DYNODOC_GOOGLE_REDIRECT_URI` | `https://<your-api>.onrender.com/api/v1/auth/google/callback` |
   | `DYNODOC_FRONTEND_POST_LOGIN_URL` | `https://PLACEHOLDER.vercel.app/app` (fix in step 4) |
   | `DYNODOC_LLM_API_KEY` | your OpenAI key |
   | `DYNODOC_SETTLE_SECRET` | `openssl rand -hex 24` |
4. Deploy. Note the service URL, e.g. `https://dynodoc-api.onrender.com`. Migrations run automatically on start; check `GET /health` returns 200.

> **Free-tier note:** the service sleeps after ~15 min idle and cold-starts (~30s) on the next request. Fine for a demo.

## 3. Google OAuth

In [Google Cloud Console](https://console.cloud.google.com) → **APIs & Services → Credentials → OAuth client (Web)**:
- **Authorized redirect URI:** `https://<your-api>.onrender.com/api/v1/auth/google/callback`
- **Authorized JavaScript origin:** your Vercel URL (from step 4)
- Copy the Client ID + Secret into Render (step 2).

## 4. SPA — Vercel

1. On [vercel.com](https://vercel.com): **Add New → Project**, import the repo.
2. **Root Directory:** `client`. Vercel auto-detects Vite and reads [`client/vercel.json`](./client/vercel.json) (build + SPA routing).
3. Add env var **`VITE_API_BASE_URL`** = `https://<your-api>.onrender.com` (no trailing slash, no `/api/v1`).
4. Deploy. Note the URL, e.g. `https://dynodoc.vercel.app`.
5. **Go back and fix the placeholders:**
   - Render: set `DYNODOC_CORS_ORIGINS` = `["https://dynodoc.vercel.app"]` and `DYNODOC_FRONTEND_POST_LOGIN_URL` = `https://dynodoc.vercel.app/app`, then redeploy.
   - Google: add `https://dynodoc.vercel.app` as an authorized JavaScript origin.

## 5. Nightly leaderboard payout (cron)

The [`.github/workflows/daily-payout.yml`](./.github/workflows/daily-payout.yml) workflow runs at **00:05 IST** and settles the previous day's top 3 (+50 / +30 / +20 coins).

In the GitHub repo → **Settings → Secrets and variables → Actions**, add:
- `DYNODOC_API_URL` = `https://<your-api>.onrender.com`
- `DYNODOC_SETTLE_SECRET` = the same value you set on Render

Trigger it once manually (**Actions → Daily leaderboard payout → Run workflow**) to confirm it works. (First call may take ~30s if the API was asleep.)

---

## Smoke test

1. Open the Vercel URL → **Start learning free** → Google sign-in → you land on `/app`.
2. Create a course, generate a lesson, take a quiz, play Connections.
3. Redeem a reward, buy a course slot — balances update instantly.
4. Run the cron manually and check a top player's profile shows the "🏆 Daily leaderboard prize".

## Env var reference

All API config is `DYNODOC_`-prefixed (12-factor). Key ones for prod:

| Var | Purpose |
|---|---|
| `DYNODOC_ENVIRONMENT` | `production` (enables Secure cookies) |
| `TZ` | `Asia/Kolkata` — aligns the "day" + payout to IST midnight |
| `DYNODOC_DATABASE_URL` | Neon, **asyncpg** scheme |
| `DYNODOC_SESSION_SECRET` | signs the session cookie |
| `DYNODOC_SESSION_SAME_SITE` | `none` (SPA + API on different domains) |
| `DYNODOC_CORS_ORIGINS` | JSON list of allowed origins |
| `DYNODOC_GOOGLE_CLIENT_ID/_SECRET/_REDIRECT_URI` | OAuth |
| `DYNODOC_FRONTEND_POST_LOGIN_URL` | where to land after sign-in |
| `DYNODOC_LLM_PROVIDER/_MODEL/_API_KEY` | OpenAI |
| `DYNODOC_SETTLE_SECRET` | guards the nightly cron endpoint |

> **Cost:** the only real spend is the OpenAI API (course/lesson/quiz/tutor generation). Everything else here is free tier. Keep an eye on the in-lesson tutor — it's the least bounded call.
