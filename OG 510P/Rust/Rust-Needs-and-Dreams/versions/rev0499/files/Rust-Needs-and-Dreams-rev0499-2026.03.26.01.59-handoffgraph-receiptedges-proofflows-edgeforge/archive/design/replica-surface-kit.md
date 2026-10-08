# Design: Replica Surface Kit (`cargo replicacheck`, `replica-pack/v0`)

## Goal
Define a portable contract for declaring, validating, diffing, and reviewing a Rust application’s supported **local-first / replicated-state surface**: collaborative documents or collections, sync/update/snapshot formats, storage and transport assumptions, merge/history behavior, cross-runtime compatibility posture, and evidence that the declared convergence story still matches reality.

This should **not** replace `automerge`, `yrs`, Loro, their repo/storage adapters, or future CRDT/document engines.
It should make them compose better and make support claims reviewable.

## References (signals)
- `automerge` explicitly positions itself as a library of data structures for collaborative local-first applications, with a sync protocol and efficient binary storage format.
  https://automerge.org/automerge/automerge/index.html
  https://docs.rs/automerge/latest/automerge/
- Automerge’s “Welcome” docs frame the product around offline local copies, later synchronization, automatic merge, history/branching, and transport-agnostic operation.
  https://automerge.org/docs/hello/
- Automerge’s repository docs explicitly say the core JSON-like CRDT + sync protocol still leave a lot of application plumbing, and that repo-based applications must choose storage and network adapters.
  https://automerge.org/docs/reference/repositories/
- Yrs is a high-performance Rust port of Yjs; its docs already expose update encoding, undo/redo, past revisions, awareness/y-sync protocol, and document-querying concerns.
  https://docs.rs/yrs/latest/yrs/
  https://docs.rs/yrs/latest/yrs/updates/index.html
- `yrs-lmdb` and `yrs-kvstore` prove that durable document stores and backend-specific persistence layers are already a practical part of Rust collaboration stacks.
  https://docs.rs/yrs-lmdb/latest/yrs_lmdb/
  https://docs.rs/yrs-kvstore/latest/yrs_kvstore/
- Loro explicitly frames syncing/offline collaboration as hard, presents itself as local-first state management with version control, import/export, event systems, and time travel, and Loro 1.0 now claims a stable data format and multi-language use from Rust, JS/WASM, and Swift.
  https://loro.dev/docs
  https://loro.dev/docs/tutorial/loro_doc
  https://loro.dev/blog/v1.0
- Loro’s docs also explicitly say some applications need stronger consistency than CRDTs provide, which is a strong signal that support posture and non-goals should be first-class artifacts instead of marketing blur.
  https://loro.dev/docs

## Core components

### 1) `replica-surface/v0`
A design-time declaration of the supported replicated-state boundary for a binary/service/workspace/app.

Required ideas:
- system/application identity
- replicated surface ids in scope
- supported replica roles:
  - local device replica
  - browser/client replica
  - desktop/mobile replica
  - relay/server replica
  - importer/exporter bridge
  - archival / backup replica
- support classes:
  - official
  - best-effort
  - experimental
  - deprecated
  - internal
- linked attachments:
  - client-app surfaces
  - runtime settings refs
  - event surfaces
  - identity/access refs
  - storage/runtime docs
  - raw CRDT engine / protocol / format artifacts

Design rule: keep declared replicated-surface support truth separate from raw CRDT implementation details. “We use engine X” is not the same claim as “we officially support collaborative document family Y with offline/history behavior Z.”

### 2) `replica-doc-catalog/v0`
Stable identities for replicated documents, collections, or shared-state families the application officially supports.

Each entry should support:
- stable replica-doc id
- human purpose summary
- kind:
  - JSON-like document
  - rich text document
  - list/map/tree collection
  - whiteboard / canvas state
  - structured app state mirror
  - presence/awareness side document
  - custom opaque payload family
- local-only vs sync-visible status
- linked schema/shape refs when relevant
- partitioning / sharding / workspace notes
- sensitivity / redaction / encryption notes
- support level
- owning team / review owner

Design rule: keep document/collection identity separate from the engine’s raw container ids or internal object paths. Reviewers need stable product-facing identities, not just CRDT internals.

### 3) `sync-capability-profile/v0`
The sync/update/runtime features a replicated surface depends on.

Each profile should capture:
- stable sync-profile id
- engine/runtime identifiers and versions when known
- supported synchronization classes:
  - peer-to-peer
  - client/server relay
  - LAN/local process
  - manual file/export-import transfer
  - store-and-forward / async replication
- required transport assumptions:
  - reliable in-order stream
  - unordered messaging tolerated
  - offline-first with later catch-up
  - persistent relay required
- update/snapshot capabilities:
  - incremental updates
  - full snapshots
  - compaction / bundle export
  - partial sync / subdocument sync
