# Gap: database schema, query, and migration contracts for Rust applications

## What is missing
Rust has strong database crates, but it still lacks a **boring, end-to-end contract workflow** for live relational database boundaries.

Today teams can separately:
- use SQLx for compile-time checked queries and offline query metadata,
- use Diesel for typed query building plus file-based or embedded migrations,
- use SeaORM for schema-first or entity-first workflows,
- use refinery as a standalone migration toolkit,
- and use Testcontainers for ephemeral database-backed integration tests.

What is still missing is the shared layer that answers:
- what live database state the application is claiming to support,
- which backends / versions / extensions / collations that claim assumes,
- what query surfaces were actually checked and by what method,
- what migrations or seed/data backfills justify the claim,
- and what portable test-environment contract CI or release tooling can consume later.

## Why it matters
This is not the same problem as generic API schemas or Rust edition/toolchain migrations.

For many Rust applications, the database is the longest-lived boundary in the system.
The dangerous questions are often not “does it compile?” but:
- can this release still run against the expected schema,
- did we remember the extension / collation / server-version assumptions,
- are our SQLx offline artifacts stale,
- did a migration actually run and leave the database in the intended shape,
- and can another machine reproduce the test environment that made us confident?

Today those answers are usually split across migration folders, generated `.sqlx` files, ORM metadata, local Docker compose snippets, CI YAML, and maintainer memory.

## Existing building blocks worth composing
- SQLx positions itself as an async Rust SQL crate with optional compile-time checked queries.
  https://docs.rs/crate/sqlx/latest
- `sqlx-cli` explicitly covers managing databases, running migrations, and generating offline query metadata.
  https://docs.rs/crate/sqlx-cli/latest
- SQLx’s FAQ documents that docs.rs cannot access the database, so projects using query macros need prepared `.sqlx` data plus `SQLX_OFFLINE=true`.
  https://github.com/launchbadge/sqlx/blob/main/FAQ.md
- `sqlx::migrate!()` embeds migrations into the binary, but on stable Rust still needs explicit build-script tracking to notice migration directory changes.
  https://docs.rs/sqlx/latest/sqlx/macro.migrate.html
- Diesel’s getting-started guide teaches the classic `up.sql` / `down.sql` migration workflow.
  https://diesel.rs/guides/getting-started/
- Diesel 2’s migration guide explains that file-based and embedded migrations now sit behind a unified `MigrationSource` abstraction.
  https://diesel.rs/guides/migration_guide.html
- `embed_migrations!` shows Diesel’s migration state can also become a compile-time artifact shipped in one executable.
  https://docs.rs/diesel_migrations/latest/diesel_migrations/macro.embed_migrations.html
- SeaORM’s migration docs and repository describe a migration system plus an entity-first workflow that can detect schema changes and generate tables/columns/keys.
  https://www.sea-ql.org/SeaORM/docs/migration/setting-up-migration/
  https://github.com/SeaQL/sea-orm
- refinery exists precisely because teams want a migration toolkit decoupled from any one ORM.
  https://docs.rs/refinery/
- Testcontainers for Rust exists because realistic integration tests often need a reproducible database dependency lifecycle.
  https://rust.testcontainers.org/quickstart/testcontainers/
  https://docs.rs/testcontainers/latest/testcontainers/

## Why existing tools are not yet the whole answer
The ecosystem has **real database point tools**, but not the **shared contract / diff / evidence layer**:
- SQLx tracks query metadata and migrations in its own way.
- Diesel tracks migrations and schema shape in its own way.
- SeaORM tracks entities, migrations, and generated code in its own way.
- refinery focuses on migrations.
- Testcontainers focuses on environment provisioning.

Teams still have to invent their own answers for:
- normalized compatibility reason codes,
- durable schema fingerprints or snapshots,
- portable query catalogs that say *how* a query was validated,
- migration-run reports that survive past local execution,
- and test-environment descriptors that capture the backend assumptions behind CI success.

## Target outcome
A project should be able to say:
- “this is the live database boundary this crate/app expects,”
- “these are the schema snapshots, query surfaces, and migration reports that justify the claim,”
- “this is the backend/version/extension/test-environment envelope the claim depends on,”
- and “this is the portable bundle CI, release, incident, and archaeology tooling can consume later.”

That would be a worthy contribution because it would make Rust’s database-heavy applications feel less like bespoke glue and more like reviewable systems.

## Lane-map correction
This gap is now better understood as a **lane-separation problem** rather than only a missing generic contract.

The archive should stop flattening:
- backend-authority posture,
- checked-query evidence,
- runtime-built/dynamic query evidence,
- schema-as-code/entity posture,
- migration-source and execution posture,
- embedded-shipping posture, and
- validation-environment receipts
into one fake “Rust database support” claim.

See [`design/database-contract-lane-map.md`](../design/database-contract-lane-map.md) and [`design/database-contract-pilot-program.md`](../design/database-contract-pilot-program.md) for the sharpened execution direction.
