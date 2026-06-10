# DynoDoc v1 — Vertical Slices & Testing Strategy

> We build the product **one vertical slice at a time**, and **every slice ships with its tests** — testing is part of "done," not a phase at the end.
> Builds on [`02-architecture.md`](./02-architecture.md) (package-by-domain, ports & adapters) and [`03-data-model.md`](./03-data-model.md).

---

# Part A — Vertical Slices

## A.1 What a "vertical slice" means here
A slice is **one complete flow**, cut top-to-bottom through every layer:

```
entrypoint (http/sse/worker)  →  process / domain service  →  ports  →  platform adapters  →  DB / external
        ↑ request schema             ↑ business rule            ↑ contract     ↑ ADK / pgvector / sandbox / redis
        └──────────────────────────── + the events it emits + its tests ──────────────────────────────┘
```

We build slices, not layers. A slice is "done" only when it works end-to-end **and** has the tests defined in Part B (its Definition of Done).

## A.2 Build order (slices depend on earlier ones)
**Phase 0 — Foundation** must exist before features can earn points or be retrieved:
auth · DB base+mixins · settings/bootstrap · **event outbox dispatcher** · **points ledger + award-points handler** · **embedding/indexing pipeline**.

Then: **Phase 1 Learning core → Phase 2 Tutor → Phase 3 Assessment → Phase 4 Engagement → Phase 5 Progress & Sharing.**

## A.3 The Slice Catalog

Legend: **P0** = required for the v1 slice to be real · **P1** = strongly want. Each slice lists its **entrypoint**, the **events** it emits/consumes, and priority.

### Phase 0 — Foundation
| # | Slice | Entrypoint | Emits / Consumes | Pri |
|---|-------|-----------|------------------|-----|
| 0.1 | **Google Sign-In** — OAuth callback → upsert `users` → issue session | `http` | emits `user.registered` (first time) | P0 |
| 0.2 | **Session / current-user resolution** — `request_context` from session | `http` middleware | — | P0 |
| 0.3 | **Event outbox dispatcher** — read unpublished `domain_events` → dispatch to handlers → mark published | `worker` | consumes all events | P0 |
| 0.4 | **Award points** — handler that writes an idempotent `point_events` row | (event handler) | consumes `*.completed`/`*.passed` → emits `engagement.points_awarded` | P0 |
| 0.5 | **Embedding / indexing pipeline** — on content created → chunk → embed (OpenAI) → store in `embeddings` | `worker` | consumes `content.created` | P0 |

### Phase 1 — Learning Core
| # | Slice | Entrypoint | Emits / Consumes | Pri |
|---|-------|-----------|------------------|-----|
| 1.1 | **Start Intake** — submit goal → adaptive 3–5 questions (conversation) | `http` (SSE) | — | P0 |
| 1.2 | **Generate Course** — submit answers → enqueue generation → roadmap + Lecture 1 | `http` → `worker` | emits `course.generation_started`, `content.created` | P0 |
| 1.3 | **Generation Status Stream** — live `generation_jobs.progress` | `http` (SSE) | — | P0 |
| 1.4 | **Get Course Home / Roadmap** — course + lectures + status | `http` | — | P0 |
| 1.5 | **Get Lecture** — its docs + statuses | `http` | — | P0 |
| 1.6 | **Get Doc Content** — current variant (`is_current`) | `http` | — | P0 |
| 1.7 | **Lazy-generate Lecture** — open an unbuilt lecture → generate its docs | `http` → `worker` | emits `content.created` | P0 |
| 1.8 | **Adapt Lesson** — "explain simpler / go deeper" → new `doc_contents` variant | `http` (SSE) | emits `content.created` | P1 |
| 1.9 | **List References** — links/YouTube for a doc | `http` | — | P0 |

### Phase 2 — Tutoring
| # | Slice | Entrypoint | Emits / Consumes | Pri |
|---|-------|-----------|------------------|-----|
| 2.1 | **Ask Tutor** — RAG-grounded chat (retrieve current doc + history) → stream answer | `http` (SSE) | — | P0 |
| 2.2 | **Get Conversation** — message history for a doc | `http` | — | P0 |

### Phase 3 — Assessment
| # | Slice | Entrypoint | Emits / Consumes | Pri |
|---|-------|-----------|------------------|-----|
| 3.1 | **Get Assessment** — quiz / coding task for a lecture | `http` | — | P0 |
| 3.2 | **Submit Quiz** — auto-grade → submission → points | `http` | emits `assessment.quiz_completed` | P0 |
| 3.3 | **Submit Coding Task** — sandbox run + AI grade vs rubric | `http` → `worker` | emits `assessment.task_passed`/`task_failed` | P0 |
| 3.4 | **Get Submission Result** — status + feedback (poll/SSE) | `http` | — | P0 |

