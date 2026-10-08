---
id: P-0076
title: Local-first Sync Kit — repo contracts, presence/history receipts, transport/membership epochs, and redacted sync bundles
status: idea
domains: [local-first, crdt, sync, storage, encryption, devtools]
last_reviewed: 2026-03-21
evidence:
  - https://www.inkandswitch.com/essay/local-first/
  - https://automerge.org/docs/hello/
  - https://automerge.org/docs/reference/repositories/dochandles/
  - https://docs.rs/automerge/latest/automerge/
  - https://loro.dev/blog/v1.0
  - https://loro.dev/docs/tutorial/loro_doc
  - https://loro.dev/docs/api/js
  - https://docs.rs/yrs/latest/yrs/
  - https://docs.rs/yrs/latest/yrs/sync/protocol/trait.Protocol.html
needs:
  - Rust now has credible substrate for CRDT state, sync protocols, peer replication, and end-to-end encrypted group membership, but teams still lack a boring default kit that composes those pieces into a supportable product workflow.
  - The missing crate is not “yet another CRDT”; it is a receiver-facing coordination kit above engines, transports, storage, and membership/key-rotation lanes.
risks:
  - Scope can sprawl into “replace your whole app architecture”; the MVP must stay at the repo contract, transport/membership receipts, and support-bundle layer.
  - It is easy to confuse convergence with authorization, privacy, or revocation semantics; the crate must keep those layers explicit.
  - Choosing a golden path too early can lock the crate to one engine; choosing none makes it too abstract to adopt.
---

# P-0076 — Local-first Sync Kit

**Codename:** `localsync`

**Canonical artifact:** `*.syncbundle.zip`, ideally as a `syncbundle@1` profile on top of **P-0256 Evidence Bundle Core Kit**.

**Primary surface:** a crate workspace plus `cargo localsync`.

## Problem

Local-first is no longer just a design essay.
It is now a realistic product direction with real Rust substrate:

- Ink & Switch’s local-first work still defines the product ideals: offline-first operation, collaboration, user control, longevity, and privacy.
- `automerge` already provides local-first documents, an explicit sync protocol that assumes a reliable in-order stream, and an efficient binary storage format.
- Automerge Repo shows the missing *repo / storage / network adapter* shape above a CRDT engine.
- `loro` now presents a high-performance CRDT framework for local-first apps with a stable data format, version control features, and explicit ambition around local-first developer tooling.
- `yrs` gives Rust a high-performance Yjs-compatible CRDT lane.
- `iroh` now provides modular networking substrate for direct connections, relay fallback, protocol routing, and document-collaboration examples.
- MLS is standardized in RFC 9420, and OpenMLS gives Rust a serious group-key-management building block.

That combination makes the actual gap sharper.
The missing crate is not a new merge algorithm.
It is a **boring coordination kit** that helps ordinary Rust teams move from:

1. a single-device prototype,
2. to multi-device sync,
3. to encrypted shared collaboration,
4. to supportable incident diagnosis,

without inventing a private repo grammar, a private transport receipt format, or a private explanation bundle every time.

## Main judgment

A worthy crate contribution here would give other people one honest answer to:

> what state existed on each replica, what sync or membership epoch was attempted, what transport path or snapshot strategy was used, and why did the replicas converge, stall, or diverge?

That answer should stay useful even when the underlying engine changes.

## What the crate should provide other people

### 1. A stable repo contract above CRDT engines
The first missing deliverable is a small repo-level contract above document engines.
Not a fake “universal CRDT” abstraction, but a stable surface for the things product teams actually need:

- document identity,
- replica identity,
- snapshot/export/import,
- incremental update exchange,
- compaction / GC checkpoints,
- migration/version markers,
- and support-bundle capture.

The key point is that this contract should survive whether a team begins on `automerge`, `loro`, or `yrs`.

### 2. A lane model, not a ball of mud
The crate should make six lanes explicit:

1. **engine lane** — CRDT document and update semantics,
2. **store lane** — durable local persistence and compaction receipts,
3. **transport lane** — ordered message exchange and reconnect behavior,
4. **membership lane** — device identity, encrypted-group epochs, revocation, and key rotation,
5. **presence lane** — ephemeral awareness/cursor/session metadata and its delivery/persistence limits,
6. **history lane** — version retention, branch/time-travel support, and comparability after compaction/export.

Most current local-first implementations blur those together.
A good crate should instead let another person inspect which lane failed.

