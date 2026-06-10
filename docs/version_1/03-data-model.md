# DynoDoc v1 — Data Model

> The PostgreSQL data model for v1, designed to be **stable** — it should rarely need migrations, and when it does, the change should be additive (a new JSONB key or a new row), not a structural rewrite.
> Builds on [`02-architecture.md`](./02-architecture.md). The schema is organized by the same domains.

---

## 1. The Stability Principles (why this schema won't churn)

Every table follows these rules. They are the answer to *"make it so we don't change tables frequently."*

| # | Principle | What it buys us |
|---|-----------|-----------------|
| 1 | **UUID surrogate keys** (`id uuid` default `gen_random_uuid()`) | IDs never collide, never need renumbering, are safe to expose, and survive a future service split. |
| 2 | **Stable core columns + `JSONB` for the volatile edges** | New optional/experimental attributes go into a `metadata`/`spec`/`settings` JSONB column — **no migration**. We only migrate when something becomes a first-class, queried, indexed field. |
| 3 | **Append-only ledgers & an event outbox** (never `UPDATE`/`DELETE` history) | Points, submissions, and events are immutable rows. Correctness + full audit trail + replayable. |
| 4 | **Structure is separate from generated content** | Lectures/docs (structure) are stable; the AI-written body lives in versioned **content variants**. "Explain simpler / go deeper" adds a row — it never mutates structure. |
| 5 | **`text` + `CHECK` for status/type, not Postgres `ENUM`** | Adding a new status value is a one-line constraint change (or a reference-table insert), not a fragile `ALTER TYPE`. |
| 6 | **Derived read-models** (stats, streaks, leaderboard) are caches, **rebuildable from the ledger** | We can add/replace a derived view without ever touching the source-of-truth tables. |
| 7 | **Soft references across domains** (indexed `uuid`, **no** cross-schema FK) | Domains stay independently evolvable and extractable into services later. Hard FKs only *within* a domain. |
| 8 | **Polymorphic generic tables** for naturally open-ended concerns (progress, embeddings, bookmarks) | New trackable item types need no new table. |
| 9 | **Business rules live in the app layer, not the schema** | e.g. "one active course per user" is enforced in code; changing that rule needs **zero** migrations. |
| 10 | **`created_at` / `updated_at` on every table; soft-delete (`archived_at`) only where needed** | Auditing and reversible removal without losing rows. |

> **Rule of thumb:** *If an attribute is queried, filtered, joined, or constrained → it's a column. If it's just stored and read back → it's a JSONB key.*

---

## 2. Naming & Table Conventions

- **Tables:** `snake_case`, **plural** nouns (`courses`, `point_events`).
- **Columns:** `snake_case`; foreign keys are `<entity>_id`; booleans are `is_*` / `has_*`; timestamps end in `_at`.
- **Primary key:** always `id uuid`.
- **Every table has:** `id`, `created_at timestamptz not null default now()`, and (if mutable) `updated_at`.
- **Schema-per-domain:** each bounded context gets its own Postgres schema — `user`, `course`, `tutoring`, `assessment`, `engagement`, `sharing`, plus a `shared` schema for cross-cutting tables. This mirrors `app/domains/…` and reinforces the module boundary at the database level.
- **Status/type fields:** `text` with a `CHECK (... in (...))` constraint; allowed values mirror an app-layer enum.

---

## 3. Cross-Domain Reference Rule (important)

- **Inside a domain/schema:** real foreign keys with `on delete` rules — full integrity.
- **Across domains/schemas:** store the `uuid` and index it, but **no FK constraint**. e.g. `engagement.point_events.user_id` references a user logically, but isn't FK-bound to `user.users`.
- **Why:** domains can evolve and be extracted into separate services without an FK web to untangle. Referential integrity across domains is enforced by the application + events, consistent with the architecture.

---

## 4. The Schema, Domain by Domain

