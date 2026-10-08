# Design: Database Contract Lane Map (backend authority, checked SQL, dynamic queries, schema-as-code, migrations, embedded shipping, and validation environments)

## Goal
Make the archive more precise about **what kind of database claim is actually being made**.

Rust’s database story is strong, but the ecosystem still talks too often as if one phrase — “database support” — names one coherent thing.
It does not.
A SQLx `query!()` checked against a live development database, a SQLx build that relies on prepared `.sqlx` metadata for offline/docs.rs builds, a SQLx `QueryBuilder` path for runtime-built SQL, a Diesel project whose query validity depends on generated `table!` schema code, a SeaORM project that can be schema-first **or** entity-first, a `refinery` project that wants standalone SQL migration execution, an application that embeds migrations into the shipped binary, and a test suite that provisions isolated live databases are **different but connected** lanes.

The worthy contribution here is therefore not another ORM, SQL DSL, migration engine, or hosted schema control plane.
It is a **portable lane map and evidence boundary** that lets tools say which database lane they are using, what semantics actually attach to it, where adapters are lossy, and which downstream consumers may reuse the claim honestly.

Read this together with:
- [`design/database-contract-kit.md`](./database-contract-kit.md)
- [`design/database-contract-pilot-program.md`](./database-contract-pilot-program.md)
- [`design/data-productization-stack.md`](./data-productization-stack.md)
- [`design/migration-truth-stack.md`](./migration-truth-stack.md)
- [`proposals/epic-database-contract-kit.md`](../proposals/epic-database-contract-kit.md)

## Why this note is needed now
The current database ecosystem already makes the lane split visible.
The archive should reflect that instead of flattening it.

- SQLx still defines itself around compile-time checked queries without a DSL, and its query macros still require string literals or concatenated string literals because the query must be introspectable. Its FAQ also still says docs.rs cannot access your database, so builds there need prepared `.sqlx` data plus `SQLX_OFFLINE=true`. SQLx’s repository also now says offline mode is always enabled in 0.8.x.
  https://docs.rs/crate/sqlx/latest
  https://docs.rs/sqlx/latest/sqlx/macro.query.html
  https://github.com/launchbadge/sqlx/blob/main/FAQ.md
  https://github.com/launchbadge/sqlx
- SQLx also keeps a **runtime-built SQL lane** explicit through `QueryBuilder`, `RawSql`, and `AnyConnection`; that is direct evidence that not every query surface is the same checked-macro lane.
  https://docs.rs/sqlx-core/latest/sqlx_core/query_builder/index.html
  https://docs.rs/sqlx/latest/sqlx/
  https://docs.rs/sqlx/latest/sqlx/struct.AnyConnection.html
- Diesel keeps a different validation lane sharp: its docs still say query validation depends on schema declared in code with `table!`, and `diesel print-schema` connects to the database and generates those macro calls. Diesel’s migration guide also says file-based and embedded migrations are unified behind `MigrationSource`.
  https://docs.diesel.rs/main/diesel/index.html
  https://diesel.rs/guides/schema-in-depth/
  https://diesel.rs/guides/migration-guide
- SeaORM keeps both migration-first and entity-first lanes explicit in current docs, and it keeps database-driver and async-runtime selection explicit during setup. That means source-of-truth and runtime-activation posture are both live choices rather than one fixed ORM story.
  https://www.sea-ql.org/SeaORM/docs/migration/writing-migration/
  https://www.sea-ql.org/SeaORM/docs/generate-entity/entity-first/
  https://www.sea-ql.org/SeaORM/docs/install-and-config/connection/
- `refinery` explicitly frames itself as a standalone SQL migration toolkit that can run migrations either by embedding them in Rust code or via `refinery_cli`, which proves that migration execution can be its own lane outside a full ORM.
  https://docs.rs/refinery/