### 3. One concrete golden path for 0.1
The MVP should not pretend to be backend-neutral in practice.
It should ship one golden path that a team can actually adopt.

The least speculative first profile now looks like:

- **engine:** Automerge-shaped document/update semantics,
- **store:** SQLite-backed durable receipts and snapshots,
- **transport:** reliable ordered frame transport with one default adapter,
- **support artifact:** `syncbundle@1` export/diff flow.

Why this direction: Rust Automerge already exposes the strongest “document + sync protocol + binary format” substrate, and Automerge Repo demonstrates the repo/storage/network adapter shape that ordinary app teams need.

### 4. A second profile for encrypted collaboration
The 0.2 collaboration lane should add a more explicit encrypted-group story instead of hand-waving “E2EE later”.

That profile should provide:

- device identities,
- membership changes,
- key epochs,
- removal/revocation receipts,
- self-update / key-rotation receipts,
- and an explicit statement of what metadata remains visible.

The important planning move here is to stay **MLS-shaped** rather than inventing a private group-key protocol.
RFC 9420 and OpenMLS make it reasonable to plan around membership epochs and forward-secrecy / post-compromise-security receipts, even if the first release keeps them optional.

### 5. Redacted sync incident bundles
When local-first sync goes wrong, logs are not enough.
Teams need a bundle that can travel between developers, support, and security reviewers.

That bundle should capture:

- manifest and profile identity,
- replica heads / frontiers,
- snapshot lineage,
- transport session receipts,
- membership/key-epoch history,
- compaction checkpoints,
- migration/version markers,
- diagnosis report,
- and optional redacted update samples.

That is the concrete artifact the crate should hand to other people.

### 6. Honest presence / awareness receipts
Some collaboration state is session-level rather than durable.
A good crate should therefore emit one explicit `presence-surface.receipt.json` saying whether live collaboration state is:

- best-effort or reliable within a session,
- persisted or not persisted,
- strong enough to identify a device/member/user or not,
- and safe to export in redacted support bundles or only as summary metadata.

This matters because Automerge Repo already has ephemeral messages that are not persisted and are not useful user identifiers, while Yrs explicitly models sync behavior in the context of an `Awareness` structure.

### 7. Honest history-retention and branch receipts
A worthy crate should also publish one `history-retention.receipt.json` saying whether the selected engine/profile still supports:

- full history,
- checkout/time-travel or branch workflows,
- direct historical comparison,
- or only current-state sync after compaction/export.

This matters because Automerge markets branch/compare semantics, while Loro explicitly supports version control plus export modes such as shallow snapshots that keep current state while narrowing older-history reach.

### 6. A conformance and failure-lab surface
The crate should also ship a tiny but serious TCK/failure lab for:

- same-user multi-device sync,
- offline fork then reconnect,
- stale peer after compaction,
- revoked device after key rotation,
- schema/migration mismatch,
- and redaction-safe incident export.

The point is not just correctness.
It is to make incidents reproducible across engines and transports.

### 7. Honest bootstrap and transport truth
The crate should export transport/bootstrap facts explicitly instead of hiding them behind a generic "connected peer" story.

For the first Automerge-shaped profile, that means the kit should record:

- that the document lane expected a **reliable in-order stream**,
- which protocol/version was spoken,
- whether the session was **direct** or **relay fallback**,
- whether the relay class was **public**, **dedicated**, or **self-hosted**,
- which bootstrap method was used (`ticket`, `endpoint_id`, `directory`, `manual`),
- and whether those facts make two sessions only partially comparable.

This is where today’s iroh substrate becomes especially useful.
It already makes ALPN/protocol routing, relay fallback, and bootstrap handles explicit.
A worthy crate should preserve that truth in its receipts instead of flattening it away.

### 8. Redaction rules for bootstrap handles
Bootstrap convenience is not the same thing as durable identity.
Current iroh tickets are useful because they package addressing information and optional application data, but they can also expose IP addresses, be reused, and go stale.

So a good local-first crate should:

- allow tickets/invite handles for bootstrapping,
- avoid treating them as durable membership truth,
- redact them by default from support bundles,
- and preserve a smaller summary like `bootstrap_method = "ticket"` plus a redaction note.

That is the difference between a supportable product kit and an accidental capability leak.

## Persona / who it’s for

- product teams building collaborative or offline-first apps
- maintainers who need reproducible sync incident reports
- platform teams that want one supportable sync stack instead of bespoke app logic
- security reviewers who need explicit membership / key-epoch semantics
- library authors who want adapters into a shared bundle and conformance surface