> Columns shown are the **first-class** ones. Assume `id`, `created_at`, `updated_at` exist per §2. `J` marks a `JSONB` column (the extensibility valve).

### 4.1 `user` domain

**`user.users`** — identity (Google) + account.
| Column | Type | Notes |
|--------|------|-------|
| `google_sub` | text unique | Google subject id (stable auth key) |
| `email` | citext unique | |
| `display_name` | text | |
| `avatar_url` | text | |
| `status` | text check (`active`,`suspended`,`deleted`) | |
| `preferences` | J | UI/learning prefs — grows without migration |
| `last_active_at` | timestamptz | |

**`user.user_stats`** — derived read-model (cache, rebuildable from ledgers/progress).
| Column | Type | Notes |
|--------|------|-------|
| `user_id` | uuid unique | soft ref |
| `total_points` | int | = SUM(`engagement.point_events.amount`) |
| `current_streak` | int | mirrors `engagement.streaks` |
| `longest_streak` | int | |
| `lectures_completed` | int | |
| `tasks_passed` | int | |
| `lines_of_code` | int | the "artifacts" number |
| `stats` | J | any future counters land here, no migration |

> Profile page = `users` + `user_stats` + a query into `course`/`engagement`. We **don't** scatter counters across the schema; they aggregate here and are recomputable.

### 4.2 `course` domain

**`course.courses`** — a roadmap (one learning journey).
| Column | Type | Notes |
|--------|------|-------|
| `owner_user_id` | uuid | soft ref |
| `title` | text | e.g. "Learn Python" |
| `slug` | text | for shareable/SEO URLs |
| `goal` | text | user's stated goal |
| `status` | text check (`draft`,`generating`,`ready`,`failed`,`archived`) | |
| `learner_profile` | J | **snapshot** of the intake answers that shaped this course |
| `generation_meta` | J | models/prompts/versions used (provenance) |
| `archived_at` | timestamptz null | soft delete |

**`course.lectures`** — ordered modules within a roadmap.
| Column | Type | Notes |
|--------|------|-------|
| `course_id` | uuid FK → courses | |
| `position` | numeric | fractional rank → insert/reorder **without renumbering** siblings |
| `title` | text | |
| `summary` | text | |
| `status` | text check (`pending`,`generating`,`ready`,`failed`) | supports lazy generation |

**`course.docs`** — the teaching docs inside a lecture (structure only).
| Column | Type | Notes |
|--------|------|-------|
| `lecture_id` | uuid FK → lectures | |
| `position` | numeric | |
| `title` | text | |
| `status` | text check (`pending`,`ready`) | |