- Embedded-shipping lanes are already real: `sqlx::migrate!()` embeds migrations into a static migrator but still needs a stable-Rust build-script workaround for migration-directory change tracking, while Diesel’s `embed_migrations!` and refinery’s embedded mode keep shipped migration state distinct from file-tree-only workflows.
  https://docs.rs/sqlx/latest/sqlx/macro.migrate.html
  https://docs.rs/diesel_migrations/latest/diesel_migrations/macro.embed_migrations.html
  https://docs.rs/refinery/
- Validation environments are also their own lane: `#[sqlx::test]` can create isolated live test databases automatically, while Testcontainers for Rust keeps container lifecycle and readiness/wait strategies explicit.
  https://docs.rs/sqlx/latest/sqlx/attr.test.html
  https://rust.testcontainers.org/quickstart/testcontainers/
  https://rust.testcontainers.org/features/wait_strategies/
- Diesel’s own comparison guide still compares Diesel with SQLx, SeaORM, tokio-postgres/postgres, mysql-async/mysql, and rusqlite. That is a useful ecosystem signal that Rust relational work is plural rather than converged on one lane.
  https://diesel.rs/compare_diesel.html

## The lane map

### Lane 1 — Backend authority and portability lane
**What it is**
- Which backend family and version the project is actually claiming.
- Whether validation was tied to a specific backend, a selected driver/runtime pair, or a looser runtime-dispatched connection path.

**Why it matters**
- SQLx query macros are compiled against a specific database type.
- SeaORM setup keeps chosen database driver explicit.
- Database portability claims often fail before schema or migration questions even begin.

**What the archive should preserve**
- backend family and version floor/ceiling,
- driver/runtime selection posture,
- backend-bound versus runtime-dispatched validation,
- extension/collation/pragmas assumptions,
- and any explicit portability caveats.

**What it should not pretend**
- that “supports SQL databases” is a meaningful contract,
- that successful validation against one backend family automatically transfers to another,
- or that runtime-dispatch lanes and backend-pinned lanes are interchangeable.

### Lane 2 — Checked-query lane
**What it is**
- Query surfaces validated against a live database or prepared offline metadata.
- Most visibly represented by SQLx `query!()` / `query_as!()` style workflows.

**Why it matters**
- This is the lane most likely to be overclaimed.
- Live checked queries, offline metadata, and docs.rs-safe prepared metadata are related but not identical strengths.

**What the archive should preserve**
- live-database versus offline-metadata validation,
- `.sqlx` provenance and freshness,
- literal-only / introspectable-query constraints,
- backend/type binding,
- and weak-coverage reason codes when the checked path was unavailable.

**What it should not pretend**
- that “compile-time checked” means every query in the codebase was checked,
- that stale offline metadata is equal to a fresh live validation,
- or that checked-query lanes cover runtime-generated SQL automatically.

### Lane 3 — Runtime-built and dynamic-query lane
**What it is**
- Query surfaces constructed at runtime or with weaker static guarantees.
- Includes SQLx `QueryBuilder`, raw SQL assembly, and other dynamic query pathways.

**Why it matters**
- Dynamic SQL is normal in real systems, but it changes the evidence story.
- The archive needs a place to say “this query path exists, but its validation is runtime-tested / prepared-only / manual-review” instead of silently hiding it.

**What the archive should preserve**
- dynamic versus literal query origin,
- builder/template/raw assembly posture,
- parameterization and backend assumptions,
- runtime-test versus manual-review coverage,
- and explicit unchecked or partially checked reason codes.

**What it should not pretend**
- that runtime-built SQL inherits the guarantees of checked macros,
- that builders erase backend-specific semantics,
- or that one successful integration test proves broad query-surface completeness.

### Lane 4 — Schema-as-code and entity-model lane
**What it is**
- Database shape represented as generated or handwritten Rust code.
- Most clearly visible in Diesel `table!` / `print-schema` workflows and SeaORM entity definitions.

**Why it matters**
- This lane shifts the review center from raw SQL files to generated or maintained Rust declarations.
- It is a legitimate source-of-truth family, but it is not the same as live introspection or migration-first SQL.

**What the archive should preserve**
- whether schema code was generated or handwritten,
- database-introspected versus entity-authored provenance,
- regeneration policy,
- correspondence to live database state,
- and lossiness notes when schema code omits backend-specific objects or operational details.