## Users & user stories

- **App team:** “We have a single-device app today; help us add same-user multi-device sync without inventing our own repo protocol.”
- **Maintainer:** “A user says two replicas stopped converging; give me one redacted bundle that says whether the issue was missing updates, membership drift, compaction, migration, or transport failure.”
- **Security reviewer:** “Show me exactly when a device was removed, which key epoch became active, and what metadata remains visible in shared artifacts.”
- **Platform team:** “Start with one boring default stack and swap the engine or transport only when we have a real reason.”

## Prior art scan (and why it’s insufficient)

### CRDT engines already exist
`automerge`, `loro`, and `yrs` are meaningful substrate, not evidence that the gap is closed.
They solve document convergence.
They do **not** by themselves freeze the repo contract, incident bundle, or cross-lane diagnosis artifact that app teams need.  

### Repo/plumbing examples exist, but not a Rust-wide product kit
Automerge Repo already demonstrates pluggable networking and storage above Automerge documents.
That is strong evidence for the shape of the missing layer.
But it is still engine-specific and does not give the wider Rust ecosystem a compact support-bundle standard or an explicit membership/key-epoch lane.  

### P2P/sync substrate exists
`iroh-sync` shows that Rust now has serious peer synchronization substrate with persistent replicas.
That reduces feasibility risk for transport and replication receipts.
But it is not itself the missing user-facing local-first kit above CRDT documents and collaboration semantics.  

### E2EE group substrate exists
MLS is standardized, and OpenMLS is a real Rust implementation.
That makes ad hoc collaboration-key stories less defensible.
What remains missing is the boring app-facing layer that records membership epochs, removals, and update receipts in a shareable support artifact.  

## Design goals

1. **Golden-path first** — one lovable profile before adapter sprawl.
2. **Lane-explicit** — engine, store, transport, and membership semantics stay separate.
3. **Supportability-first** — failures must export as small redacted bundles.
4. **Security-honest** — convergence is not authorization; key epochs and metadata leakage must be explicit.
5. **Migration-aware** — compaction and schema drift are first-class, not “later”.
6. **Adapter-friendly after 0.1** — alternative engines/transports can land after the base contract is stable.

## Proposed architecture

```text
localsync-core/         # repo contract, ids, causal frontier, migration markers
localsync-automerge/    # default 0.1 engine profile
localsync-store-sqlite/ # snapshots, update receipts, compaction receipts
localsync-transport/    # reliable ordered frame transport traits
localsync-iroh/         # likely first nontrivial transport adapter
localsync-membership/   # device ids, membership epochs, revocation receipts
localsync-openmls/      # optional 0.2 MLS-shaped membership adapter
localsync-bundle/       # syncbundle export/import/diff/redaction
localsync-tck/          # scenario corpus and adapter tests
cargo-localsync/        # doctor, capture, diff, explain, redact
```

## Core artifacts

### `repo-manifest.toml`
A compact identity and topology record:

- app / workspace identity,
- chosen engine profile,
- schema/migration version,
- store profile,
- transport profile,
- membership profile,
- and declared redaction mode.

### `sync-state.report.json`
A machine-readable snapshot of:

- replica IDs,
- document heads/frontiers,
- snapshot lineage,
- update counts,
- compaction checkpoints,
- and declared comparability caveats.

### `transport-session.receipt.json`
A receipt for one sync attempt:

- peers,
- transport lane,
- protocol/version identity,
- bootstrap method,
- connection / relay mode,
- relay class,
- bytes and message counts,
- reconnect / retry status,
- ordering guarantees,
- and failure class if the session did not complete.

### `membership-ledger.json`
A diffable history of:

- devices and members,
- role or scope tags,
- membership adds/removes,
- key epochs,
- self-updates / rotations,
- revocation reason,
- and visibility / redaction notes.

### `presence-surface.receipt.json`
A machine-readable statement of whether session-level collaboration state is best-effort or reliable within a session, whether it is persisted, what kind of identity it carries, and how it is redacted for support export.

### `history-retention.receipt.json`
A machine-readable statement of whether the current profile retains full history, supports checkout/branch flows, still permits direct historical comparison, and what changed after compaction or shallow-snapshot export.

### `divergence-triage.report.json`
A conservative diagnosis layer with classes like:

- `missing_updates`,
- `membership_epoch_mismatch`,
- `revoked_device`,
- `compaction_gap`,
- `migration_mismatch`,
- `transport_not_comparable`,
- `redaction_insufficient`,
- `manual_review_required`.