**`course.doc_contents`** — the AI-written body, as **versioned variants** (this is principle #4).
| Column | Type | Notes |
|--------|------|-------|
| `doc_id` | uuid FK → docs | |
| `difficulty` | text check (`simpler`,`standard`,`deeper`) | the "explain simpler / go deeper" axis |
| `variant_key` | text | e.g. `js-analogy`, `default` — personalization variant |
| `body` | text | markdown lesson content |
| `is_current` | boolean | the active variant for this (doc, difficulty) |
| `generation_meta` | J | model/prompt/version that produced it |

> Adapting a lesson **inserts a new `doc_contents` row** and flips `is_current`. Structure (`docs`) never changes; history is preserved; variants are cacheable.

**`course.references`** — curated links + YouTube.
| Column | Type | Notes |
|--------|------|-------|
| `doc_id` | uuid FK → docs | (or lecture-level via nullable) |
| `type` | text check (`article`,`video`,`docs`,`youtube_channel`) | |
| `url` | text | |
| `title` | text | |
| `source_domain` | text | |
| `quality_score` | numeric | LLM/engagement-scored |
| `metadata` | J | |

**`course.generation_jobs`** — tracks async generation (feeds the SSE status screen).
| Column | Type | Notes |
|--------|------|-------|
| `course_id` | uuid FK → courses | |
| `target_type` | text check (`course`,`lecture`,`doc`) | |
| `target_id` | uuid | |
| `status` | text check (`queued`,`running`,`succeeded`,`failed`) | |
| `progress` | J | step messages: "Researching…", "Writing Lecture 1…" |
| `error` | text null | |
| `started_at` / `finished_at` | timestamptz | |

### 4.3 `tutoring` domain

**`tutoring.conversations`** — a chat thread, grounded in a doc.
| Column | Type | Notes |
|--------|------|-------|
| `user_id` | uuid | soft ref |
| `course_id` | uuid | soft ref (context) |
| `doc_id` | uuid | soft ref (the grounding doc) |
| `title` | text | |

**`tutoring.messages`** — append-only chat turns.
| Column | Type | Notes |
|--------|------|-------|
| `conversation_id` | uuid FK → conversations | |
| `role` | text check (`user`,`assistant`,`system`) | |
| `content` | text | |
| `citations` | J | retrieved chunks used (RAG provenance) |
| `token_usage` | J | cost tracking |

### 4.4 `assessment` domain

**`assessment.assessments`** — quiz or coding task attached to a lecture.
| Column | Type | Notes |
|--------|------|-------|
| `lecture_id` | uuid | soft ref |
| `type` | text check (`quiz`,`coding_task`) | |
| `title` | text | |
| `language` | text null | e.g. `python` (coding tasks; null for quiz) |
| `max_points` | int | |
| `spec` | J | **quiz:** questions/options/answers · **coding task:** prompt, rubric, starter_code, hidden tests. JSONB so new question/task shapes need no migration |

**`assessment.questions`** — reusable question bank (powers daily challenge + spaced repetition).
| Column | Type | Notes |
|--------|------|-------|
| `topic` | text | |
| `difficulty` | text check (`easy`,`medium`,`hard`) | |
| `type` | text check (`mcq`,`short_answer`) | |
| `spec` | J | prompt, options, correct answer, explanation |
| `source` | text | generated / curated |

**`assessment.submissions`** — append-only attempts (quiz answers or code).
| Column | Type | Notes |
|--------|------|-------|
| `user_id` | uuid | soft ref |
| `assessment_id` | uuid FK → assessments | |
| `attempt_no` | int | |
| `payload` | J | submitted answers / code |
| `status` | text check (`submitted`,`grading`,`passed`,`failed`) | |
| `score` / `max_score` | int | |
| `feedback` | J | per-criterion AI feedback |
| `execution_result` | J | sandbox stdout/exit/time/limits |
| `grading_meta` | J | model/rubric version |
| `graded_at` | timestamptz null | |

**`assessment.daily_challenges`** — the per-user daily set (the engagement hook).
| Column | Type | Notes |
|--------|------|-------|
| `user_id` | uuid | soft ref |
| `challenge_date` | date | **unique (`user_id`,`challenge_date`)** |
| `question_ids` | J | refs into `questions` (mix of their topics + general) |
| `responses` | J | answers + correctness (points always go via the ledger) |
| `status` | text check (`pending`,`completed`) | |

### 4.5 `engagement` domain

**`engagement.point_events`** — ⭐ the **append-only points ledger** (the heart). Everything else derives from this.
| Column | Type | Notes |
|--------|------|-------|
| `user_id` | uuid | soft ref |
| `amount` | int | can be negative (corrections) |
| `reason` | text check (`lecture_completed`,`task_passed`,`daily_correct`,`streak_bonus`,`adjustment`,…) | |
| `source_type` | text | e.g. `submission`,`daily_challenge`,`lecture` |
| `source_id` | uuid null | the originating row |
| `idempotency_key` | text **unique** | e.g. `task_passed:{submission_id}` → **prevents double-award** |
| `occurred_at` | timestamptz | |
| `metadata` | J | |

> Total points = `SUM(amount)`. Leaderboards, `user_stats.total_points` — all derived. The `idempotency_key` unique constraint is the single most important correctness guarantee once real prizes exist.

**`engagement.streaks`** — small mutable projection (rebuildable from activity).
| Column | Type | Notes |
|--------|------|-------|
| `user_id` | uuid unique | |
| `current_length` | int | |
| `longest_length` | int | |
| `last_active_date` | date | |
| `state` | J | freezes/repairs etc. later — no migration |

**`engagement.leaderboard_snapshots`** + **`engagement.leaderboard_entries`** — durable monthly history (live ranks live in Redis ZSET, not here).
| `leaderboard_snapshots` | Type | | `leaderboard_entries` | Type |
|---|---|---|---|---|
| `period_type` | text check (`monthly`) | | `snapshot_id` | uuid FK |
| `period_start`/`period_end` | date | | `user_id` | uuid (soft ref) |
| `generated_at` | timestamptz | | `rank` | int |
| | | | `points` | int |

**`engagement.rewards`** — monthly top-N prizes.
| Column | Type | Notes |
|--------|------|-------|
| `snapshot_id` | uuid FK → leaderboard_snapshots | |
| `user_id` | uuid | soft ref |
| `rank` | int | |
| `reward_type` | text | swag / subscription / badge / … |
| `details` | J | |
| `status` | text check (`pending`,`granted`,`revoked`) | |

**`engagement.badges`** (catalog) + **`engagement.user_badges`** — achievements as **data, not schema**.
| `badges` | Type | | `user_badges` | Type |
|---|---|---|---|---|
| `code` | text unique | | `user_id` | uuid (soft ref) |
| `name` | text | | `badge_id` | uuid FK → badges |
| `description` | text | | `awarded_at` | timestamptz |
| `criteria` | J | | unique (`user_id`,`badge_id`) | |
| `icon_url` | text | | | |

> New badge = a row in `badges`. Zero schema change.

### 4.6 `sharing` domain

**`sharing.shares`** — public read-only links with privacy control.
| Column | Type | Notes |
|--------|------|-------|
| `owner_user_id` | uuid | soft ref |
| `resource_type` | text check (`profile`,`course`) | |
| `resource_id` | uuid | |
| `public_token` | text unique | the un-guessable share URL key |
| `visibility` | text check (`public`,`unlisted`,`private`) | |
| `settings` | J | exactly **what** is exposed (privacy toggles grow here) |
| `revoked_at` | timestamptz null | |

---

## 5. Shared / Cross-Cutting Tables (`shared` schema)

**`shared.embeddings`** — ⭐ one polymorphic table for **all four RAG layers** (behind the `VectorStore` port).
| Column | Type | Notes |
|--------|------|-------|
| `owner_type` | text check (`doc_content`,`knowledge_chunk`,`learner_memory`,`reference`) | which RAG layer |
| `owner_id` | uuid | soft ref to the source row |
| `chunk_index` | int | |
| `content` | text | the chunked text |
| `embedding` | `vector(1536)` | pgvector; dimension pinned to OpenAI `text-embedding-3-small` (see ADR-016) |
| `metadata` | J | topic, tags, quality, etc. |

> New RAG use case = a new `owner_type` value, **not** a new table. Index: `ivfflat`/`hnsw` on `embedding`.

**`shared.knowledge_chunks`** — the vetted, reusable content corpus (RAG layer 2, the moat/cache).
| Column | Type | Notes |
|--------|------|-------|
| `topic` | text | |
| `content` | text | |
| `quality_score` | numeric | |
| `source` | text | where it came from |
| `metadata` | J | |
> Embedded via `shared.embeddings` (`owner_type='knowledge_chunk'`). Reused across courses so we don't re-pay to research the same topic.

**`shared.user_progress`** — one polymorphic table for **all** progress (principle #8).
| Column | Type | Notes |
|--------|------|-------|
| `user_id` | uuid | soft ref |
| `item_type` | text check (`course`,`lecture`,`doc`) | |
| `item_id` | uuid | |
| `status` | text check (`not_started`,`in_progress`,`completed`,`verified`) | |
| `metadata` | J | last position, percent, etc. |
| unique (`user_id`,`item_type`,`item_id`) | | |

**`shared.bookmarks`** — saved items (also polymorphic).
| Column | Type | Notes |
|--------|------|-------|
| `user_id` | uuid · `resource_type` text · `resource_id` uuid | unique together |

**`shared.domain_events`** — the **transactional outbox** for the event bus (reliable event-driven engagement).
| Column | Type | Notes |
|--------|------|-------|
| `event_type` | text | e.g. `assessment.task_passed` |
| `aggregate_type` | text · `aggregate_id` uuid | what it happened to |
| `payload` | J | the event data |
| `occurred_at` | timestamptz | |
| `published_at` | timestamptz null | null = not yet dispatched |

> Events are written **in the same transaction** as the state change, then dispatched. This guarantees "task passed → points awarded" never gets lost, and gives a replayable audit log.

---

## 6. Shared ORM Mixins & Base (`platform/database`)

Common column groups are declared **once** as declarative mixins so no table re-declares them. They live in `platform/database/` (the shared DB foundation from the architecture).

### The declarative `Base` — with a naming convention
The `Base` carries a **constraint/index naming convention** so Alembic generates **deterministic, stable names**. (Without this, autogenerated constraint names drift and migrations churn for no real reason — directly against our stability goal.)

```python
# platform/database/base.py
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
```

### The mixins
| Mixin | Adds | Applied to |
|-------|------|-----------|
| `UUIDPrimaryKeyMixin` | `id uuid` PK, default `gen_random_uuid()` | **every** table |
| `TimestampMixin` | `created_at`, `updated_at` (server defaults; `updated_at` `onupdate=now()`) | every **mutable** table |
| `SoftDeleteMixin` | `archived_at timestamptz null` + `is_archived` property | only where reversible removal matters (courses, shares) |
| `MetadataMixin` | a `JSONB` column, default `{}` (the extensibility valve) | tables that carry free-form attributes |
| `SlugMixin` | `slug text` + its index | courses (shareable/SEO URLs) |

> **Gotcha (documented so nobody trips on it):** SQLAlchemy reserves `Base.metadata`, so `MetadataMixin` names the Python attribute `meta_` (or `attributes`) while the **SQL column stays `metadata`**. Clean schema name, no ORM clash.

A typical table = `class Course(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, MetadataMixin, SlugMixin): ...`.

**Append-only tables** (`point_events`, `tutoring.messages`, `submissions`, `domain_events`) deliberately use **only** `UUIDPrimaryKeyMixin` + a single `created_at` — **no `TimestampMixin`/`updated_at`**, because they are never updated. Not having the column is how we *enforce* immutability at the schema level.

---

## 7. Database Views (derived data, always fresh)

We keep **append-only / normalized source tables** and expose **derived reads as views** — instead of storing volatile computed columns that would need constant updates (and constant migrations). This is principle #6 made concrete.

| View | Type | Derives | Why a view |
|------|------|---------|-----------|
| `shared.v_user_points_balance` | view | `SUM(amount)` per user from `point_events` | Authoritative balance; used to rebuild/verify the `user_stats` cache |
| `engagement.v_monthly_points` | view | points per user in the current period | Source for the monthly snapshot + leaderboard reconciliation |
| `assessment.v_user_assessment_status` | view | latest / `passed` attempt per `(user, assessment)` from append-only `submissions` | "Current status" derived from immutable attempts — **never an UPDATE** |
| `course.v_course_progress` | view | `% complete` per `(user, course)` from `user_progress` + doc counts | Percent is computed **on read, not stored** → no progress-column updates |
| `course.v_lecture_doc_counts` | view | doc/assessment counts per lecture | Reusable helper for progress + UI |
| `user.v_profile` | view | `users` ⨝ `user_stats` | One convenient read for the profile page |

- **Plain views in v1** — always fresh, no refresh logic to maintain.
- **Materialized views are deferred** to when an aggregate gets genuinely expensive (e.g. cross-learner analytics); they'd be refreshed by a scheduled worker. Noted, not built.
- The **live leaderboard stays in Redis ZSET** (real-time ranking); `v_monthly_points` is the durable reconciliation/snapshot source.

> **Pattern worth naming:** *append-only table + a "current state" view* (`submissions` → `v_user_assessment_status`) gives full history **and** a trivial "is it passed?" read — with zero mutation. We use this instead of an updatable status column.

---

## 8. Indexing Strategy (who gets indexed, and why)

**Principles:**
1. **Index every foreign key and cross-domain soft-ref `uuid`.** Postgres does **not** auto-index FKs, and these are our hottest join/filter columns.
2. **Index columns used in `WHERE` / `JOIN` / `ORDER BY`.**
3. **Partial indexes** for hot filtered subsets — far smaller and faster.
4. **GIN on JSONB only where we actually query into it** — never blanket (GIN has real write cost).
5. **Don't over-index** — every index taxes writes; index to real query patterns, not "just in case."

**Indexes that matter, per table:**

| Table | Index | Kind | Serves |
|-------|-------|------|--------|
| `user.users` | `google_sub`, `email` | unique | login lookup |
| `course.courses` | `owner_user_id` | btree | "my courses" |
| | `(owner_user_id) WHERE archived_at IS NULL` | partial | active courses |
| | `slug` | unique | share / SEO URL |
| `course.lectures` | `(course_id, position)` | btree | ordered listing |
| `course.docs` | `(lecture_id, position)` | btree | ordered listing |
| `course.doc_contents` | `(doc_id, difficulty) WHERE is_current` | partial unique | fetch the live variant fast |
| `course.references` | `doc_id` | btree | links for a doc |
| `course.generation_jobs` | `(status) WHERE status IN ('queued','running')` | partial | poll active jobs |
| `tutoring.messages` | `(conversation_id, created_at)` | btree | thread in order |
| `assessment.submissions` | `(user_id, assessment_id, attempt_no)` | btree | attempts |
| | `(assessment_id) WHERE status = 'passed'` | partial | verified lookups |
| `assessment.daily_challenges` | `(user_id, challenge_date)` | unique | today's set |
| `engagement.point_events` | `idempotency_key` | unique | **anti-double-award guarantee** |
| | `(user_id, occurred_at)` | btree | balance + monthly window |
| `engagement.streaks` | `user_id` | unique | |
| `engagement.user_badges` | `(user_id, badge_id)` | unique | |
| `engagement.leaderboard_entries` | `(snapshot_id, rank)` | btree | render a board |
| `sharing.shares` | `public_token` | unique | resolve a public link |
| | `(resource_type, resource_id)` | btree | shares of a resource |
| `shared.user_progress` | `(user_id, item_type, item_id)` | unique | the core lookup |
| | `(user_id, item_type)` | btree | list progress |
| `shared.bookmarks` | `(user_id, resource_type, resource_id)` | unique | |
| `shared.domain_events` | `(occurred_at) WHERE published_at IS NULL` | **partial** | **the outbox dispatcher poll** — stays tiny & fast |
| `shared.embeddings` | `embedding` | **HNSW** (pgvector) | vector similarity search |
| | `(owner_type, owner_id)` | btree | fetch/delete a source's chunks |

**Vector index decision:** **HNSW** over IVFFlat — better recall/latency at our scale and no training step. One vector index per pinned embedding model (dimension fixed, per §5).

**JSONB:** add a GIN index only on the specific JSONB columns we end up filtering on in practice. Default = no JSONB index.

---

## 9. Entity Map (high level)

```
user.users ──< course.courses ──< course.lectures ──< course.docs ──< course.doc_contents
   │                                     │                    └──< course.references
   │                                     └──< assessment.assessments ──< assessment.submissions
   │
   ├─ user.user_stats        (derived)
   ├─ engagement.point_events (ledger)  ──► leaderboard_snapshots ──< leaderboard_entries ──► rewards
   ├─ engagement.streaks / user_badges
   ├─ assessment.daily_challenges ──► (questions bank)
   ├─ tutoring.conversations ──< tutoring.messages
   └─ sharing.shares

shared.embeddings (all RAG)   ·   shared.knowledge_chunks   ·   shared.user_progress
shared.bookmarks   ·   shared.domain_events (outbox)

(— = hard FK within a domain ; ── soft uuid ref across domains)
```

---

## 10. Data-Model Decision Records

### DM-001 — Schema-per-domain + soft cross-domain references
Hard FKs within a schema; indexed `uuid` (no FK) across schemas. **Why:** integrity where it's cheap, decoupling where it matters for future service extraction.

### DM-002 — JSONB as the extensibility valve
Volatile/optional/experimental attributes live in `metadata`/`spec`/`settings`/`payload` JSONB. **Why:** features evolve weekly; we migrate only when an attribute must be queried/indexed. Promotes a JSONB key to a column *only then*.

### DM-003 — Append-only ledger for points (+ outbox for events)
`point_events` is immutable; totals are derived; `idempotency_key` is unique. **Why:** money/prizes demand correctness + audit; no "lost/double points" class of bugs.

### DM-004 — Structure separated from generated content (`doc_contents` variants)
Adapting a lesson inserts a content row and flips `is_current`. **Why:** "simpler/deeper" and personalization must not mutate or destroy structure; variants are cacheable and historical.

### DM-005 — `text` + `CHECK` instead of Postgres `ENUM`
**Why:** adding a status value is a trivial constraint change, not a fragile `ALTER TYPE` with locking pitfalls.

### DM-006 — Derived read-models are caches (`user_stats`, `streaks`, leaderboards)
Always rebuildable from `point_events` / `user_progress`. **Why:** we can add/replace derived views freely; a cache loss is recoverable.

### DM-007 — Polymorphic generic tables for open-ended concerns
`embeddings`, `user_progress`, `bookmarks` use `(type, id)`. **Why:** new trackable/embeddable kinds need no new table.

### DM-008 — Business rules stay in the app layer
e.g. "one active course per user", point amounts, gating — enforced in code, not schema. **Why:** rules change far more often than data shapes; keep migrations rare.

### DM-009 — Shared ORM mixins + constraint naming convention on `Base`
Common columns are mixins; `Base.metadata` carries a deterministic naming convention. **Why:** DRY schema, and **stable, predictable migration/constraint names** so Alembic doesn't churn on cosmetic name drift. Append-only tables omit `updated_at` to enforce immutability structurally.

### DM-010 — Derived reads as views (not stored computed columns)
Balances, progress %, and "current assessment status" are **views** over append-only/normalized tables; materialized views deferred. **Why:** no volatile computed columns to keep updated → fewer writes, fewer migrations, always-fresh reads. The *append-only table + current-state view* pattern replaces updatable status columns.

### DM-011 — Deliberate indexing (FKs/soft-refs + partials + HNSW)
Index all FKs/soft-ref uuids and real query columns; partial indexes for hot subsets (unpublished outbox, current content, passed submissions, active courses); HNSW for vectors; GIN on JSONB only where queried. **Why:** match indexes to actual access patterns — fast reads without over-taxing writes.

---

## 11. Explicitly Deferred (designed-around, not blocked)
- **Multi-tenant / orgs (B2B):** add a nullable `tenant_id` later; soft references make this non-breaking.
- **Spending points / levels, streak freezes:** land in existing JSONB (`streaks.state`) or new derived tables.
- **Dedicated vector DB:** the `embeddings` table hides behind the `VectorStore` port; migrate when scale demands.
- **Partitioning** `point_events` / `embeddings` by time — when volume warrants.

> Next doc (when we start building): `04-api-and-contracts.md` — the HTTP/SSE endpoints and the `shared/contracts` port interfaces.
