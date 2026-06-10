# DynoDoc v1 — Architecture & Decisions

> This doc records **the architecture decisions for v1, why we made them, and the trade-offs** — written so that six months from now nobody says *"why did we do it this way?"*
> It builds on [`00-product-idea.md`](./00-product-idea.md) and [`01-features-and-flow.md`](./01-features-and-flow.md).

> **How to read this:** Sections 1–8 explain the architecture and principles. Section 9 is the list of **Architecture Decision Records (ADRs)** — the actual decisions, each with context, choice, rationale, alternatives, and consequences.

---

## 1. Architecture Goals

These are the non-negotiables every decision is measured against:

1. **Scalable** — handle growth without rewrites. Stateless app servers, externalized state, independent scaling of heavy work (AI generation).
2. **Maintainable & clean** — SOLID, clear layering, design patterns. New engineers understand it fast.
3. **Swappable externals** — LLMs, vector store, sandbox, search provider *will* change. Business logic must never depend on a specific vendor.
4. **Cost-aware** — AI is the cost center. Caching, model routing, and lazy generation are architectural, not afterthoughts.
5. **Right-sized for v1** — no premature microservices. Build a **modular monolith** with clean seams so services can be extracted later *if* needed.

---

## 2. High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Next.js (React) — Frontend                  │
│   Public pages (SEO: shared profiles/roadmaps) + App (auth)    │
└───────────────┬───────────────────────────────┬──────────────┘
                │ REST (JSON)                     │ SSE (streaming:
                │                                 │ tutor + generation status)
┌───────────────▼─────────────────────────────────▼─────────────┐
│                    FastAPI — API Layer (stateless)             │
│   Routers → Application Services (use cases) → Domain           │
└───┬─────────────┬──────────────┬───────────────┬──────────────┘
    │             │              │               │
    │ enqueue     │ ports        │ ports          │ ports
┌───▼────┐  ┌─────▼──────┐  ┌────▼─────┐   ┌──────▼───────┐
│ Queue  │  │ LLM/Agent  │  │ Vector   │   │ Code Sandbox │
│ (Arq/  │  │ (ADK)      │  │ Store    │   │ (exec port)  │
│ Redis) │  │ adapter    │  │(pgvector)│   │              │
└───┬────┘  └────────────┘  └──────────┘   └──────────────┘
    │
┌───▼─────────────────────┐     ┌───────────────────────────────┐
│  Background Workers      │     │  PostgreSQL (source of truth)  │
│  (course generation,     │     │  + pgvector (embeddings)       │
│   embeddings, monthly     │     ├───────────────────────────────┤
│   leaderboard snapshot)  │     │  Redis (cache, sessions,       │
└──────────────────────────┘     │  leaderboard sorted sets)      │
                                  └───────────────────────────────┘
```

---

## 3. The Core Pattern: Modular Monolith + Hexagonal (Ports & Adapters)

This is the single most important structural decision, so it gets its own section.

### Modular Monolith
One deployable backend, internally split into **bounded contexts** (modules) with **explicit boundaries**. Modules talk through well-defined interfaces and domain events — never by reaching into each other's tables.

**Why not microservices in v1?** Distributed systems add network failure, deployment, and data-consistency complexity that a pre-product-market-fit team should not pay for. But badly-coupled code is also a trap. The answer: a monolith with **microservice-ready seams**. If "course generation" later needs to scale independently, we extract that module into a service *without* untangling spaghetti — because the boundary already exists.

### Hexagonal (Ports & Adapters)
The **domain and application logic sit in the center and depend on nothing external.** Everything external (LLM, DB, vector store, sandbox, search, queue) is reached through a **port** (an interface defined by the domain) and implemented by an **adapter** in the infrastructure layer.

```
        ┌─────────────────────────────────────────┐
        │            Domain (pure rules)            │   ← no imports of FastAPI,
        │   entities, value objects, domain events  │     ADK, SQL, vendors
        └───────────────────┬───────────────────────┘
                            │ defines PORTS (interfaces)
        ┌───────────────────▼───────────────────────┐
        │         Application (use cases)            │   ← orchestrates domain
        │   GenerateCourse, GradeSubmission, ...     │     via ports
        └───────────────────┬───────────────────────┘
                            │ ports implemented by ADAPTERS
   ┌────────────┬────────────┼────────────┬───────────────┐
