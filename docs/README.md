# DynoDoc — Documentation

This folder holds all the planning and design docs for DynoDoc.
Read them in order. Each doc has one clear job.

| Doc | What it covers |
|-----|----------------|
| [`version_1/00-product-idea.md`](./version_1/00-product-idea.md) | **The big picture.** What we're building, who it's for, why it's different, and what's in v1. Start here. |
| [`version_1/01-features-and-flow.md`](./version_1/01-features-and-flow.md) | The v1 feature set and the step-by-step user workflows. |
| [`version_1/02-architecture.md`](./version_1/02-architecture.md) | The architecture decisions (ADRs), patterns, SOLID, modules, and stack — with rationale. |
| [`version_1/03-data-model.md`](./version_1/03-data-model.md) | The PostgreSQL schema — designed for stability (rare migrations), with the points ledger and RAG storage. |
| [`version_1/04-vertical-slices-and-testing.md`](./version_1/04-vertical-slices-and-testing.md) | The catalog of vertical slices (build order) and the full testing strategy (unit/contract/integration/e2e/eval). |
| [`version_1/05-api-and-contracts.md`](./version_1/05-api-and-contracts.md) | The HTTP/SSE API design (versioning, errors, pagination, async jobs) and the `shared/contracts` port Protocols + fakes. |

> **Status:** Planning phase. We are locking the idea and scope first, then features, then architecture.
