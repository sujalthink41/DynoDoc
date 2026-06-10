# DynoDoc v1 — Features & Workflows

> This doc lists **what we're building in v1** (the features) and **how the user moves through it** (the workflows/flows).
> It builds on [`00-product-idea.md`](./00-product-idea.md). Architecture (agents, RAG, DB) comes in a later doc.

> **Guiding principle:** DynoDoc is not a boring course site. It's a **super-engaging, habit-forming learning platform.** Every day should pull the user back. Learning + competition + streaks + rewards are all first-class — not extras.

---

## Part A — The v1 Feature Set

Features are grouped into **4 pillars**:

1. **Foundation** — auth & profile
2. **Learning Core** — the actual teaching engine
3. **Engagement Engine** — what makes it addictive (daily challenge, streaks, leaderboard, rewards)
4. **Sharing** — showing off and spreading the platform

Priority key: **P0** = must-have for the slice · **P1** = strongly want · **P2** = parked for later.

---

## Pillar 1 — Foundation

### 1.1 Auth — Google only  · *P0*
Dead simple. No friction.

- **In v1:** **Google sign-in only.** Nothing else.
- **Parked:** Email/password, other providers, SSO.

### 1.2 Profile  · *P0*
A personal page that shows the user's whole learning story.

- **In v1:**
  - Basic info from Google (name, photo).
  - **What they're currently learning** (active course).
  - **What they've learned** (completed courses/lectures).
  - **Stats:** progress %, lectures completed, coding tasks passed, total **points/XP**, current **streak**, **badges/achievements**.
  - **"Artifacts" framing:** *"Written 340 lines of code · Built 3 things · 12-day streak."*
- **Parked:** Custom bios, follower/following, profile themes.

---

## Pillar 2 — Learning Core

### 2.1 "Start Learning" Intake  · *P0*
- **In v1:** User types a goal (*"I want to learn Python"*) → AI asks **3–5 short adaptive questions** (level, background, goal, time) → produces a **learner profile** that shapes the lessons.
- **Parked:** Long skill tests, resume upload.
> Keep it under ~5 questions. We learn more from performance than from a door quiz.

### 2.2 Course Generation  · *P0*
- **In v1:** AI builds **roadmap → lectures → docs → reference links → assessments**.
  - **Strategy: roadmap eager, lessons lazy** — generate the full roadmap + Lecture 1 immediately; generate other lectures when first opened.
  - **Live waiting screen:** *"Researching resources… building roadmap… writing Lecture 1…"* so the wait feels alive.
- **Parked:** On-demand course expansion, importing own materials.

### 2.3 Roadmap / Course Home  · *P0*
- **In v1:** Udemy-style ordered list of **lectures**, each with docs count + status (not started · in progress · completed · **verified**). **Resume** button.
- **Parked:** Multi-course dashboard view, course templates.

### 2.4 Lecture & Doc Reading  · *P0*
- **In v1:** Multiple **docs** per lecture (Doc 1, 2…), clean reading UI with **code blocks**, **reference links + YouTube** per topic, mark-as-read / continue.
- **Parked:** Highlighting, note-taking.

### 2.5 AI Tutor (Right-Side Panel)  · *P0*
- **In v1:** Chat panel **grounded in the current doc** — ask questions, get examples, discuss the concept.
- **Parked:** Full-history memory, proactive "you seem stuck" nudges, voice.

### 2.6 Adaptive Lessons — the WOW feature  · *P1 (headline)*
- **In v1:** Lessons **written for the learner's level/background** (e.g. JS dev → Python via JS analogies). On any doc: **"Explain simpler"** / **"Go deeper"** regenerates it at a new difficulty.
- **Parked:** Auto-detecting difficulty, switching teaching style automatically.

### 2.7 Assessment & Verification — the moat  · *P0*
- **In v1:**
  - **Quiz** per lecture (MCQ/short answer, **auto-graded** instantly).
  - **One coding task** per lecture: prompt + code editor → **runs in a sandbox** → **AI-graded against a rubric** → pass/fail **with feedback**. Passing marks the lecture **verified** and awards **points**.
- **Parked:** Multi-file project verification, full capstone apps.

---

## Pillar 3 — Engagement Engine 🔥
*This is the new heart of v1 — what makes DynoDoc addictive.*

### 3.0 Points / XP System  · *P0 (the backbone)*
A single currency that powers streaks, leaderboards, and rewards. Everything that matters earns points.

- **In v1:** Earn points for:
  - Answering **daily challenge** questions correctly.
  - Completing a **lecture** / reading docs.
  - **Passing a coding task** (worth the most).
  - **Maintaining a streak** (bonus multiplier).
- **Parked:** Spending points (cosmetics, unlocks), level tiers.
> Every engagement feature reads from this one points system. Build it first.

### 3.1 Daily Challenge ("Daily Dose")  · *P0*
The hook that brings people back every single day.

- **In v1:**
  - Every day a user logs in, they get **2–3 quick tech questions**.
  - Questions are a mix of **their current learning topics** (reinforcement / spaced repetition) and **general tech**.
  - Instant feedback + points for correct answers.
  - Completing today's challenge **keeps the streak alive**.
- **Parked:** Difficulty tiers, themed weeks, "challenge a friend."

### 3.2 Streaks  · *P0*
- **In v1:** Consecutive days the user shows up and does the daily challenge (and/or learns). **Streak count shown prominently** (profile, dashboard, home). Visible **streak-break warning**.
- **Parked:** Streak freezes / repair, streak milestones with rewards.

### 3.3 Leaderboard & Dashboard  · *P0*
The competition layer.