┌──▼──┐    ┌────▼────┐   ┌────▼────┐   ┌───▼────┐    ┌─────▼─────┐
│ ADK │    │pgvector │   │ Postgres│   │Sandbox │    │  Search   │
│adapt│    │ adapter │   │  repo   │   │adapter │    │  adapter  │
└─────┘    └─────────┘   └─────────┘   └────────┘    └───────────┘
```

**Why this matters for "don't regret later":** the day we swap a model, change vector DB, or replace the sandbox, we write **one new adapter** and change **zero lines of business logic**. This is the concrete payoff of the Dependency Inversion Principle.

---

## 4. SOLID — Applied Concretely (not just named)

| Principle | How we apply it in DynoDoc |
|-----------|----------------------------|
| **S** — Single Responsibility | Each agent does one job (Architect ≠ Writer ≠ Grader). Each service is one use case. A repository only persists; it doesn't decide business rules. |
| **O** — Open/Closed | New coding-task languages, new adaptive-difficulty strategies, new question types are added as **new strategy implementations** — no edits to existing code. |
| **L** — Liskov Substitution | Any `LLMProvider` adapter (ADK/Gemini, or a future one) is fully interchangeable; callers never special-case the vendor. |
| **I** — Interface Segregation | Small, focused ports: `TextGenerator`, `Embedder`, `CodeExecutor`, `SearchProvider` — not one giant "AIService" interface. |
| **D** — Dependency Inversion | Domain/application depend on **ports (abstractions)**; adapters (ADK, pgvector, sandbox) depend on those abstractions. Wiring happens at startup via a DI container. |

---

## 5. Design Patterns We'll Use (and exactly where)

| Pattern | Where | Why |
|---------|-------|-----|
| **Ports & Adapters (Hexagonal)** | Whole backend | Swappable externals; testable core |
| **Repository** | All DB access | Domain talks to `CourseRepository`, not SQL |
| **Strategy** | Model routing (cheap vs smart), adaptive difficulty, grading per language | Behavior varies without `if/else` sprawl |
| **Factory** | Building ADK agents / pipelines | Centralized, configurable agent creation |
| **Pipeline (Sequential/Parallel agents)** | Course generation | Maps to ADK Sequential/Parallel agents |
| **Adapter** | Wrapping ADK, sandbox, search | Vendor APIs hidden behind our ports |
| **Domain Events + Observer** | Engagement (points/streak/leaderboard) | A `CodingTaskPassed` event fans out to award points, update streak, update leaderboard — fully decoupled |
| **Command + Queue** | Long-running jobs (generation) | Requests become enqueued commands handled by workers |
| **DI Container** | App startup | Wires ports → adapters in one place |

> **The engagement system is event-driven on purpose.** When something good happens (lecture done, task passed, daily challenge complete), we publish a **domain event**. Separate handlers award XP, bump the streak, and update the leaderboard. Adding a new reaction later (e.g. "send a notification") = add a new handler, touch nothing existing. This is Open/Closed in action.

---

## 6. Bounded Contexts (the Domains)

Each bounded context is one folder under `app/domains/` (see §10). It owns its own data and rules:

| Domain (`domains/…`) | Owns | Capabilities it uses (via `shared/contracts`) |
|--------|------|--------------------|
| **`user`** | Google auth identity, profile, stats | — |
| **`course`** | Roadmaps, lectures, docs, adaptive lessons | LLM, Search, VectorStore |
| **`tutoring`** | The right-side AI chat, grounded in current doc | LLM, VectorStore |
| **`assessment`** | Quizzes, coding tasks, AI grading | LLM, CodeExecutor |
| **`engagement`** | Points/XP, streaks, daily challenge, leaderboard, rewards | Cache (Redis ZSET) — reacts to domain events |
| **`sharing`** | Public read-only views, share links, privacy | — |

> Multi-step work that spans domains (course generation, engagement reactions, monthly rewards) lives in `app/processes/`, not inside a domain. Domains communicate via **domain events** or **processes**, never by direct table access or domain→domain imports. This is the seam that makes future service-extraction painless.

---

## 7. Data Architecture

Three stores, each with a clear job (decided in ADR-007/008):

- **PostgreSQL** — the **source of truth**: users, profiles, courses, lectures, docs, progress, submissions, points ledger, leaderboard history. Strong consistency where it matters (points must never be wrong).
- **pgvector (inside Postgres)** — **embeddings** for all four RAG layers. One database to operate in v1; we can graduate to a dedicated vector DB later behind the same `VectorStore` port.
- **Redis** — **hot, ephemeral, fast**: sessions, response cache, rate limits, and **leaderboard sorted sets** (real-time ranking is exactly what Redis ZSET is built for). The **monthly leaderboard is snapshotted into Postgres** so history is durable.

**Points integrity rule:** points are written as an **append-only ledger** in Postgres (every award is a row), and aggregates/leaderboards are derived. This prevents "lost or double-counted points" bugs and gives a full audit trail — important the moment real prizes are involved.

---

## 8. Async, Streaming & The Generation Pipeline

**The defining runtime challenge:** course generation takes 30s–2min. It **cannot** run inside an HTTP request.

- **Generation runs in background workers** via a Redis-backed queue (Arq — async-native, fits FastAPI). The API enqueues a job and returns immediately with a job id.
- **Status streams to the UI via SSE** ("Researching… structuring… writing Lecture 1…"). Same SSE mechanism streams **tutor chat tokens**.
- **Lazy lesson generation:** roadmap + Lecture 1 generated on submit; later lectures generated when first opened (cost + speed).
- **Cost controls are architectural:**
  - **Model routing (Strategy):** cheap model (Haiku) for classification/quiz-gen/tagging; strong model (Opus) for roadmap planning and lesson writing.
  - **Knowledge-base cache (RAG layer 2):** generated, vetted content is embedded and reused, so we don't re-pay to research the same topic.

ADK's role is scoped (ADR-003): it orchestrates the **generation pipeline** (Sequential + Parallel agents) and the **runtime tutor/grader agents (tools)** — it is **not** the web framework and does not leak past the Learning/Tutoring/Assessment adapters.

---

## 9. Architecture Decision Records (ADRs)

Each ADR: **Context → Decision → Why → Alternatives rejected → Consequences.**

### ADR-001 — Modular Monolith (not microservices) for v1
- **Context:** Small team, pre-PMF, but we want to scale later.
- **Decision:** One deployable backend, split into bounded-context modules with explicit boundaries + domain events.
- **Why:** Avoids distributed-system tax now; clean seams let us extract services later without a rewrite.
- **Alternatives rejected:** Microservices (premature, slows v1); big-ball-of-mud monolith (regret guaranteed).
- **Consequences:** Discipline required to respect module boundaries (no cross-module table access). Worth it.

### ADR-002 — Hexagonal (Ports & Adapters) + Dependency Inversion
- **Context:** LLMs, vector DBs, sandboxes, search APIs will change.
- **Decision:** Domain/application depend only on ports; all vendors are adapters wired by a DI container.
- **Why:** Swap any external by writing one adapter; core stays untouched and unit-testable with fakes.
- **Alternatives rejected:** Calling ADK/SDKs directly from services (vendor lock-in, untestable).
- **Consequences:** A little upfront interface boilerplate; massive long-term flexibility.

### ADR-003 — Google ADK scoped to orchestration only
- **Context:** ADK is mandatory and powerful, but frameworks tend to sprawl.
- **Decision:** ADK lives **behind adapters** in Learning/Tutoring/Assessment. It orchestrates agents (Sequential pipeline, Parallel research fan-out, tool-using tutor/grader). It is **not** the API layer or the app's backbone.
- **Why:** Keeps ADK's reach contained; if it ever needs replacing, the blast radius is the adapters.
- **Alternatives rejected:** ADK as the central app framework (couples everything to it).
- **Consequences:** A thin abstraction over ADK; we accept that to protect the core.

### ADR-004 — FastAPI for the API layer
- **Decision:** FastAPI (async).
- **Why:** Async fits long AI calls + SSE streaming; Python ecosystem matches ADK/AI tooling; Pydantic gives clean validation at the boundary.
- **Alternatives rejected:** Django (heavier, sync-first); Node (splits the AI stack across languages).
- **Consequences:** We lean on async correctly (no blocking calls in handlers).

### ADR-005 — Next.js (App Router) for the frontend
- **Decision:** Next.js with React.
- **Why:** SSR for **public shared profiles/roadmaps = SEO = free organic growth**; great DX; one obvious choice.
- **Alternatives rejected:** Plain React SPA (no SSR/SEO); separate marketing+app stacks (duplication).
- **Consequences:** Clear split of server components (public/SEO) vs client components (tutor, editor).

### ADR-006 — Async jobs via Arq (Redis queue) + SSE for status/streaming
- **Decision:** Long jobs run in Arq workers; progress + tutor tokens stream over SSE.
- **Why:** Generation can't block a request; Arq is async-native (fits FastAPI) and lightweight; SSE is simpler than WebSockets for our mostly one-way streaming.
- **Alternatives rejected:** Celery (heavier, sync-rooted) — still a fine fallback; WebSockets (overkill for v1); doing it inline (times out, doesn't scale).
- **Consequences:** Redis becomes infrastructure we must run (we need it anyway for cache + leaderboard).

### ADR-007 — PostgreSQL as the single source of truth
- **Decision:** Postgres for all transactional/relational data.
- **Why:** Mature, relational fit for courses/users/progress; **points as an append-only ledger** needs transactional integrity.
- **Alternatives rejected:** NoSQL-first (our data is relational; we'd fight it).
- **Consequences:** We model carefully and use migrations from day one.

### ADR-008 — pgvector now, dedicated vector DB later (behind a port)
- **Decision:** Store embeddings in pgvector; hide it behind a `VectorStore` port.
- **Why:** One database to run in v1; "good enough" to millions of vectors; the port lets us move to Pinecone/Qdrant later with zero domain changes.
- **Alternatives rejected:** Standalone vector DB on day one (extra ops, premature).
- **Consequences:** Watch index performance; migrate when (if) it actually hurts.

### ADR-009 — Redis sorted sets for live leaderboards; monthly snapshot to Postgres
- **Decision:** Real-time ranks in Redis ZSET; snapshot + reset monthly into Postgres.
- **Why:** ZSET is purpose-built for ranking at speed; Postgres keeps durable history for rewards/audits.
- **Alternatives rejected:** Computing ranks from SQL on every request (slow at scale).
- **Consequences:** Redis is treated as a cache of a Postgres-derived truth (the points ledger), so a Redis loss is recoverable.

### ADR-010 — Code sandbox behind a `CodeExecutor` port
- **Context:** Running untrusted user code is the riskiest part of the moat.
- **Decision:** Define a `CodeExecutor` port; start with a managed sandbox (e.g. E2B) **or** self-hosted (Judge0 / Docker-per-run) — chosen as an adapter, not baked into logic.
- **Why:** Isolation/security is non-negotiable; abstracting it lets us switch providers as cost/security needs evolve.
- **Alternatives rejected:** Executing code in the API process (catastrophic security risk).
- **Consequences:** Network egress, timeouts, and resource limits enforced in the adapter.

### ADR-011 — Engagement is event-driven (domain events)
- **Decision:** Learning/Assessment publish domain events; Engagement handlers react (award XP, update streak/leaderboard).
- **Why:** Decouples the addictive-loop features from the learning features; new reactions = new handlers (Open/Closed).
- **Alternatives rejected:** Hard-coding points logic inside learning services (tight coupling, fragile).
- **Consequences:** Need a simple in-process event bus in v1 (upgradeable to a real broker later).

### ADR-012 — Coding tasks: Python-only in v1
- **Decision:** Support **one language (Python)** for graded coding tasks in v1; design the grader/sandbox via Strategy so more languages are additive.
- **Why:** Keeps the sandbox + grading rubric simple while still proving the moat; most-requested first skill anyway.
- **Alternatives rejected:** Multi-language at launch (multiplies sandbox/grader complexity).
- **Consequences:** Non-Python skills can still be taught; their tasks are quizzes/conceptual until we add languages.

### ADR-013 — Free navigation + "verified" badges (no hard gating)
- **Decision:** Users move freely between lectures; passing the task earns a **verified** badge, it doesn't unlock.
- **Why:** Less frustration for self-learners; badges + points provide the motivation instead of locks.
- **Alternatives rejected:** Must-pass-to-unlock (raises drop-off).
- **Consequences:** Progress/verification are tracked but not enforced as gates.

### ADR-014 — Package-by-domain layout (`domains / entrypoints / platform / processes / runtime / shared`)
- **Context:** We want high cohesion, painless future service-extraction, and a layout where a feature lives in one place. Layer-first folders scatter one feature across the tree.
- **Decision:** Organize `app/` by **domain (vertical slice)** under a fixed set of top-level packages: `domains/`, `entrypoints/`, `platform/`, `processes/`, `runtime/`, `shared/`. Everything about a domain (e.g. `user`) lives in that domain's folder.
- **Why:** Touching "assessment" = open one folder; a domain can later become its own service by moving one directory; the top-level packages make the **dependency direction explicit and enforceable**.
- **Alternatives rejected:** Layer-first (`domain/application/adapters` at top — spreads each feature everywhere); generic `api/core/models/services` (turns into dumping grounds).
- **Consequences:** Dependency rules (§10.1) are enforced by convention/lint; cross-domain calls go through `processes/` or domain events, never direct domain→domain imports.

### ADR-015 — RAG is first-party (our ports), not LangChain or Vertex RAG Engine
- **Context:** RAG could be delegated to LangChain or ADK's managed Vertex AI RAG Engine. But our RAG is bespoke: 4 layers (doc grounding, knowledge base, learner memory, cross-learner), a polymorphic pgvector store, and tight cost control.
- **Decision:** Build RAG ourselves as a thin pipeline behind ports — `Embedder` + `VectorStore` + a `Retriever` service that chunks, retrieves, ranks, and assembles context. **Expose `retrieve(...)` to ADK agents as a tool.** Small utilities (e.g. a text splitter) sit behind our own interfaces; **no LangChain runtime, no Vertex RAG Engine corpus.**
- **Why:** Full control over chunking/retrieval/ranking/cost; no heavy-framework abstraction debt; no lock-in to a Google-managed corpus; matches the hexagonal design. LangChain/ADK-RAG can't cleanly model learner-memory + per-doc grounding the way we need.
- **Alternatives rejected:** LangChain (hidden control flow, dependency churn); Vertex AI RAG Engine (couples the corpus to Google infra, weak fit for our custom layers).
- **Consequences:** We own a small, highly-testable retrieval codebase. Agents still get RAG via a clean tool.

### ADR-016 — Embeddings via OpenAI `text-embedding-3-small` (1536-dim), behind the `Embedder` port
- **Context:** We need an embedding model; the generation LLM (ADK/Gemini/Claude) is independent of embeddings.
- **Decision:** Use OpenAI **`text-embedding-3-small` (1536 dims)**. Pin one model → `vector(1536)` + one HNSW index. Mixed-provider (OpenAI embeddings + non-OpenAI generation) is fine — the `Embedder` port decouples it.
- **Why:** Strong quality/cost, widely supported, and supports dimension-shortening later if we want smaller vectors. Decoupled from the generator.
- **Alternatives rejected:** `text-embedding-3-large` (3072-dim, pricier, marginal gain now); Gemini embeddings (kept swappable via the port).
- **Consequences:** Changing the model later means re-embedding the corpus (acknowledged); the port makes that swap mechanical.

---

## 10. Folder Structure (reflects the architecture)

**Backend (`server/`)** — package-by-domain. Top-level packages under `app/` map to clear roles:

```
server/
  app/
    domains/            # ❤️ business logic — one folder per bounded context (vertical slice)
      user/             #   identity + profile
      course/           #   roadmap, lectures, docs, adaptive lessons
      tutoring/         #   the right-side AI chat
      assessment/       #   quizzes, coding tasks, grading
      engagement/       #   points/XP, streaks, daily challenge, leaderboard, rewards
      sharing/          #   public read-only views, share links, privacy

    entrypoints/        # how the outside world ENTERS the app (driving adapters)
      http/             #   FastAPI routers, request/response schemas, SSE endpoints, exception handlers
      mcp/              #   MCP server exposing DynoDoc capabilities as tools
      workers/          #   Arq worker entrypoints (consume queued jobs → call processes)

    platform/           # technical capabilities the app RUNS ON (driven adapters; implement shared contracts)
      auth/             #   Google OAuth (OIDC), token verification, session issuing
      database/         #   SQLAlchemy engine, session factory, Base, unit-of-work
      cache/            #   Redis client (cache, sessions, leaderboard ZSETs)
      llm/              #   ADK adapter + model router (cheap vs strong) + prompt management
      agents/           #   ADK agent & pipeline definitions + factory  (Sequential/Parallel)
      vectorstore/      #   pgvector adapter (implements VectorStore contract)
      sandbox/          #   code-executor adapter (E2B / Judge0) — runs untrusted code
      search/           #   web-search adapter (Exa / Tavily)
      queue/            #   Arq enqueue client
      events/           #   in-process event bus implementation
      telemetry/        #   logging, tracing, per-generation cost tracking

    processes/          # cross-domain orchestration / workflows / sagas (coordinate many domains)
      course_generation/    #   the big one: intake → architect → research → write → curate → assess
      engagement_reactions/ #   event handlers: on TaskPassed → award XP, bump streak, update leaderboard
      monthly_rewards/      #   scheduled: snapshot leaderboard → pick winners → reset

    runtime/            # app composition + lifecycle (the only place concretes meet abstractions)
      settings.py       #   12-factor config (Pydantic Settings)
      bootstrap.py      #   DI wiring: build platform adapters, bind contracts→impls, register handlers
      application.py    #   build the ASGI app, mount entrypoints/http
      lifespan.py       #   startup/shutdown (db pool, redis, warm caches)
      request_context.py#   per-request context (current user, request/correlation id) via contextvars

    shared/             # leaf — sharable everywhere, depends on NOTHING internal
      contracts/        #   technical capability ports: TextGenerator, Embedder, VectorStore,
                        #     CodeExecutor, SearchProvider, EventBus, QueuePublisher, Clock, UnitOfWork
      errors/           #   base exceptions + error taxonomy
      events/           #   base domain-event types + bus interface
      result.py         #   Result/Either type, common value objects, typed IDs
      pagination.py, types.py, ...

  tests/                # sibling of app/ — unit (domains/processes with fakes), integration (platform), e2e (http)
  migrations/           # Alembic
  pyproject.toml
