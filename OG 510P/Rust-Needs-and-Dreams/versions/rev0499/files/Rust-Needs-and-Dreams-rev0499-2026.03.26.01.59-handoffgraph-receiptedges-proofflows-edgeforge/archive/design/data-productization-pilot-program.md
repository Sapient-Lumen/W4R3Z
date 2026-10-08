# Design: Data Productization Pilot Program (Query/Offline Truth → Migration/Test Environments → Runtime Activation → Consumer Imports)

## Goal
Turn the **Data Productization Stack** into a ranked execution program so the archive can answer a practical question: what is the first boring, portable, ecosystem-shaping contribution that would materially improve Rust’s stateful-data story?

The pilot program should not chase a universal “database platform.” It should sequence the contribution so each lane proves something concrete before the next lane expands scope.

## Why a pilot program is necessary
Data work is one of the easiest places for good ideas to dissolve into giant abstractions. Rust already has strong ingredients, but they come from different source-of-truth families and different failure modes. A credible plan therefore needs to decide:
- when query evidence is already enough,
- when schema or migration evidence must be attached,
- when runtime settings become part of the contract,
- when public schemas should be linked,
- and which downstream consumers justify graduation.

## Principles
1. **Start where the evidence gap is painful and common**
   - docs/CI/offline query validation and backend assumptions are earlier wins than a grand unified schema platform.
2. **Respect multiple source-of-truth families**
   - SQL files, generated schema code, ORM entities, migration dirs, live introspection, and test-environment descriptors are all real.
3. **Keep internal DB truth and external schema truth separate**
   - the database lane and the API/schema lane should travel together without becoming one artifact.
4. **Settings are part of the data story**
   - backend/profile/secret activation changes what was actually validated or shipped.
5. **Partial truth is still useful**
   - a pack that only knows checked queries and backend version can still help docs, CI, and support.
6. **Consumers import; they do not redefine**
   - release, incident, policy, service, and client tooling should import the data stack rather than reinterpret it from scratch.


## Proposal-layer anchor
This pilot program now has an explicit proposal-layer companion: [`proposals/epic-data-productization-stack.md`](../proposals/epic-data-productization-stack.md). The pilot should keep proving the boundary lane-by-lane rather than widening into a universal “data platform” abstraction.

## Common artifacts this program should drive
- `data-lane-brief/v0` — declare which lane is being exercised, scope, engines, and non-goals.
- `data-escalation-policy/v0` — rules for when a subject must move from query-only evidence to schema/migration/runtime evidence.
- `data-correlation-budget/v0` — bounded rules for correlating query/schema/migration/runtime/support facts without pretending perfect universal inference.
- `data-readiness-scorecard/v0` — not a fake maturity number; a lane-by-lane checklist showing which truths exist and which remain absent.
- `data-pilot-pack/v0` — attachable summary pack importing the lane artifacts used in a specific pilot.

## Ranked pilot lanes

### 1) Query / offline / docs.rs lane
**Why first:** it hits common daily pain with the least ecosystem coercion.

**Concrete scope**
- checked-query metadata,
- offline preparation state,
- backend/version declaration,
- docs.rs-safe posture,
- dynamic-SQL caveat imports,
- CI/local parity notes.

**Graduation bar**
- the pack can explain what was live-validated, what was offline-validated, what backend/version assumptions held, and why docs builds do or do not work.

**What success looks like**
- SQLx-centric first proof, but with interfaces honest enough that later Diesel/SeaORM/refinery/testcontainers imports do not feel bolted on.

### 2) Multi-source migration + test-environment lane
**Why second:** stateful deployments need more than query metadata.

**Concrete scope**
- migration execution reports,
- schema snapshots/fingerprints,
- test DB image/init/reset posture,
- advisory/manual-step attachments,
- comparison notes across local/CI/staging.

**Graduation bar**
- the pack can show which schema/migration/test facts were observed and which were only declared.

### 3) Runtime settings + secret posture lane
**Why third:** once deployments and support enter the story, activation truth matters.

**Concrete scope**
- chosen backend/profile,
- secret source and activation rules,
- replica/region posture,
- environment/profile correlation with validation artifacts,
- explicit unknown/inferred markers.

**Graduation bar**
- a release or support consumer can tell which data posture was actually activated without scraping shell scripts or README prose.

### 4) Public schema + service/client consumer lane
**Why fourth:** after the internal data plane is honest, attach external surfaces without flattening them.

**Concrete scope**
- field/endpoint/message ↔ DB evidence links,
- service/client docs attachments,
- migration notes that explain external compatibility risk,
- compatibility reason imports from Schema Contract Kit.

**Graduation bar**
- service and client consumers can import data facts while preserving the line between relational truth and public API/schema truth.

### 5) Release / support / incident consumer lane
**Why fifth:** this is where the stack proves it can matter beyond development-time validation.

**Concrete scope**
- release attachments,
- support-envelope claims tied to real data artifacts,
- incident packs that import migration/query/schema/runtime evidence,
- archaeology diffs for “what changed between shipped states.”

**Graduation bar**
- the stack can answer boring real-world questions without bespoke operator memory.

## What to defer
- a mega-ORM or universal query DSL,
- a hosted migration or schema-control plane,
- a one-true relational meta-schema,
- policy-first hard gates before the evidence lanes exist,
- “AI database copilots” that claim universal understanding without stable artifacts.

## Immediate archive consequences
- Promote **Database Contract Kit** from Tier 1/2 to a clearer frontier-adjacent role.
- Treat **Schema Contract Kit** as an attached but distinct consumer/peer.
- Treat the broader **Migration Truth Stack** as the choreography layer rather than the single owner of all data change facts.
- Add a specific amnesia resistor so later revisions cannot collapse query evidence, schema truth, migration truth, runtime activation, and support claims into one note.

## Read this together with
- `design/data-productization-stack.md`
- `design/database-contract-kit.md`
- `design/schema-contract-kit.md`
- `design/migration-truth-stack.md`
- `design/runtime-settings-kit.md`
- `design/docproof-kit.md`
