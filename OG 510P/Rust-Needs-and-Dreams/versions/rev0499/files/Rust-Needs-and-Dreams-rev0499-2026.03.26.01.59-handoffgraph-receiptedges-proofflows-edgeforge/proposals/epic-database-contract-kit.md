# Epic proposal: Database Contract Kit

## Thesis
Rust already has serious database building blocks.
The next high-leverage contribution is not another ORM or another migration runner.
It is a **shared database contract layer** that turns schema snapshots, query-validation modes, migration execution, and test-environment assumptions into durable engineering artifacts.

That would be a worthy ecosystem contribution because it helps:
- SQLx users carry `.sqlx` and migration truth forward without treating them as incidental build debris,
- Diesel users review schema/migration state beyond generated code and local CLI history,
- SeaORM teams preserve entity-first or migration-first assumptions explicitly,
- service teams attach database evidence to releases and incidents,
- and maintainers stop reconstructing backend/version/seed assumptions from local setup lore.

## Why now
The timing is good because Rust already has the ingredients, but still not the contract:
- SQLx treats compile-time query checking and offline metadata as real workflows;
- Diesel supports both file-based and embedded migration sources;
- SeaORM now pushes entity-first and migration-first workflows side by side;
- refinery exists as an ORM-independent migration toolkit;
- and Testcontainers for Rust makes ephemeral database-backed testing routine.

Sources:
- https://docs.rs/crate/sqlx/latest
- https://docs.rs/crate/sqlx-cli/latest
- https://github.com/launchbadge/sqlx/blob/main/FAQ.md
- https://diesel.rs/guides/migration_guide.html
- https://docs.rs/diesel_migrations/latest/diesel_migrations/macro.embed_migrations.html
- https://www.sea-ql.org/SeaORM/docs/migration/setting-up-migration/
- https://docs.rs/refinery/
- https://rust.testcontainers.org/quickstart/testcontainers/

Read this together with:
- [`../design/database-contract-lane-map.md`](../design/database-contract-lane-map.md)
- [`../design/database-contract-pilot-program.md`](../design/database-contract-pilot-program.md)

## Proposed shape
Ship a narrowly scoped reference stack:
1. schemas for `db-intent/v0`, `db-schema-snapshot/v0`, `db-query-catalog/v0`, `db-migration-report/v0`, `db-test-env/v0`, `db-compat-report/v0`, `db-pack/v0`
2. adapters for SQLx offline metadata and migration directories, Diesel migration/schema surfaces, SeaORM migration/entity workflows, refinery migration runs, and Testcontainers-style environment descriptions
3. explicit reporting for validation modes and weak spots (`dynamic-sql`, `runtime-only`, `backend-specific`, `manual-step-required`)
4. CI and release examples showing database evidence attached to normal Rust delivery workflows
5. guidance for preserving raw SQL / schema / metadata artifacts instead of flattening them into one fake canonical schema language
6. lane profiles and adapter reports that keep backend authority, checked queries, dynamic queries, schema-as-code/entity posture, migration-source posture, embedded-shipping posture, and validation environments visibly distinct

The winning version is boring, adapter-heavy, and explicit about backend assumptions.
It should make today’s tools legible together rather than replacing them.

## Initial pilots
- one Axum or Actix service using SQLx + PostgreSQL + `.sqlx` + Testcontainers
- one Diesel application using file-based migrations and an embedded-migration single-binary deploy
- one SeaORM project using entity-first schema generation plus explicit migration reports
- one refinery-based service that wants migration evidence without adopting a full ORM

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve schema/query source truth and validation modes
2. **v0.2 adapters**
   - support SQLx / Diesel / SeaORM / refinery / Testcontainers evidence extraction
   - capture backend/version/extension assumptions honestly
3. **v0.3 cross-kit integration**
   - integrate with Release Pipeline, Incident, Config Set, and DocProof artifacts
   - support baseline/diff workflows across deployment candidates and rollback paths
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one ORM or one migration style

## Success metrics
- Teams can review database changes as explicit schema/query/migration/environment artifacts rather than screenshots, local containers, and issue comments.
- Query-validation strength is visible instead of hiding dynamic SQL or stale offline metadata.
- Migration runs become durable evidence instead of one-shot CLI side effects.
- Database-backed CI results become reproducible because the environment is described, not implied.
- Rust release and incident workflows can point to a durable database pack.

## Archive fit
This proposal adds an underrepresented but important domain to the concise archive: **data and persistence workflows**.
It also fills a deliberate hole left by Migration Kit, which explicitly does not try to become a generic database/data-migration framework.
Database Contract Kit is the missing relational-data substrate that can travel alongside schema contracts, releases, incidents, docs, and configuration evidence without being absorbed by any of them.