```

### Inside a single domain (e.g. `domains/user/`)
Everything about the domain, colocated:
```
domains/user/
  models.py         # entities + value objects (pure — imports only shared)
  schemas.py        # DTOs (in/out) for this domain
  events.py         # domain events this context emits (e.g. UserRegistered)
  errors.py         # domain-specific errors
  repository.py     # the repository PORT (Protocol/ABC) — pure
  service.py        # use-case logic for this domain (depends on ports)
  persistence.py    # repository IMPLEMENTATION (SQLAlchemy tables + repo) — the ONLY file
                    #   in the domain allowed to import platform (database session/Base)
```
> **The one rule that keeps it clean:** a domain's *core* (`models`, `service`, `repository` port, `events`) imports **only `shared/`**. The single `persistence.py` adapter file is the only place allowed to touch `platform/`. This keeps the core unit-testable with fakes while still colocating everything for the domain.

### §10.1 — Dependency Rules (the "what calls what")
Arrows point in the **allowed import direction**:

```
entrypoints ──▶ processes ──▶ domains ──▶ shared ◀── platform
     │                          ▲                       ▲
     └──────────▶ domains ──────┘                       │
                                                         │
runtime ──▶ (imports EVERYTHING: wires platform impls into domains/processes)
```

- **`shared/`** depends on nothing internal. (leaf)
- **`domains/`** import only `shared/`. **Never** import another domain, `platform`, `processes`, or `entrypoints`. (The lone exception: `persistence.py` may import `platform/database`.)
- **`platform/`** implements `shared/contracts`; stays generic; does **not** import domains.
- **`processes/`** orchestrate: import domain services + `shared/contracts`. Cross-domain coordination lives here.
- **`entrypoints/`** call `processes/` and domain services; translate transport ↔ app. No business logic.
- **`runtime/`** is the **composition root** — the only place that imports concrete `platform` adapters and binds them to the contracts that domains/processes depend on.
- **Cross-domain communication** happens via `processes/` or **domain events** on the bus — never a direct `domains/a → domains/b` import.

### Why `processes/` earns its place (you asked)
Yes, keep it. Some work doesn't belong to any single domain:
- **Course generation** touches `course` + `assessment`, and drives `llm`/`search`/`vectorstore` — it's a multi-step pipeline, not one domain's method.
- **Engagement reactions** listen to events from `course`/`assessment` and update `engagement` — a process manager / saga.
- **Monthly rewards** is a scheduled workflow.

Putting these in `processes/` keeps domains pure and focused, and makes the orchestration explicit instead of hidden inside a domain that "reaches into" others.

### Concept → folder mapping (so §3–§9 still line up)
| Hexagonal / DDD concept | Lives in |
|---|---|
| Domain core (entities, rules) | `domains/<x>/` (models, service, events) |
| Ports — domain-specific | `domains/<x>/repository.py` |
| Ports — technical capabilities | `shared/contracts/` |
| Driven adapters (DB, LLM, vector, sandbox, search, cache) | `platform/` (+ domain `persistence.py`) |
| Driving adapters (HTTP, MCP, workers) | `entrypoints/` |
| Use-case orchestration / sagas | `processes/` |
| Composition root / DI container | `runtime/bootstrap.py` |
| Cross-cutting primitives | `shared/` |

**Frontend (`client/`)** — Next.js App Router, feature-first:
```
client/
  app/                      # routes; (public)/ for SEO, (app)/ for authed
  features/                 # learning/, tutor/, assessment/, engagement/, profile/, sharing/
  components/               # shared UI
  lib/                      # api client, SSE client, auth
  stores/                   # client state (e.g. Zustand)
