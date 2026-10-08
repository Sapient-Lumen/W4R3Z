# Design: Database Contract Kit (`cargo dbcheck`, `db-pack/v0`)

Read this together with:
- [`design/database-contract-lane-map.md`](./database-contract-lane-map.md)
- [`design/database-contract-pilot-program.md`](./database-contract-pilot-program.md)
- [`design/data-productization-stack.md`](./data-productization-stack.md)
- [`proposals/epic-database-contract-kit.md`](../proposals/epic-database-contract-kit.md)

## Goal
Define a portable contract for planning, verifying, diffing, and reviewing Rust relational-database workflows: schema state, query evidence, migration execution, seed/backfill assumptions, and ephemeral test environments.

This should **not** replace SQLx, Diesel, SeaORM, refinery, or Testcontainers.
It should make them compose better and make database support claims reviewable.

## References (signals)
- SQLx is a mainstream async Rust SQL crate with optional compile-time checked queries, which is strong evidence that query validation is already a first-class Rust workflow.
  https://docs.rs/crate/sqlx/latest
- `sqlx-cli` explicitly combines database management, migrations, and offline query metadata generation, but those outputs still remain tool-local.
  https://docs.rs/crate/sqlx-cli/latest
- SQLx’s FAQ says docs.rs cannot access the database, so projects using query macros must prepare `.sqlx` metadata and enable `SQLX_OFFLINE`; that is exactly the kind of externalized evidence a shared contract should record.
  https://github.com/launchbadge/sqlx/blob/main/FAQ.md
- `sqlx::migrate!()` embeds migrations into the binary, and its docs note the stable-Rust build-script workaround needed to notice migration directory changes.
  https://docs.rs/sqlx/latest/sqlx/macro.migrate.html
- Diesel’s getting-started guide uses ordered `up.sql` / `down.sql` migrations, reinforcing that schema evolution is a core workflow rather than an edge case.
  https://diesel.rs/guides/getting-started/
- Diesel 2’s migration guide says file-based and embedded migration sources now share a `MigrationSource` abstraction; this is useful proof that multiple migration representations are normal and should remain first-class.
  https://diesel.rs/guides/migration_guide.html
- `embed_migrations!` shows migration state can be compiled into the final binary, which matters for single-binary deploys and in-memory test setups.
  https://docs.rs/diesel_migrations/latest/diesel_migrations/macro.embed_migrations.html
- SeaORM’s official docs and repository show both schema-first migrations and an entity-first workflow with automatic schema-change detection, which means the ecosystem already has multiple legitimate “source of truth” models.
  https://www.sea-ql.org/SeaORM/docs/migration/setting-up-migration/
  https://github.com/SeaQL/sea-orm
- refinery exists as a database-agnostic migration toolkit, proving that many teams want migration workflows outside a full ORM.
  https://docs.rs/refinery/
- Testcontainers for Rust exists because database confidence often depends on reproducible dependency lifecycles in integration tests, not just unit tests or compile-time checks.
  https://rust.testcontainers.org/quickstart/testcontainers/
  https://docs.rs/testcontainers/latest/testcontainers/

## Lane-map correction
Database Contract Kit should now be read through the lane map in [`design/database-contract-lane-map.md`](./database-contract-lane-map.md).
The kit is still the right substrate, but future revisions should stop flattening:
- backend-authority posture,
- checked-query evidence,
- runtime-built/dynamic query evidence,
- schema-as-code and entity-model posture,
- migration-source and execution posture,
- embedded-shipping posture, and
- validation-environment receipts.

The pilot rollout for locking these distinctions in now lives in [`design/database-contract-pilot-program.md`](./database-contract-pilot-program.md).

## Core components

### 1) `db-intent/v0`
A design-time declaration of what database boundary the project intends to support.

Required ideas:
- subject identity (crate / workspace / service / deployment unit)
- backend family and versions in scope (`postgres`, `mysql`, `mariadb`, `sqlite`, etc.)
- source-of-truth mode (`sql-migrations`, `embedded-migrations`, `entity-first`, `generated-schema`, `live-introspection`)
- required extensions / pragmas / collations / server settings
- query-validation modes allowed (`compile-time-checked`, `offline-metadata`, `runtime-only`, `snapshot-only`)
- migration policy (`reversible-required`, `forward-only-allowed`, `manual-step-allowed`)
- drift posture (`must-match`, `warn-on-drift`, `introspect-and-report`)
- seed/backfill policy (`none`, `fixtures-required`, `production-backfill-attached`, `manual`)
- release attachment policy

