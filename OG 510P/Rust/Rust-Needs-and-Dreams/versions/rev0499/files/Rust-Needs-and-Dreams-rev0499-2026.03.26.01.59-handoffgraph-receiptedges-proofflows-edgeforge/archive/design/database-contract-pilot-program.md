# Design: Database Contract Pilot Program

## Goal
Turn Database Contract Kit from a good conceptual map into a **ranked execution plan**.

Rust already has enough relational-database tooling to prove the gap is real.
The next step is not more ORM comparison.
It is a pilot sequence that shows Rust projects can publish **reviewable database truth** across backend authority, checked-query posture, dynamic-query posture, schema-as-code lanes, migration sources, embedded shipping, and validation environments without pretending those lanes have already converged.

Read this together with:
- [`design/database-contract-kit.md`](./database-contract-kit.md)
- [`design/database-contract-lane-map.md`](./database-contract-lane-map.md)
- [`design/data-productization-stack.md`](./data-productization-stack.md)
- [`design/migration-truth-stack.md`](./migration-truth-stack.md)
- [`proposals/epic-database-contract-kit.md`](../proposals/epic-database-contract-kit.md)

## Why this needs its own design layer
The Database Contract Kit already defines the base artifact family: intent, schema snapshot, query catalog, migration report, test environment, compatibility report, and pack artifacts.

What it did **not** yet answer clearly enough is:
- which database lanes should be piloted first,
- which distinctions are worth locking in early,
- how to keep checked-query evidence separate from dynamic-query evidence,
- how to keep schema-as-code posture separate from live-database and migration-execution posture,
- how to keep embedded-shipping claims separate from execution claims,
- and what counts as pilot success versus another ORM comparison page.

Without that layer, database-contract work risks two bad outcomes:
1. **database flattening** — the archive starts implying SQLx, Diesel, SeaORM, and refinery differ mostly in syntax or taste;
2. **environment theater** — one successful local or CI run impersonates evidence for broader backend, migration, or operational claims.

## Design principles
1. **Start from exact lane identity.** Every pilot should say which database lane it is proving.
2. **Keep backend authority public.** Backend family, version, extensions, collation, and runtime/driver choices should stay visible.
3. **Keep checked and dynamic queries separate.** Weakening query-construction guarantees must be explicit.
4. **Keep schema source families distinct.** Live introspection, generated schema code, entity-first models, and migration files are related but not identical.
5. **Keep migration execution separate from migration shipping.** Embedded migrations and applied migrations are different truths.
6. **Treat environments as evidence.** Container image, readiness, seed, reset, and isolation details matter.
7. **Prefer vectors that reveal lossiness.** Stale offline metadata, untracked migration directory changes, backend-specific DDL, and seed/init drift matter more than feature matrices.
8. **Consumer handoffs must stay bounded.** Release, support, service, and incident layers should only claim the database-lane facts actually exported.

## Artifact family
### 1. `db-pilot-brief/v0`
Why this database lane is being piloted.

Should record:
- pilot id and summary
- lane family (`backend-authority`, `checked-query`, `dynamic-query`, `schema-as-code`, `migration-program`, `embedded-shipping`, `validation-env`, `migration`)
- why the lane matters now
- intended consumer(s)
- why the lane is tractable now

### 2. `db-lane-profile/v0`
The declared contract for the lane.

Should record:
- primary crate/tool family
- backend and runtime assumptions
- source-of-truth posture
- validation method
- freshness/drift assumptions
- adapter/lossiness notes
- explicit unsupported areas

### 3. `db-query-budget/v0`
The bounded questions the pilot must answer.

Should record:
- named semantic questions in scope
- required answer fields
- required uncertainty classes
- mandatory vector coverage
- explicit out-of-scope questions

### 4. `db-consumer-handoff/v0`
How a downstream consumer may reuse the pilot.

Should record:
- consumer class (`release-review`, `service-review`, `incident-review`, `migration-review`, `support`, `docs`, `policy`)
- which artifacts are consumed directly
- which claims remain advisory only
- what the consumer must still verify independently

### 5. `db-pilot-scorecard/v0`
Decides whether widening is justified.

Should ask:
- did the pilot preserve lane identity honestly?
- did it make lossy adapters explicit?
- did it attach concrete vectors and reports?
- did at least one real consumer import it?
- did it avoid claiming universal database truth?

### 6. `db-pilot-pack/v0`
Bundle of:
- pilot brief
- lane profile
- query budget
- consumer handoff
- database-contract artifacts from the base kit
- scorecard
- references and rendered summaries

## Ranked first pilots

