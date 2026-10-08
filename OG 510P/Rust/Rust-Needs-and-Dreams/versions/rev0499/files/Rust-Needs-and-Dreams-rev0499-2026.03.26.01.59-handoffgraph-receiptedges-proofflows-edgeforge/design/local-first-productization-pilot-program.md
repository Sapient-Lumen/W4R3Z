# Design: Local-First Productization Pilot Program (Offline Durable Truth → Multi-Replica Sync Truth → Relay/Auth Activation → Recovery/Migration Truth → Support/Release Consumers)

## Goal
Turn the **Local-First Productization Stack** into a ranked execution program so the archive can answer a practical question: what is the first boring, portable, ecosystem-shaping contribution that would materially improve how Rust local-first products are built, supported, and shipped?

The pilot program should not chase a universal local-first platform.
It should sequence the contribution so each lane proves something concrete before the next lane widens scope.

## Why a pilot program is necessary
Local-first ideas are unusually easy to romanticize.
Rust already has serious ingredients — CRDT engines, repo/storage/network adapters, typed mapping layers, browser/mobile/desktop clients, relay services, and export/backup/mirror lanes — but those ingredients live at different authority layers and fail in different ways.
A credible plan therefore needs to decide:
- when offline durability and restart truth are already enough,
- when live sync and presence/session posture must be attached,
- when relay/auth/runtime activation becomes part of the contract,
- when recovery/export/migration evidence is required,
- and which support/release consumers justify graduation.

## Principles
1. **Start from durable user-state truth, not CRDT ideology**
   - a pack that proves restart/offline/data-ownership posture is worth more than a framework pitch.
2. **Keep document truth, relay truth, and auth truth separate**
   - they travel together in products, but they are not the same source of truth.
3. **Session/presence is not the same as document history**
   - awareness/cursor/session lanes should stay explicit instead of getting smuggled into “sync works”.
4. **Recovery and migration are part of ownership**
   - backup/export/import/version-change posture should graduate before big support claims do.
5. **Cross-runtime claims need evidence**
   - browser/mobile/desktop/server or Rust/JS/Swift compatibility should be reviewable, not only implied by a library README.
6. **Consumers import; they do not reinterpret**
   - release, support, atlas, docs, and service/client consumers should import artifacts instead of becoming the hidden source of truth.

## Common artifacts this program should drive
- `localfirst-lane-brief/v0` — declare which pilot lane is being exercised, scope, product roles, and non-goals.
- `replica-activation-brief/v0` — bounded summary of storage, room, peer, relay, auth, and runtime settings actually activated.
- `presence-boundary-note/v0` — explicit summary of what session/presence state exists outside document history.
- `recovery-migration-brief/v0` — export/import/backup/restore/version-transition posture for the pilot.
- `localfirst-consumer-handoff/v0` — what release/support/docs/atlas consumers may conclude from the pilot and what remains out of scope.
- `localfirst-readiness-scorecard/v0` — not a fake maturity score; a lane-by-lane checklist showing which truths exist and which remain absent.
- `localfirst-product-pack/v0` — attachable summary pack importing the lane artifacts used in a specific pilot.

## Ranked pilot lanes

### 1) Single-device durable lane
**Why first:** it proves the most universal local-first claim with the least ecosystem coercion.

**Concrete scope**
- document/collection identities,
- local storage adapter and restart behavior,
- offline-only operation,
- save/load/restore posture,
- typed mapping or schema attachment when relevant,
- docs/support examples that state single-device posture honestly.

**Graduation bar**
- the pack can explain what local state exists, where it lives, how it survives restart, and what parts remain transient.

### 2) Multi-replica sync lane
**Why second:** once local durability is real, the next hidden source of pain is convergence and session truth.

**Concrete scope**
- peer/runtime combinations exercised,
- offline edit / reconnect scenarios,
- concurrent edit / merge scenarios,
- awareness or presence posture where relevant,
- snapshot/update compatibility,
- convergence and divergence findings.

**Graduation bar**
- the pack can explain which replica combinations converged, which session/presence state sat outside document history, and what was only illustrative.

### 3) Relay / auth / runtime-activation lane
**Why third:** this is where local-first product claims often become hand-wavy unless configuration and access posture are explicit.

**Concrete scope**
- relay or service boundary attachments,
- room/document discovery and naming rules,
- peer or principal identity posture,
- auth/session/key/cookie/token activation where relevant,
- per-environment runtime settings,
- failure modes for missing relay/auth state.

**Graduation bar**
- a reviewer can tell which collaboration lanes were peer-to-peer versus relayed, under which identity posture they ran, and what runtime setup was required.

### 4) Recovery / export / migration lane
**Why fourth:** live sync success is not enough for real ownership or long-term support.

**Concrete scope**
- export/import artifacts,
- backup/restore behavior,
- format/schema/version evolution,
- compaction/retention and deletion posture,
- optional database/mirror attachments,
- migration reports across versions or runtimes.

**Graduation bar**
- the pack can explain how users keep or move their data, what changed across upgrades, and what remained best-effort or partial.

### 5) Support / release / customer-handoff lane
**Why fifth:** this is where the stack proves it matters beyond demos and internal experimentation.

**Concrete scope**
- supported client/runtime/storage/relay combinations,
- checked docs/examples,
- release attachments importing replica/runtime/recovery evidence,
- support/playbook handoff,
- atlas or comparison views for serious Rust local-first lanes.

**Graduation bar**
- a release or support consumer can answer what collaboration/offline story is actually supported and what evidence accompanied it.

## What to defer
- a universal relay service;
- one mega local-first framework that owns client, relay, storage, auth, and export at once;
- policy-first hard gates before the evidence lanes exist;
- benchmark or “CRDT winner” theater without product-boundary artifacts;
- vague “works offline and multiplayer” claims that skip recovery and support truth.

## Immediate archive consequences
- Treat **Replica Surface Kit** as the anchor of a broader local-first-productization seam rather than an isolated CRDT/report idea.
- Treat **Client App Surface + Event/Service Surface + Runtime Settings + Identity Surface** as the product-boundary half of the story instead of letting replica docs silently absorb them.
- Treat **Support Envelope + DocProof** as downstream import lanes that should consume lower-layer local-first evidence instead of retelling it.
- Add a specific amnesia resistor so later revisions cannot collapse document/sync/history/storage truth, client/relay truth, runtime/identity activation, recovery/migration truth, and support/release conclusions into one note.

## Read this together with
- `design/local-first-productization-stack.md`
- `design/replica-surface-kit.md`
- `design/client-app-surface-kit.md`
- `design/service-surface-kit.md`
- `design/event-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/identity-surface-kit.md`
- `design/support-envelope-kit.md`
- `design/docproof-kit.md`

## Proposal-layer companion
The explicit proposal-layer candidate is now [`proposals/epic-local-first-productization-stack.md`](../proposals/epic-local-first-productization-stack.md): a thin `cargo local-product` / `local-first-product-pack/v0` layer above Replica Surface + Client App Surface + Event/Service Surface + Runtime Settings + Identity Surface + Support Envelope. The pilot program stays intentionally narrower than a universal framework claim: prove durable replica truth first, then multi-replica/presence truth, then relay/auth/runtime activation, then recovery/export, then support/release/atlas handoffs.