### Phase 4 — Engagement
| # | Slice | Entrypoint | Emits / Consumes | Pri |
|---|-------|-----------|------------------|-----|
| 4.1 | **Get Daily Challenge** — today's per-user set (their topics + general) | `http` | — | P0 |
| 4.2 | **Submit Daily Challenge** — grade → points → streak kept | `http` | emits `engagement.daily_completed` | P0 |
| 4.3 | **Streak update** — handler bumps `streaks` on activity | (event handler) | consumes activity events | P0 |
| 4.4 | **Get Dashboard** — streak, points, today's correct, rank | `http` | — | P0 |
| 4.5 | **Get Leaderboard** — daily/monthly from Redis ZSET | `http` | — | P0 |
| 4.6 | **Monthly Rewards** — snapshot leaderboard → pick top-N → `rewards` → reset | `worker` (scheduled) | emits `engagement.rewards_granted` | P1 |
| 4.7 | **Award Badge** — handler grants `user_badges` on criteria met | (event handler) | consumes `engagement.points_awarded` etc. | P1 |

### Phase 5 — Progress & Sharing
| # | Slice | Entrypoint | Emits / Consumes | Pri |
|---|-------|-----------|------------------|-----|
| 5.1 | **Mark Doc Read / Update Progress** — upsert `user_progress` | `http` | emits `learning.doc_read`, `learning.lecture_completed` | P0 |
| 5.2 | **Get Course Progress** — from `v_course_progress` | `http` | — | P0 |
| 5.3 | **Bookmark / Saved items** — add + list | `http` | — | P1 |
| 5.4 | **Get My Profile** — `users` + `user_stats` + currently learning | `http` | — | P0 |
| 5.5 | **Create Share link** — token + visibility + settings | `http` | — | P1 |
| 5.6 | **View Shared resource** — public read-only resolve by token | `http` (public) | — | P1 |
| 5.7 | **Revoke Share** | `http` | — | P1 |

> ~30 slices. The **bold Phase-0 slices** are the spine — points integrity, event delivery, and retrieval — and they get the most test rigor (Part B.7).

---

# Part B — Testing Strategy

## B.1 Philosophy
- **Testing is first-class.** No slice merges without its tests (B.6 Definition of Done).
- **The hexagonal design is what makes this cheap.** Because the domain depends only on **ports**, we test business logic with **fake adapters** — fast, no network, no flakiness.
- **AI is non-deterministic → never assert exact LLM text in CI.** Mock the LLM for determinism; measure *quality* separately with an eval suite (B.4).

## B.2 The Test Pyramid (mapped to our architecture)
```
        ▲  fewer, slower, highest confidence
        │   E2E (HTTP/SSE through the whole stack, AI+sandbox stubbed)
        │   Process / workflow tests (course_generation, engagement_reactions)
        │   Integration tests (each platform adapter vs real dependency)
        │   Contract tests (every adapter satisfies its port — incl. the fake)
        │   Unit tests (domain models & services with fake adapters)
        ▼  many, fast, run on every save
```

## B.3 The Test Types

| Type | Scope | Dependencies | Speed | Where |
|------|-------|--------------|-------|-------|
| **Unit** | Domain entities + services; pure logic (points math, streak rules, progress %, variant selection, rubric scoring) | **Fakes** for all ports — no I/O | ⚡ ms | `tests/unit/domains/<x>` |
| **Contract** | Each **port** has one shared test suite run against **every** adapter *and* its fake — proves Liskov substitution | Real dep for real adapters | fast | `tests/contracts/<port>` |
| **Integration** | One platform adapter vs the **real** thing: repos vs Postgres+pgvector, cache vs Redis, sandbox vs sandbox, LLM via recorded cassettes | **Testcontainers** | medium | `tests/integration/platform/<x>` |
| **Process** | Orchestration (generation pipeline, event reactions) with fake LLM/search but real event bus + DB | Testcontainers + fakes | medium | `tests/processes/<x>` |
| **E2E (API)** | Drive HTTP/SSE endpoints through the full stack; external AI + sandbox **stubbed deterministically** | Testcontainers DB/Redis | slower | `tests/e2e` |
| **Property-based** | Invariants of critical logic (ledger never double-awards; balance = Σ amounts) | fakes | fast | with unit |
| **Eval (LLM quality)** | Prompt/output *quality* on golden examples via LLM-as-judge + schema checks | real LLM | slow | `tests/evals` (nightly, not PR-gating) |