This is the thing humans review before they trust automation.

### 2) `db-schema-snapshot/v0`
A portable description of the live schema state the project expects or observed.

Should support:
- stable schema identity and provenance
- backend family / version / extension assumptions
- snapshot source kind:
  - migration tree hash
  - introspected live database
  - generated `schema.rs`
  - SeaORM entity/migration state
  - SQL DDL dump
- raw attachment pointers instead of one fake canonical schema language
- normalized object inventory metadata (tables, columns, indexes, views, enums, triggers when available)
- content hashes / fingerprints for diffing
- optional redaction or omission for sensitive database objects

Design rule: **preserve source truth**.
Do not pretend SQL files, Diesel-generated schema, SeaORM entity metadata, and live introspection are identical.

### 3) `db-query-catalog/v0`
Records what query surfaces exist and how they were validated.

Should support:
- stable query ids and package/module provenance
- source kind (`sqlx-macro`, `raw-sql-file`, `diesel-query`, `sea-query`, `runtime-built`, `other`)
- backend assumptions and feature/target assumptions
- validation mode (`compile-time-db`, `offline-metadata`, `prepared-only`, `runtime-tested`, `not-validated`)
- optional result-shape / parameter-shape summaries
- raw attachments such as `.sqlx` metadata, generated SQL, or query fixtures
- reason codes for weak coverage (`dynamic-sql`, `backend-specific`, `test-only`, `manual-review`)

This is the missing answer to “which database-facing code paths were actually checked, and how?”

### 4) `db-migration-report/v0`
Machine-readable evidence for a migration or sequence of migrations.

Should record:
- linked `db-intent/v0`
- from/to schema snapshot identities
- migration source kind and versions applied
- transactional posture (`per-step`, `whole-run`, `non-transactional`, `backend-limited`)
- reversible / irreversible flags
- destructive-operation flags (`drop-column`, `rewrite-table`, `backfill-required`, `lock-risk`)
- execution environment (backend/version/test-env id)
- outcomes (`applied`, `skipped`, `reverted`, `failed`, `manual-step-pending`)
- optional seed or data-backfill attachments
- manual notes / rollback notes

This is not only for deployment tooling; it is also the archaeology artifact for later incidents.

### 5) `db-test-env/v0`
A portable description of the environment used to validate the database contract.

Should support:
- provisioning kind (`testcontainers`, `docker-compose`, `embedded`, `local`, `remote-ephemeral`)
- image / package identity and optional digest
- backend version / extension / locale / collation / TLS assumptions
- init hooks, migration hooks, and seed hooks
- credentials source model (`ephemeral`, `env`, `secret-ref`, `manual`)
- reset / teardown policy
- network assumptions and timeouts
- whether the environment is CI-safe, hermetic, or best-effort local only

This is the part that stops “works in CI against some Postgres container” from being folklore.

### 6) `db-compat-report/v0`
A diff/report artifact for comparing two expected or observed database states.

Should support:
- baseline identity and comparison mode
- schema deltas and query-surface deltas
- validation coverage deltas (`compile-time-checked` → `runtime-only`, missing `.sqlx`, etc.)
- migration execution verdicts
- reason codes such as:
  - `table-added`
  - `column-dropped`
  - `nullability-tightened`
  - `index-changed`
  - `backend-capability-missing`
  - `extension-missing`
  - `query-metadata-stale`
  - `dynamic-query-unchecked`
  - `migration-gap`
  - `seed-contract-changed`
- verdicts (`pass`, `warn`, `fail`, `inconclusive`)

A good compat report is about **review**, not just extraction.

### 7) `db-pack/v0`
Bundle format containing:
- `db-intent/v0`
- one or more `db-schema-snapshot/v0`
- optional `db-query-catalog/v0`
- one or more `db-migration-report/v0`
- optional `db-test-env/v0`
- optional `db-compat-report/v0`
- raw attachments and rendered summaries

This is the unit that should travel through CI, deployment review, release notes, incident packs, and later archaeology.

