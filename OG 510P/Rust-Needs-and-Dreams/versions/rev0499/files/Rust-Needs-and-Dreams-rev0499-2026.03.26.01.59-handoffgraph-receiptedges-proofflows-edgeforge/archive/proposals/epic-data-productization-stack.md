# Epic proposal: Data Productization Stack (`cargo data-product`, `data-product-pack/v0`)

## One-line thesis
Build a thin Rust companion layer for **stateful data products** that links **live database truth**, **public schema truth**, **migration-program truth**, **runtime activation**, **test-environment evidence**, and **support/docs truth** into one portable review boundary without pretending SQLx, Diesel, SeaORM, refinery, and containerized database test flows have already converged into one framework or one source of truth.

## Why this is now worth doing
Rust’s data story is strong enough that the missing contribution looks like a **product boundary above the ingredients** rather than another ingredient:
- The 2025 State of Rust survey still says online documentation is the preferred canonical reference, while resource usage and debugging remain major productivity problems. That increases the value of machine-usable, reviewable data-plane artifacts over README folklore and one-off operator memory.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- SQLx is explicit about a checked-query lane and the docs make the docs/build boundary concrete: SQLx supports compile-time checked queries without a DSL, and its FAQ says docs.rs cannot access your database, so projects need prepared `.sqlx` metadata plus `SQLX_OFFLINE=true` during docs.rs builds. That is exactly the kind of portable evidence boundary a product layer should preserve.
  https://docs.rs/crate/sqlx/latest/source/FAQ.md
  https://github.com/launchbadge/sqlx/blob/main/FAQ.md
- Diesel sharpens the point from a different source-of-truth family. `diesel print-schema` connects to the database, queries the schema, and generates Rust `table!` invocations; Diesel can also be configured to re-run `print-schema` on migrations. That means generated schema code is a real lane, not just a tooling accident.
  https://diesel.rs/guides/schema-in-depth/
- SeaORM and refinery make migration plurality impossible to ignore. SeaORM’s current migration docs support schema changes and seeding with SeaQuery or raw SQL and also allow an entity-first workflow, while refinery explicitly treats standalone SQL migrations as a first-class database-agnostic workflow that can be embedded in Rust code or run via CLI.
  https://www.sea-ql.org/SeaORM/docs/migration/setting-up-migration/
  https://docs.rs/refinery/
- Testcontainers for Rust shows that ephemeral database evidence is no longer exotic. Its docs position the library as a way to create and clean up container-based dependencies for integration or smoke tests, and the quickstart emphasizes readiness/wait strategies rather than naive sleeps.
  https://rust.testcontainers.org/
  https://rust.testcontainers.org/quickstart/testcontainers/
  https://rust.testcontainers.org/features/wait_strategies/

What is still missing is the **stack-level boundary that says one Rust data product subject was reviewed with these engines/versions, these query-validation facts, these schema/migration facts, these test environments, these activated settings and secrets, these public-schema attachments, and these bounded release/support/incident conclusions**.

## Working name
- CLI: `cargo data-product`
- primary artifact: `data-product-pack/v0`

## Scope
### This epic should own
- data-product subject identity
- imported database-contract / schema-contract / migration-truth / runtime-settings / support attachments
- diffable review points across query validation, schema source-of-truth posture, migration execution, test-environment evidence, and activated backend/profile/secret posture
- bounded release / support / incident / policy / service / client / assistant handoffs
- verification of pack integrity and import references

### This epic should not own
- a universal ORM
- a universal query DSL
- a hosted migration control plane
- a one-true relational meta-schema
- flattening public API/schema truth into live relational truth
- a fake one-number “data platform readiness” badge

## Candidate artifact family
### `data-product-brief/v0`
Why the product exists, intended consumer set, data lanes in scope, supported environments, freshness budget, and review status.

### `data-product-subject/v0`
The exact service/app/workspace/release/deployment subject, imported database/schema/migration/runtime surfaces, comparison base, and environment/support scope.

### `data-product-pack/v0`
The portable review bundle linking:
- imported `db-intent` / `db-validate-report` / `db-migrate-report` / `db-testenv` attachments
- imported schema-contract and migration-truth attachments
- imported runtime-settings / secret-source / backend-profile attachments
- imported release/support/docs and optional incident handoffs
- local notes, waivers, caveats, and integrity metadata

### `data-product-diff/v0`
What changed between two review points, with separate sections for:
- engines / versions / extensions / configuration assumptions
- checked-query and offline-preparation posture
- generated-schema or introspected-schema posture
- migration execution and manual-step posture
- test-environment descriptors and readiness assumptions
- runtime activation and secret-source changes
- public schema attachments and support/docs claims

### `data-product-handoff/v0`
Bounded consumer summaries for:
- release review
- support / incident review
- policy / risk review
- service/client/schema import consumers
- atlas / adoption review
- assistant/editor rendering

## Recommended rollout
1. query / offline / docs.rs lane
2. schema + migration + test-environment lane
3. runtime activation + secret posture lane
4. public schema + service/client attachment lane
5. release / support / incident handoff lane

This should be driven by [`design/data-productization-pilot-program.md`](../design/data-productization-pilot-program.md).

## What makes this epic “epic” rather than incremental
A merely incremental tool would improve one lane:
- a nicer SQLx prepare helper,
- a nicer Diesel schema generator,
- a nicer migration runner,
- a nicer testcontainers wrapper,
- or a nicer database admin/dev shell.

An epic contribution here instead gives Rust one **portable data-product contract** above those lanes.
That is strategically different because it can:
- make release/support/incident/policy/service/client reviews share the same subject and evidence boundary;
- let checked-query, schema-as-code, migration-first, and ephemeral-test-environment workflows stay specialized without pretending any one defines the whole product;
- keep live DB truth, public schema truth, migration choreography, runtime activation, and support conclusions distinct but linked;
- and give downstream tooling a bounded artifact to import instead of re-scraping migration directories, generated schema files, env vars, docs.rs workarounds, container setup, and incident notes.

## Design principles
- **Live database truth is not public schema truth.**
- **Checked-query truth is not migration truth.**
- **Runtime activation is part of the data support surface.**
- **Ephemeral test environments are evidence, not the whole contract.**
- **Docs/build constraints (like docs.rs) belong in the product boundary.**
- **Consumer summaries are lossy on purpose and say so.**
- **The stack remains thin.**

## Success conditions
This epic is succeeding when Rust teams can say:
- “this is the exact data product subject,”
- “these are the database engines/versions/extensions we actually support,”
- “these are the checked queries, offline-preparation facts, or dynamic-query caveats we actually have,”
- “these are the schema and migration facts that were really observed or executed,”
- “these are the test environments and readiness assumptions attached to those facts,”
- “these are the settings, profiles, replicas, and secret sources that materially changed behavior,”
- “these are the public schema attachments and support/docs caveats,”
- “this is what changed from the prior review,”
- and “this is what release/support/incident/policy/service/client consumers may safely conclude,”

without inventing a bespoke “data platform readiness” schema for every repository.

## Read this with
- `gaps/database-schema-query-and-migration-contracts.md`
- `design/data-productization-stack.md`
- `design/data-productization-pilot-program.md`
- `design/database-contract-kit.md`
- `design/schema-contract-kit.md`
- `design/migration-truth-stack.md`
- `design/runtime-settings-kit.md`
- `design/support-envelope-kit.md`