## B.4 Handling non-deterministic AI (the part everyone gets wrong)
- **In unit/process/e2e tests:** the LLM/agent is a **fake adapter** returning fixed, schema-valid output → tests are deterministic and fast. We assert *structure and behavior* (a course with N lectures was created, the right event fired, the submission was marked passed), **never exact prose**.
- **In integration tests:** real LLM calls are **recorded once (cassettes/VCR)** and replayed → realistic payloads, deterministic CI, no per-run cost.
- **Quality** (is the lesson good? is the grader fair?) is measured by the **eval suite**: golden inputs, LLM-as-judge scoring + JSON-schema validation of structured outputs, run nightly and tracked over time. It does **not** gate PRs on a pass/fail flake.

## B.5 Tooling
- **Backend:** `pytest`, `pytest-asyncio`/`anyio`, `httpx` `ASGITransport` (in-process API calls), **Testcontainers** (Postgres+pgvector, Redis), `respx`/`vcrpy` (record/replay HTTP+LLM), `polyfactory`/`factory_boy` (fixtures), `hypothesis` (property tests), `coverage.py`. Static: `ruff` + `mypy` (typed ports catch substitution bugs at compile time). Optional: `schemathesis` (fuzz the OpenAPI surface).
- **Frontend:** `Vitest` + React Testing Library (components), **Playwright** (e2e user flows), **MSW** (mock API/SSE).
- **SSE endpoints** are tested by consuming the event stream and asserting the sequence of frames (e.g. generation status `Researching → Writing → ready`).

## B.6 Definition of Done — tests required for **every** slice
A slice is not "done" until it has:
1. **Unit tests** for its domain logic — happy path **and** edge cases — using fakes.
2. **Contract tests** pass if it introduces/uses a port (the adapter + fake both satisfy it).
3. **Integration test** for any new adapter (repo/external) against the real dependency via Testcontainers.
4. **One E2E test**: an HTTP happy path **plus** at least one key failure/authorization path, AI/sandbox stubbed.
5. **Event assertions**: the correct domain events are emitted, and re-delivery is **idempotent** (no double effects).
6. **(LLM slices only)** at least one **eval case** added to the nightly suite.

## B.7 Highest-risk slices → extra rigor
These get the deepest testing because a bug here is expensive:

| Slice | Why risky | Extra testing |
|-------|-----------|---------------|
| **0.4 Award points / ledger** | Real prizes ride on it | `hypothesis` invariants (balance = Σ, no negative-from-nowhere); **concurrency test** (two events, same idempotency_key → one row); integration vs Postgres |
| **0.3 Outbox dispatcher** | At-least-once delivery; lost/dup events corrupt engagement | crash-in-the-middle test → no lost & no duplicated effects (idempotent handlers) |
| **3.3 Coding-task grader + sandbox** | Untrusted code; pass/fail must be fair & safe | sandbox isolation tests (timeout, infinite loop, network egress blocked, memory cap); rubric threshold tests; malicious-input tests |
| **1.2 Course generation pipeline** | Long, multi-step, partial failures | process tests for partial failure & resume; lazy-gen correctness; cost/step accounting |
| **0.1 Auth & sessions** | Security boundary | session forgery/expiry tests; new-vs-returning user |
| **5.6 View Shared resource** | Must never leak private data | authorization matrix tests: private/unlisted/public × owner/stranger; revoked link returns 404 |

## B.8 CI gating
- **Every PR:** static (ruff+mypy) → unit → contract → integration → process → e2e (all with Testcontainers). Must be green to merge.
- **Coverage threshold** enforced on `domains/` and `processes/` (the logic that matters); adapters covered by integration/contract tests.
- **Nightly:** the **eval suite** (LLM quality) + full e2e against real (sandboxed) AI for a smoke signal — reported, not PR-blocking.

## B.9 Test layout (mirrors `app/`)
```
server/tests/
  unit/         domains/<domain>/...        # fakes only, ⚡
  contracts/    <port>_contract.py          # run against every adapter + fake
  integration/  platform/<capability>/...   # Testcontainers
  processes/    course_generation/, engagement_reactions/...
  e2e/          <flow>_test.py              # HTTP/SSE, AI stubbed
  evals/        <prompt>_eval.py            # nightly, LLM-as-judge
  fixtures/     factories.py, fakes/        # shared fakes for every port
```

> Next doc (when we start building): `05-api-and-contracts.md` — the HTTP/SSE endpoint list + the `shared/contracts` port `Protocol`s (`TextGenerator`, `Embedder`, `VectorStore`, `CodeExecutor`, `SearchProvider`, `EventBus`), each paired with its fake for testing.