- awareness/presence support when relevant
- peer-id / actor-id assumptions
- cross-runtime compatibility claims
- unsupported or unchecked lanes

Design rule: do not flatten all engines into one fake sync matrix. Preserve raw engine/docs truth as attachments and model only the support claims your application depends on.

### 4) `merge-history-profile/v0`
Conflict-resolution, history, and long-lived-state posture for a replicated surface.

Each profile should support:
- stable merge-history-profile id
- linked replica-doc ids
- conflict posture summary
- branch/history capabilities:
  - no exposed history
  - undo/redo only
  - version checkpoints
  - branch/merge support
  - time travel / checkout support
- retention / GC / compaction notes
- migration/import/export notes
- schema-evolution posture
- deletion/redaction semantics
- strong-consistency exclusions / non-goals

Design rule: keep history/merge posture explicit. “Offline collaboration supported” is not enough if branching, compaction, or migration can make old data unreadable or merge outcomes surprising.

### 5) `replica-storage-profile/v0`
How replicated state is durably stored and recovered.

Each profile should support:
- stable storage-profile id
- storage lane:
  - browser/local storage
  - file system
  - embedded KV store
  - LMDB / RocksDB / database
  - cloud object / blob store
  - custom encrypted store
- durability expectations
- snapshot/update retention policy
- backup/export format refs
- encryption/redaction posture
- restore/recovery notes
- linked doc/sync profiles

Design rule: keep persistence separate from sync and separate from logical document support. A document might sync fine and still have weak durability or poor recovery guarantees.

### 6) `replica-check-plan/v0`
A plan for validating that the declared replicated-state surface still behaves as claimed.

A plan should capture:
- selected document/surface ids
- peer/runtime combinations exercised
- offline edit / reconnect scenarios
- concurrent edit / merge scenarios
- snapshot save/load and update import/export checks
- branch/history/undo/redo checks where supported
- persistence restart / crash recovery checks
- cross-language/runtime compatibility checks when relevant
- illustrative-only or unsupported scenarios

Design rule: distinguish illustrative collaboration examples from actual checked convergence scenarios.

### 7) `replica-check-report/v0`
Portable results from running replicated-state checks.

A report should capture:
- artifact versions and environment
- engines/runtimes exercised
- peer combinations exercised
- document/surface ids exercised
- divergence / convergence outcomes
- format compatibility results
- recovery/reload outcomes
- branch/history/undo findings when relevant
- raw attachment refs (logs, update files, snapshots, traces)

Design rule: the report should be honest about scope. “Two browsers converged in one smoke test” is not proof that desktop/mobile/server and historical snapshots are all compatible.

### 8) `replica-diff-report/v0` (optional)
A compatibility-oriented comparison between two declared replicated-state surfaces.

Should support:
- added/removed document ids
- changed sync/update/snapshot support
- changed history/retention posture
- changed persistence/recovery posture
- changed support levels
- possible compatibility hazards

### 9) `replica-pack/v0`
A bundle format for attaching the relevant declarations, reports, raw docs, sample updates/snapshots, and generated references to CI, releases, app handoff, or bug reports.

## How it should compose
- **Schema Contract Kit:** attach logical schemas or JSON-like shape contracts where appropriate, but do not flatten all replicated state into one canonical schema language.
- **Client App Surface Kit:** link platform capabilities, package ids, deeplinks, notifications, and lifecycle checks without pretending they own the collaborative-state boundary.
- **Event Surface Kit / Service Surface Kit:** link relay/server/event APIs used for sync without confusing them with the replicated document contract itself.
- **Runtime Settings Kit:** link sync endpoints, storage locations, encryption toggles, and retention settings as runtime inputs.
- **Identity Surface Kit:** link authn/authz assumptions for collaborative sessions, peer identity, and access control.
- **Dataset Surface Kit / Database Contract Kit:** attach durable export/import lanes or database mirrors without collapsing replicated live state into analytical or server-side schema truth.

## Non-goals
- standardizing one CRDT algorithm
- inventing a universal sync wire format
- replacing storage or network adapters
- replacing hosted collaboration backends
- pretending strong consistency and local-first eventual consistency are interchangeable
- forcing rich text, tree, map/list, and opaque custom replicated state into one fake canonical document model

## First implementation shape
A credible first implementation could be mostly adapters and validators:
- generate `replica-surface` + `replica-doc-catalog` declarations from app config and small annotations/macros
- ingest raw Automerge/Loro/Yrs metadata and attach it without flattening away source truth
- record simple convergence scenarios across 2–3 peers/runtimes
- emit generated support/reference docs for collaborative surfaces
- attach snapshots/updates/traces as raw evidence
- provide a diff mode for support changes across releases

The winning version is intentionally boring: it turns “offline sync support” from folklore into reviewed artifacts.
