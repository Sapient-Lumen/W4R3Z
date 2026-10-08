# Design note: Data Productization Stack (Database Contract + Schema Contract + Migration Truth + Runtime Settings + Support Envelope)

Read this together with:
- [`design/database-contract-lane-map.md`](./database-contract-lane-map.md)
- [`design/database-contract-pilot-program.md`](./database-contract-pilot-program.md)
- [`design/database-contract-kit.md`](./database-contract-kit.md)

## Problem statement
Rust has strong pieces for database work, but the ecosystem still lacks a portable, boring, reviewable way to describe the **stateful data plane** of real applications.
Teams routinely need to keep the following truths straight at the same time:
- what live databases/backends/versions are actually supported,
- what schema/query evidence was validated and how,
- what migration program moves one state to another,
- what runtime settings and secrets activate those choices,
- what public API/schema contracts attach to the database story,
- and what support, release, or incident consumers may later conclude.

Today those truths are scattered across SQL migrations, ORM/entity code, CLI metadata caches, runtime settings, integration tests, docs, and release notes. The missing contribution is not “yet another ORM” but a **Data Productization Stack** that keeps those lanes distinct while still letting them compose.

## Why this deserves frontier treatment now
Rust’s official surveys still show server/backend/cloud work as major usage territory, while current pain continues to cluster around debugging, resource usage, and documentation clarity. That means stateful service and app workloads are common, but the portable evidence story around databases is still thin and fragmented. The ecosystem also shows multiple legitimate source-of-truth families rather than one winner: SQLx centers compile-time/offline query checking, Diesel keeps schema in generated Rust code, SeaORM keeps migration and entity lanes explicit, refinery focuses on standalone SQL migration execution, and testcontainers-style workflows make ephemeral database evidence practical in integration tests. A worthy ecosystem contribution should therefore connect these lanes rather than pretend one crate family will replace the others.

## Stack shape

### 1) Database Contract
Own the live relational truth — but now with explicit lane identity rather than one fake database-support bucket:
- backend-authority posture,
- checked-query evidence,
- dynamic-query evidence,
- schema-as-code/entity posture,
- migration-source and execution posture,
- embedded-shipping posture,
- validation-environment receipts,
- and explicit “validated / advisory / unknown” status.

That lane map is now spelled out in [`design/database-contract-lane-map.md`](./database-contract-lane-map.md).

Within those lanes, Database Contract still owns the concrete live relational facts the stack needs to carry:
- backend family and version floor/ceiling,
- extension/collation/transaction assumptions,
- schema snapshots and fingerprints,
- query-validation evidence,
- migration execution reports,
- test-environment descriptors,
- and explicit “validated / advisory / unknown” status.

This remains the anchor lane for real database behavior.

### 2) Schema Contract
Keep external service/data contracts distinct:
- Serde/JSON Schema/OpenAPI/Protobuf surface,
- compatibility reasoning for payloads and public interfaces,
- attachable notes about which API surfaces are backed by which database facts.

This lane must not absorb live relational truth.

### 3) Migration Truth
Own broader source→destination change programs:
- schema transitions,
- data movement and backfills,
- manual/operator steps,
- rollout sequencing,
- reversible/irreversible markers,
- and change-window assumptions.

Migration Truth may import Database Contract and Schema Contract artifacts, but it should not pretend to replace them.

### 4) Runtime Settings
Own activation truth:
- backend selection,
- connection/profile selection,
- replica/region posture,
- secret and environment-variable activation,
- offline versus live validation posture,
- and per-profile toggles that materially change data behavior.

This is where `DATABASE_URL`, feature flags, and environment selection stop being README trivia and become reviewable state.

### 5) Support Envelope + DocProof
Own what is actually promised and documented:
- supported backend/version/runtime matrix,
- docs.rs or offline-build posture,
- setup guides with explicit prerequisites,
- troubleshooting/support claims tied to specific database lanes,
- release notes or install docs that attach the right data artifacts.

### 6) Downstream consumers
These consumers should **import** data-plane artifacts rather than flatten them:
- Service Surface Kit
- Client App Surface Kit
- Release Pipeline Kit
- Policy Kit
- Incident Kit
- Canonical Learning / DocProof consumers