```

---

## 11. Cross-Cutting Concerns

- **Security:** Google OAuth (OIDC); sandbox isolation (ADR-010); rate limiting (Redis); input validation (Pydantic); awareness of **prompt injection** in tutor/RAG (treat retrieved + user text as untrusted).
- **Observability:** structured logging, request tracing, and **per-generation cost/latency tracking** (AI spend must be visible from day one).
- **Testing:** domain/application tested with **fake adapters** (no network) — the payoff of hexagonal; integration tests per adapter.
- **Config:** 12-factor — all secrets/endpoints via env; no vendor keys in code.
- **Migrations:** Alembic from commit one.

---

## 12. Explicitly Deferred (so it's a conscious choice, not an oversight)
- Microservice extraction · dedicated vector DB · multi-language sandbox · real message broker (Kafka/RabbitMQ) · multi-region · CDN for generated content · WebSockets. All have a **clean upgrade path** because of the ports/seams above.

---

## 13. Decisions Still Needing Your Sign-off
Most are pre-decided above with rationale; these are the few worth your explicit nod:
1. **Arq vs Celery** for the queue — recommended **Arq** (async-native). Override if the team knows Celery well.
2. **Sandbox provider** — managed **E2B** (fastest path) vs self-hosted **Judge0/Docker** (more control, cheaper at scale). Both fit ADR-010's port.
3. **One active course per user in v1**, or several? (Affects Course Home + profile UI only — not core architecture.)

> Once these are confirmed, the next doc is `03-data-model.md` — the PostgreSQL schema + the points ledger + the learner-state model.