### 8) `cargo dbcheck`
Reference UX:
- `cargo dbcheck init`
- `cargo dbcheck snapshot`
- `cargo dbcheck queries`
- `cargo dbcheck migrate-report`
- `cargo dbcheck compat`
- `cargo dbcheck test-env`
- `cargo dbcheck pack`

`cargo dbcheck` should begin as an explainer / adapter / packer.
It should not pretend to be a universal ORM, migration runner, or hosted schema registry.

## Default policy
- **Preserve raw source truth** for schema/query artifacts.
- **Separate validation modes** instead of flattening compile-time checks, offline metadata, runtime tests, and manual review.
- **Require explicit backend assumptions** because database portability is never magic.
- **Treat migrations and seeds as evidence attachments** rather than invisible side effects.
- **Record the test environment** that made a compatibility claim believable.

## What the kit should provide to others
- **Application teams:** one way to review schema drift, query coverage, and migration execution without bespoke scripts.
- **Release Pipeline Kit:** attach database evidence to deployable artifacts or release candidates without absorbing the database story into generic release metadata.
- **Incident Kit:** preserve migration history, schema fingerprints, and environment assumptions when database incidents happen.
- **Config Set Kit:** reuse explicit feature/target/backend selections instead of rediscovering them per run.
- **DocProof Kit:** let setup guides and deployment docs point at an explicit database contract rather than README prose.
- **Schema Contract Kit:** keep external service/payload schemas distinct from live relational schema/query contracts while allowing both packs to travel together.

## Non-goals
- Do **not** replace SQLx, Diesel, SeaORM, or refinery.
- Do **not** define one canonical relational schema language in v0.
- Do **not** promise full automatic compatibility reasoning for arbitrary dynamic SQL.
- Do **not** become a hosted migration-control plane.
- Do **not** blur service/API contracts with live database state.

## Overlap boundaries
- **Not Schema Contract Kit:** that kit owns external data/service contracts (Serde, OpenAPI, Protobuf, JSON Schema). Database Contract Kit owns live relational schema, query evidence, migration runs, and test environments.
- **Not Migration Kit:** that kit is about Rust code/toolchain/dependency change choreography. Database Contract Kit is about data-store/schema evolution and its execution evidence.
- **Not Release Pipeline Kit:** release tooling should attach `db-pack/v0`, not absorb it.
- **Not Observability Kit:** runtime telemetry remains separate; this kit records the declared database boundary and validation evidence.
- **Not Config Set Kit:** Config Set chooses bounded slices; Database Contract Kit records the database-specific truths observed within those slices.

## Hard problems (explicitly scoped)
1. **Source-of-truth plurality is real**
   - SQL migrations, ORM entity models, generated schema code, and live introspection are all legitimate in different teams.
2. **Query evidence is heterogeneous**
   - compile-time checked SQL, offline metadata, runtime tests, and dynamic SQL must stay visibly different.
3. **Backend assumptions are not cosmetic**
   - extensions, collations, server versions, and transaction semantics can change truth materially.
4. **Migrations can include data movement and manual steps**
   - v0 should allow advisory/manual attachments instead of assuming a pure DDL world.
5. **Test environments lie unless described**
   - container image tags, init hooks, secrets, and teardown/reset behavior all shape what “the tests passed” actually means.

## Why this could matter
A good Database Contract Kit would make Rust’s data-heavy applications feel more honest and more reusable.
It would give the ecosystem:
- explicit database support envelopes instead of README folklore,
- one way to diff schema state and query evidence without pretending every ORM works the same way,
- durable migration reports instead of one-shot CLI runs,
- reproducible database test-environment descriptors,
- and a portable artifact that release, incident, and documentation tooling can reference later.


## Execution posture
Treat **Database Contract Kit** as the live relational-state anchor of the broader **Data Productization Stack** rather than as an isolated database helper.
Its nearest execution plan now lives in:
- `design/data-productization-stack.md`
- `design/data-productization-pilot-program.md`

The ranked pilot order should be:
1. query/offline/docs.rs truth,
2. multi-source migration + test-environment comparison,
3. runtime-settings and secret-activation handoff,
4. public schema + service/client consumer attachments,
5. release/support/incident imports.

The bar is not another ORM wrapper, migration generator, or hosted control plane.
The bar is portable stateful-data evidence that downstream consumers can import honestly.