**What it should not pretend**
- that generated schema code and live database state are automatically identical,
- that entity declarations alone prove migration execution,
- or that schema-as-code lanes make raw SQL and backend features irrelevant.

### Lane 5 — Migration-program lane
**What it is**
- Ordered schema-change execution over time.
- Includes schema-first SQL migrations, entity-first generated migrations, and standalone migration toolkits.

**Why it matters**
- This is where source-of-truth plurality is most visible.
- SeaORM explicitly keeps schema-first and entity-first lanes visible, Diesel keeps migration sources explicit, and refinery proves standalone migration execution matters outside ORMs.

**What the archive should preserve**
- migration source family,
- ordered applied-set identity,
- reversible versus forward-only posture,
- data-backfill/manual-step attachments,
- and execution environment/backend assumptions.

**What it should not pretend**
- that every migration lane is schema-first,
- that entity-first and migration-first carry the same drift risks,
- or that a migration directory by itself proves anything was actually applied.

### Lane 6 — Embedded-shipping lane
**What it is**
- Migrations or schema state embedded into the shipped binary or library rather than left only as external files.

**Why it matters**
- Shipping posture changes operational and review semantics.
- Embedded migrations can make single-binary deploys easier, but they also require explicit provenance and change-tracking rules.

**What the archive should preserve**
- whether migrations are embedded or file-tree-only,
- build-time tracking posture,
- shipped migrator identity,
- embedded-versus-external drift risks,
- and which operational environments are expected to run the embedded path.

**What it should not pretend**
- that embedded migration state is the same thing as a migration file tree,
- that shipping migrations proves they ran,
- or that build-time embedding automatically tracks later file changes without caveats.

### Lane 7 — Validation-environment lane
**What it is**
- The live environment used to justify database claims.
- Includes isolated test databases, containerized databases, wait/readiness posture, seed/setup hooks, and reset semantics.

**Why it matters**
- Database confidence often depends less on query syntax than on which database actually ran under test.
- `#[sqlx::test]` and Testcontainers both prove the environment story deserves first-class evidence.

**What the archive should preserve**
- environment provisioning kind,
- backend image/version identity,
- wait/readiness strategy,
- seed/init/reset policy,
- isolation posture,
- and CI-safe versus best-effort local-only posture.

**What it should not pretend**
- that “tests passed” says enough about the database lane,
- that container tags without readiness/init details are reproducible truth,
- or that ephemeral test environments and production deployment environments are the same claim.

## Adapter rules
A lane map only matters if it can name **lossy boundaries**.
The archive should therefore treat these as first-class adapter classes:

1. **live checked query ↔ offline checked query**
   - can lose freshness while preserving some shape/type evidence.
2. **checked query ↔ dynamic query**
   - usually loses compile-time introspection and widens uncertainty.
3. **live schema ↔ schema-as-code**
   - can lose backend-specific objects, operational metadata, or freshness.
4. **entity-first ↔ schema-first migration source**
   - can change drift posture and regeneration assumptions.
5. **file-tree migration ↔ embedded migration**
   - can change shipping and change-tracking semantics.
6. **validation environment ↔ deployment environment**
   - can lose readiness, extension, locale, seed, and operational realism details.

Adapters should report not just “supported” or “unsupported”, but **what semantics changed**.

## What this changes in the archive
This note sharpens Database Contract Kit in one important way:

- the archive should stop treating **checked SQL**, **dynamic SQL**, **schema-as-code/entity lanes**, **migration source lanes**, **embedded shipping**, and **validation environments** as one “database support” bucket;
- pilot programs should prove those lanes separately before speaking about “Rust database support” in general;
- downstream consumers should import only the lane facts they can honestly reuse.

The worthy contribution here is therefore a thin `cargo dbcheck` / `db-pack/v0` layer whose lane profiles, adapter reports, environment receipts, and bounded consumer handoffs make relational-database truth reviewable without forcing one universal ORM or migration model.