### `*.syncbundle.zip`
A portable bundle carrying those artifacts together.

## Fixture-first MVP

The 0.1 release should not promise “all local-first app concerns solved”.
It should promise one honest, supportable workflow:

1. initialize a repo with one default engine profile,
2. persist snapshots and update receipts locally,
3. synchronize over one default transport lane,
4. emit a redacted sync bundle when something goes wrong,
5. classify the failure conservatively,
6. and diff two sync bundles without pretending incomparable cases are comparable.

## Suggested first policy profiles

The fixture pack under `fixtures/localfirst-sync-kit/` should be treated as the first concrete receiver surface for these profiles.


### `single_user_multi_device@1`
- no shared membership graph required,
- one owner identity with several replica/device IDs,
- optional at-rest encryption,
- strongest focus on offline fork / reconnect / compaction.

### `shared_group_sync@1`
- explicit membership ledger,
- membership changes and key epochs required,
- revocation receipts required,
- stronger redaction rules,
- and diagnosis classes that can name stale or removed devices.

## MVP surface

### 0.1
- `localsync-automerge`
- SQLite-backed snapshot/update receipts
- one reliable ordered transport adapter
- `cargo localsync doctor`
- `cargo localsync bundle`
- `cargo localsync diff`

### 0.2
- membership ledger and key-epoch receipts
- OpenMLS-shaped collaboration adapter
- compaction and stale-peer diagnosis
- first TCK scenarios

### 0.3
- adapter stabilization for Loro/Yrs lanes
- richer redaction policy
- replayable incident explanation and comparability output

## Adoption plan

1. **Offline-first only** — adopt the repo/store contract locally.
2. **Same-user multi-device** — turn on the default transport and bundle flow.
3. **Shared collaboration** — add membership ledger and encrypted-group profile.
4. **Scale and specialize** — swap engine or transport only when the stable contract stops fitting.

## Path to boring stability

- Freeze the support-bundle vocabulary before multiplying adapters.
- Keep transport guarantees explicit; do not assume every adapter is “equivalent”.
- Keep membership and revocation receipts explicit; do not let E2EE become magical hand-waving.
- Treat compaction, stale peers, and migration drift as first-class fixtures.
- Make `single_user_multi_device@1` excellent before chasing giant collaborative workspaces.

## Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 5/5
- **Total: 24/30**

## Minimum lovable MVP

A crate workspace that lets a Rust app persist CRDT-backed local state, synchronize replicas over one boring default transport, and export one redacted sync bundle that another person can actually use to diagnose divergence.

## De-risk plan

1. Start with one engine profile and one transport adapter, not a marketplace.
2. Freeze `syncbundle@1` early.
3. Pilot on one note/document app and one structured-tree app.
4. Treat membership and key epochs as separate receipts, not implicit transport metadata.
5. Delay “smart conflict UX” until the receiver-facing support artifact is good.

## Non-goals

- Not a full app framework.
- Not a claim that CRDT convergence solves authorization or privacy.
- Not a hosted collaboration backend.
- Not a fake universal CRDT abstraction that erases engine semantics.
- Not a replacement for dedicated messaging or identity systems.

## Open questions

- Should the first stable engine profile be Automerge-only, or should Loro also land before 1.0 if adapter shape proves small enough?
- Should the first production transport profile be iroh-first, or should a simpler client/server ordered-stream adapter land before that for easier adoption?
- Which bootstrap flows deserve first-class ergonomic support (`endpoint_id`, QR/ticket, or coordination-server invite), and which must remain adapters?
- Which metadata must remain visible in bundles to keep diagnosis useful without compromising users?
- How should migration and compaction policies declare that two sync bundles are only partially comparable?

## Sources

- https://www.inkandswitch.com/essay/local-first/
- https://automerge.org/docs/hello/
- https://automerge.org/automerge/automerge/sync/index.html
- https://automerge.org/blog/automerge-repo-2/
- https://loro.dev/docs
- https://loro.dev/blog/v1.0
- https://docs.rs/yrs/latest/yrs/
- https://docs.iroh.computer/what-is-iroh
- https://docs.iroh.computer/concepts/protocols
- https://docs.iroh.computer/protocols/automerge
- https://docs.iroh.computer/concepts/relays
- https://docs.iroh.computer/concepts/tickets
- https://datatracker.ietf.org/doc/rfc9420/
- https://github.com/openmls/openmls