### 1) Checked-query and offline-metadata lane
**Why first**
- SQLx already gives the clearest “query was checked” story in Rust.
- The docs.rs / `.sqlx` / `SQLX_OFFLINE` distinction is exactly the kind of reviewable evidence boundary the archive should lock in early.

**Primary artifacts**
- `db-intent/v0`
- `db-query-catalog/v0`
- `db-compat-report/v0`
- vectors for live-versus-offline validation, stale metadata detection, backend binding, and literal-only coverage gaps

**Primary consumers**
- library/service reviewers
- docs/build consumers
- release and support consumers

### 2) Schema-as-code versus live-schema lane
**Why second**
- Diesel makes schema-as-code unusually explicit.
- This pilot creates the baseline rule that generated or authored Rust schema declarations are not interchangeable with live database state.

**Primary artifacts**
- `db-schema-snapshot/v0`
- `db-compat-report/v0`
- vectors for live introspection versus generated schema, regeneration freshness, and omitted backend-specific objects

**Primary consumers**
- migration reviewers
- service/data maintainers
- support consumers

### 3) Migration-source plurality lane
**Why third**
- SeaORM and refinery make it obvious that migration-first, entity-first, and standalone migration execution are all live postures.
- This is where the archive can prevent fake convergence early.

**Primary artifacts**
- `db-intent/v0`
- `db-migration-report/v0`
- `db-compat-report/v0`
- vectors for schema-first versus entity-first flows, reversible/irreversible markers, manual-step attachments, and backend-specific migration behavior

**Primary consumers**
- migration reviewers
- release/deploy consumers
- incident consumers

### 4) Embedded-shipping lane
**Why fourth**
- SQLx, Diesel, and refinery all make embedded-shipping lanes real enough to deserve direct evidence.
- The archive should prove that “embedded” and “applied” stay separate truths.

**Primary artifacts**
- `db-migration-report/v0`
- `db-schema-snapshot/v0`
- vectors for embedded migrator identity, build-script tracking posture, file-tree drift, and shipped-versus-executed state

**Primary consumers**
- single-binary deploy reviewers
- firmware/edge/local-first consumers
- support consumers

### 5) Validation-environment lane
**Why fifth**
- This lane should arrive before the archive starts narrating strong deploy confidence.
- `#[sqlx::test]` and Testcontainers already give enough substrate to prove environment receipts are practical.

**Primary artifacts**
- `db-test-env/v0`
- `db-migration-report/v0`
- `db-compat-report/v0`
- vectors for image/version, wait strategy, seed/init hooks, isolation, reset behavior, and local-versus-CI differences

**Primary consumers**
- CI/release reviewers
- service and incident consumers
- support/documentation consumers

### 6) Dynamic-query lane
**Why sixth**
- This lane is important but easy to overclaim.
- It should be piloted only after the stronger checked-query and schema lanes are already explicit.

**Primary artifacts**
- `db-query-catalog/v0`
- `db-compat-report/v0`
- vectors for builder/raw/template origins, runtime-test coverage, manual-review coverage, and backend-specific query behavior

**Primary consumers**
- application teams with reporting/search/admin surfaces
- service reviewers
- policy/support consumers

### 7) Backend-authority and portability lane
**Why seventh**
- This lane becomes credible only after the project can already record what was actually validated.
- It is where “supports Postgres + SQLite + MySQL” claims often need the most honesty.

**Primary artifacts**
- `db-intent/v0`
- `db-schema-snapshot/v0`
- `db-query-catalog/v0`
- `db-compat-report/v0`
- vectors for backend/version matrix coverage, extension or collation assumptions, runtime/driver choices, and cross-backend unknowns

**Primary consumers**
- support-envelope consumers
- release and docs consumers
- adoption-decision consumers

## Graduation criteria
A database-contract pilot should graduate only when it has:
1. an explicit pilot brief;
2. a lane profile naming the database lane under review;
3. a bounded query budget with named vectors;
4. at least one consumer-handoff artifact;
5. concrete reports or attached evidence;
6. a scorecard showing the pilot remained lane-specific and did not claim universal database truth.

## Worthy first pilot bundles
1. **SQLx checked-query + offline/docs.rs bundle**
   - proves checked/offline distinction and metadata freshness.
2. **Diesel schema-as-code + migration-source bundle**
   - proves generated-schema and migration-source posture without pretending live DB truth is automatic.
3. **SeaORM schema-first versus entity-first bundle**
   - proves source-of-truth plurality explicitly.
4. **refinery embedded-versus-cli migration bundle**
   - proves standalone migration execution and embedded shipping stay separate.
5. **testcontainers / `sqlx::test` validation-environment bundle**
   - proves environment receipts can be portable and reviewable.