## What the worthy contribution should look like in practice
The archive should now treat the best data-plane contribution as a **portable evidence stack** with a ranked rollout. The next credible shared move is now explicit: pair this stack with [`proposals/epic-data-productization-stack.md`](../proposals/epic-data-productization-stack.md), a thin `cargo data-product` / `data-product-pack/v0` layer above **Database Contract + Schema Contract + Migration Truth + Runtime Settings + Support Envelope** rather than another ORM wrapper or “data platform” shell.


1. **Query/offline truth first**
   - stabilize the boring, high-value path for checked queries, offline metadata, docs.rs-safe validation posture, and explicit backend/version attachments;
   - make it easy to see what was validated live, what was validated offline, and what was never validated.

2. **Schema + migration evidence second**
   - capture schema snapshots, migration execution reports, and test-environment descriptors without requiring one universal ORM or migration engine.

3. **Runtime activation third**
   - make backend/profile/secret/region/replica activation explicit enough that deployment and support teams can tell which data posture was actually exercised.

4. **Public schema attachments fourth**
   - connect external schemas and service/client surfaces to the database lane without collapsing them into the same artifact.

5. **Support / release / incident consumers fifth**
   - give downstream tools a stable import lane so they can answer questions like “what database posture shipped?” or “what migration evidence accompanied this incident?” without rereading ad hoc docs.

## Ranked execution lanes

### Lane A — Query / offline / docs.rs truth
Focus on the places where Rust teams already feel friction:
- compile-time checked query metadata,
- offline caches for CI/docs builds,
- backend/version declarations,
- query diff reports,
- explicit “docs.rs cannot hit a live DB” posture,
- and lossiness notes when dynamic SQL or runtime-generated queries enter the picture.

### Lane B — Multi-source migration + test-environment comparison
Treat SQLx, Diesel, SeaORM, refinery, and containerized test flows as legitimate inputs:
- schema snapshots from different families,
- migration execution reports,
- test DB descriptors and image/init/reset posture,
- comparison reports across local/CI/staging lanes,
- and imported manual-step attachments for non-pure-DDL migrations.

### Lane C — Runtime activation + secrets posture
Make data-plane runtime truth portable:
- chosen backend/profile,
- selected secret source,
- connection/session capability posture,
- replica/region choices,
- retry or transactional semantics that materially affect behavior,
- and explicit activation reports for support and release consumers.

### Lane D — Public schema + service/client consumers
Join—but do not flatten—the service/client layers:
- map API fields/endpoints/messages to database evidence packs,
- attach schema-diff and migration notes where appropriate,
- expose enough traceability that service and client docs can stay honest.

### Lane E — Release / support / incident consumers
Turn the stack into durable boring operations:
- release attachments saying what data posture shipped,
- support guides pointing at real database evidence,
- incident packs importing migration/query/schema/runtime truth with timestamps and subject identity preserved.

## Non-goals
- Do **not** build a one-true universal ORM.
- Do **not** define a canonical relational schema language in v0.
- Do **not** become a hosted migration-control plane.
- Do **not** promise full static reasoning for arbitrary dynamic SQL.
- Do **not** flatten service/API schemas, live relational state, and rollout choreography into one fake “data platform” artifact.
- Do **not** replace SQLx, Diesel, SeaORM, refinery, or testcontainers-style workflows; import them honestly.

## Archive implications
This stack changes the archive in three ways:
1. **Database Contract Kit graduates upward** from a useful isolated idea into the anchor of a larger frontier seam.
2. **Schema Contract Kit and Migration Truth Stack get narrower and cleaner boundaries** because they are now explicitly related but not interchangeable.
3. **Future revisions gain a better memory discipline**: query-validation metadata, schema snapshots, migration reports, runtime settings, and support/release conclusions must no longer be merged into one vague “database readiness” note.

## Read this together with
- `design/database-contract-kit.md`
- `design/migration-truth-stack.md`
- `design/schema-contract-kit.md`
- `design/runtime-settings-kit.md`
- `design/service-productization-stack.md`
- `design/client-productization-stack.md`
- `design/data-productization-pilot-program.md`
- `proposals/epic-data-productization-stack.md`

## Pointers / sources consulted
- Rust 2024 state-of-rust survey (backend/cloud usage; common pain themes)
- Rust 2025 survey results / blog notes (docs/debug/resource signals)
- SQLx docs and FAQ (`query!`, offline mode, docs.rs posture, CLI prepare flow)
- Diesel docs (`print-schema`, generated schema-as-code lane)
- SeaORM migration docs and 2.0 migration guide
- refinery docs
- testcontainers-rs docs for integration-testing / database lifecycle patterns