- **In v1:**
  - A **dashboard** showing: your **streak**, **points**, **how many you got correct each day**, and your **rank**.
  - **Leaderboards** — **daily** and **monthly** — showing **who's leading**, top performers, and the user's own position.
  - Scope: **global** in v1.
- **Parked:** Friends/cohort leaderboards, company/team boards, weekly boards.

### 3.4 Monthly Rewards  · *P1*
The payoff that makes the competition matter.

- **In v1:**
  - At **month end**, the **top 5–10** users (by monthly points) get a **reward** (exact reward TBD — swag, free subscription time, badge, etc.).
  - Monthly leaderboard **snapshots and resets** each month.
  - A clear **"this month's prize"** banner so people know what they're playing for.
- **Parked:** Seasons, tiered prizes, referral bonuses, sponsored prizes.

### 3.5 Progress & Saving  · *P0*
- **In v1:** Per-course progress (% complete, lectures verified, tasks passed, artifacts written). **Save / bookmark** lectures. Resume where you left off.
- **Parked:** Spaced-repetition review scheduler.

---

## Pillar 4 — Sharing

### 4.1 Share Your Learning  · *P1*
Show off progress + spread the platform organically.

- **In v1:**
  - User can **share** their **profile** or a specific **course/progress** via a **link**.
  - Anyone with the link can **open and view it (read-only)**.
  - User controls **what's public** (privacy toggle).
- **Parked:** Embeddable widgets, share to LinkedIn/X with auto-cards, verified credential pages.

---

## Part B — The Workflows (User Flows)

### Flow 1 — Onboarding → Course Created (first-time user)
```
1. User signs in with Google (one tap).
2. Types a goal:  "I want to learn Python."
3. AI asks 3–5 quick questions (level, background, goal, time).
4. Submits → generation starts; live status screen plays.
5. Roadmap appears (all lectures listed); Lecture 1 ready to open.
6. User lands on Course Home and opens Lecture 1.
```

### Flow 2 — Daily Check-In (the engagement loop) 🔥
```
1. User opens DynoDoc → greeted with today's "Daily Dose" (2–3 questions).
2. Answers them → instant feedback + points → STREAK kept alive.
3. Sees the dashboard: streak, points, today's correct count, their rank.
4. Glances at the leaderboard — "I'm #14 this month, 200 pts from top 10."
5. Motivated → jumps into their course to earn more points (→ Flow 3).
```

### Flow 3 — The Learning Loop (the everyday core)
```
1. Opens a lecture → reads Doc 1.
2. Confused? → asks the AI tutor (grounded in this doc).
3. Too hard/easy? → "Explain simpler" / "Go deeper" → doc rewrites itself.
4. Explores reference links / YouTube.
5. Marks docs read → reaches the lecture's assessment (→ Flow 4).
```

### Flow 4 — Assessment & Verification (the proof)
```
1. Quiz → auto-graded instantly → score + explanations + points.
2. Coding task: prompt + code editor → submit.
3. Code runs in sandbox + AI grades vs rubric.
      PASS  → lecture "verified", points awarded, progress + profile update.
      CLOSE → feedback on what's wrong → fix → resubmit.
4. Return to Course Home → next lecture.
```

### Flow 5 — Profile & Sharing
```
1. User opens their Profile: currently learning, completed, stats,
   points, streak, badges, artifacts.
2. Taps "Share" → gets a link (chooses what's public).
3. Sends it to a friend → friend opens it → sees a read-only view
   of the user's learning journey.  (Organic growth!)
```

### Flow 6 — Resume (returning user)
```
1. Signs in → does the Daily Dose (Flow 2).
2. Course Home shows progress + "Resume".
3. Clicks Resume → drops back exactly where they left off.
```

---

## Part C — v1 Feature Summary Table

| Pillar | # | Feature | Priority |
|--------|---|---------|----------|
| Foundation | 1.1 | Google Auth (only) | P0 |
| Foundation | 1.2 | Profile (stats + journey) | P0 |
| Learning | 2.1 | Start-Learning Intake | P0 |
| Learning | 2.2 | Course Generation | P0 |
| Learning | 2.3 | Roadmap / Course Home | P0 |
| Learning | 2.4 | Lecture & Doc Reading | P0 |
| Learning | 2.5 | AI Tutor (right panel) | P0 |
| Learning | 2.6 | **Adaptive Lessons (WOW)** | P1 |
| Learning | 2.7 | **Assessment + AI code grading (moat)** | P0 |
| Engagement | 3.0 | **Points / XP backbone** | P0 |
| Engagement | 3.1 | **Daily Challenge (Daily Dose)** | P0 |
| Engagement | 3.2 | **Streaks** | P0 |
| Engagement | 3.3 | **Leaderboard & Dashboard** | P0 |
| Engagement | 3.4 | **Monthly Rewards** | P1 |
| Engagement | 3.5 | Progress & Saving | P0 |
| Sharing | 4.1 | Share your learning | P1 |

---

## Part D — Open Decisions to Lock Next

1. **Coding-task language in v1:** start with **one language (e.g. Python)** to keep sandbox + grader simple? *(Recommended: yes.)*
2. **Gating:** free navigation between lectures with "verified" badges, or must-pass-to-unlock? *(Recommended: free + badges.)*
3. **Daily challenge source:** mix of *their topics* + *general tech*, or purely their topics? *(Recommended: mix.)*
4. **Monthly reward:** what's the actual prize for top 5–10? (swag / free subscription / cash / badge)
5. **Leaderboard scope:** global only in v1, or also friends/cohort? *(Recommended: global only for v1.)*
6. **One active course per user in v1**, or several at once?

> Once these are answered, we move to `02-architecture.md` (ADK agents + RAG layers + data model).
