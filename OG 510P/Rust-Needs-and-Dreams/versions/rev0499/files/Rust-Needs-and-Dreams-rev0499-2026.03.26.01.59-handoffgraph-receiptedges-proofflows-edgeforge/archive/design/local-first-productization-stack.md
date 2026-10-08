# Design: Local-First Productization Stack (Replica Surface + Client App Surface + Event/Service Surface + Runtime Settings + Identity Surface + Support Envelope)

## Goal
Turn Rust local-first and collaborative applications into a **portable productization stack** instead of leaving each product to publish its offline/collaboration story as a tangle of CRDT-engine choices, repo/network/storage adapters, relay glue, auth/session caveats, client-specific defaults, migration scripts, and README prose.

The stack should **not** replace Automerge, Yrs, Loro, repo/backplane frameworks, storage adapters, or hosted sync products.
It should make them compose better and make supported local-first behavior reviewable.

## Why this note is needed now
Rust’s current signals say the missing problem is no longer “can Rust do local-first?” They say the missing problem is **what a Rust local-first product can honestly claim to support**:
- the local-first essay still gives the north star clearly: software should work offline, collaborate across devices, and improve long-term ownership, privacy, and user control;
- Automerge now presents itself as a local-first sync engine for multiplayer apps, while the Automerge Repo docs are explicit that the CRDT + sync protocol still leave significant application plumbing around storage and networking;
- Automerge Repo storage docs are also explicit that a repo without a `StorageAdapter` is transient and must reload from remote peers on restart, which is exactly the kind of product truth that disappears when teams speak only in engine names;
- Yrs already distinguishes document history from `Awareness` session state and exposes the y-sync protocol as a cross-system communication basis, which means “shared document” and “live user/session presence” are already separate public lanes;
- Loro now explicitly frames itself as a local-first CRDT framework with undo/redo, time travel, and cross-runtime Rust/JS/WASM/Swift use, Loro 1.0 says its data format is stable, the Loro Protocol now ships matching Rust client/server implementations, and Loro Mirror exists because CRDT-state ↔ UI-state glue is repetitive and easy to get wrong;
- the typed-mapping layer is also starting to matter: `autosurgeon` gives Automerge a serde-like Rust mapping story, while `lorosurgeon` does the same for Loro, which is a strong signal that application-state/product-state truth now exists above raw CRDT containers;
- app-shell reality is no longer hypothetical either: Tauri 2 now makes Rust-backed desktop/mobile shells a mainstream product lane, which increases the value of honest offline/sync/runtime/recovery boundaries above individual engines.

Together, those signals argue that the missing contribution is **not** another CRDT engine, sync backend, or full-stack collaboration framework. It is the **boring portable boundary above the ingredients**.

## Stack layers

### 1) Replica Surface: declared collaborative document, sync, history, and storage truth
Replica Surface owns the **declared replicated-state boundary** for a product, app, service, or workspace:
- collaborative document and collection identities,
- local-only versus sync-visible state,
- sync/update/snapshot capabilities,
- merge/history/undo/retention posture,
- persistence and recovery assumptions,
- and checked convergence evidence.

Replica Surface answers questions like:
- “Which local-first documents or state families are officially supported?”
- “What offline/catch-up/history behavior is part of that promise?”
- “Which persistence guarantees are real versus accidental?”

Design rule: **engine choice must not be the only durable description of the collaborative product surface**.

### 2) Client App Surface + Event/Service Surface: actual device, UI, and relay boundaries
Local-first products are rarely just “a CRDT library in memory.”
They usually involve:
- desktop/mobile/browser application identities,
- lifecycle and capability posture,
- relay/server/event boundaries when sync is not purely peer-to-peer,
- document/open/share/link flows,
- background or reconnect behavior,
- and client-vs-relay responsibilities.

This layer answers questions like:
- “Which parts of the system are peer replicas, browser/mobile clients, or relay services?”
- “Which sync lanes are direct, relayed, store-and-forward, or import/export only?”
- “Which collaboration claims depend on a real service boundary?”

Design rule: **local-first product truth must not blur client identity and relay/service identity into one fake ‘sync runtime’.**

### 3) Runtime Settings + Identity Surface: activation, room, peer, and access posture
Real local-first systems only become honest when activation and access posture are explicit:
- relay endpoints and discovery rules,
- local storage paths and persistence modes,
- room/document identifiers,
- peer/actor identity posture,
- auth/session/access assumptions for collaboration,
- encryption or redaction settings,
- and per-environment activation across local/dev/staging/production.

This layer answers questions like:
- “Which runtime settings determine where data lives and how it syncs?”
- “Which collaboration lanes require auth or relay credentials?”
- “What is local-only, what is shared, and under which principal or room model?”

Design rule: **offline/collaboration claims must not silently depend on hidden storage defaults, room naming rules, or invisible auth/session setup.**

### 4) Recovery, export, and migration truth: product continuity above live sync
Local-first products accumulate archaeology pressure quickly:
- snapshot/export/import lanes,
- backup and restore behavior,
- schema evolution and app-version transitions,
- compaction and retention changes,
- server/database mirrors where they exist,
- and cross-runtime or cross-language upgrade posture.

This layer answers questions like:
- “Can users move or back up their data?”
- “What happens when formats, adapters, or sync paths change?”
- “Which migration claims are real versus merely hoped for?”

Design rule: **live collaboration success is not proof of durable ownership, recovery, or upgrade safety.**

### 5) Support Envelope + DocProof: support, docs, and checked example truth
Local-first systems are unusually vulnerable to folk wisdom:
- supported platforms and runtimes,
- checked offline/reconnect docs and examples,
- browser/mobile/desktop support posture,
- supported relay/storage adapters,
- support levels for peer-to-peer versus relayed modes,
- and public/non-public collaboration features.

This layer answers questions like:
- “Which offline/collaboration setups are officially supported?”
- “Which examples and guides were actually checked?”
- “What part of the local-first story is public support versus experimental lore?”

Design rule: **one demo sync session or one happy-path reconnect example is not the support contract**.

### 6) Downstream consumers
The stack becomes ecosystem-shaping when real consumers can import it honestly:
- **release/support** consumers can answer what data/sync/recovery story a shipped app actually promised;
- **client/service** consumers can attach collaboration truth to real surfaces without becoming the new source of truth;
- **policy/security/ownership** consumers can reason about storage, relay, and export posture without scraping issue threads;
- **atlas/learning** consumers can compare serious Rust local-first lanes without pretending one engine or relay pattern has already won.

Design rule: **consumers import selected local-first-productization facts; they do not redefine the stack.**

## What an epic contribution should look like in practice
A worthy contribution here is not “the one true Rust local-first framework.”
It is a portable boring stack with clear boundaries:

1. **replica/document/history/storage truth first**
   - prove `replica-surface/v0`, `replica-doc-catalog/v0`, `sync-capability-profile/v0`, `merge-history-profile/v0`, `replica-storage-profile/v0`, and `replica-check-report/v0` on one real product;
2. **client/relay attachments second**
   - attach client-app and relay/service surfaces without flattening them into replica truth;
3. **runtime/identity activation third**
   - make storage, room, peer, relay, and auth/session posture diffable and reviewable;
4. **recovery/export/migration fourth**
   - prove backup/import/export/recovery and version-transition artifacts exist above live sync success;
5. **support/docs and consumer imports fifth**
   - prove public support claims, checked docs, and release/support/atlas consumers can import the artifacts without re-deriving them.

An eventual aggregate artifact may exist, but it should be a **thin pack of linked artifacts**, not a mega-schema that erases replica, client, relay, runtime, migration, and support boundaries. The proposal-layer candidate is now [`proposals/epic-local-first-productization-stack.md`](../proposals/epic-local-first-productization-stack.md): a thin `cargo local-product` / `local-first-product-pack/v0` layer above Replica Surface + Client App Surface + Event/Service Surface + Runtime Settings + Identity Surface + Support Envelope rather than another “just use this sync framework” pitch.

## Ranked first execution lanes
1. **single-device durable lane**
   - best first exporter because it proves offline durability, restart, and document identity without requiring a whole relay stack.
2. **same-product multi-device or multi-tab lane**
   - proves sync, awareness/session state, and reconnect behavior can be captured honestly.
3. **relay/auth lane**
   - proves room/peer/auth/runtime posture is part of the product boundary, not hidden setup glue.
4. **recovery/export/migration lane**
   - proves ownership and archaeology claims survive format changes, upgrades, and support events.
5. **support/release/customer-handoff lane**
   - proves the stack matters outside demos by attaching collaboration truth to docs, release notes, and support playbooks.

## Non-goals
- one universal CRDT algorithm or sync protocol;
- one hosted collaboration backend;
- another full-stack local-first framework that tries to own app, relay, storage, and auth all at once;
- flattening replica truth, client truth, relay truth, runtime truth, recovery truth, and support truth into one fake “collaboration readiness” badge;
- pretending strong-consistency systems and local-first eventual-consistency systems are interchangeable.

## Archive implications
- The archive should now treat **Replica Surface + Client App Surface + Event/Service Surface + Runtime Settings + Identity Surface + Support Envelope** as a coupled **Local-First Productization Stack** in frontier discussions.
- Future revisions should prefer **document/sync/history/storage truth, client/relay boundary truth, runtime/identity activation, recovery/export/migration evidence, and support/docs truth** over another CRDT engine comparison, relay wrapper, sync demo, or local-first framework bake-off.
- When Client, Service, Identity, Documentation, Release, or Atlas work cites collaboration readiness, they should import **replica truth**, **client/relay truth**, **runtime/identity truth**, **recovery truth**, and **support truth** separately.

## References (signals)
- Local-first principles:
  https://www.inkandswitch.com/essay/local-first/
- Automerge and Automerge Repo:
  https://automerge.org/
  https://automerge.org/docs/reference/repositories/
  https://automerge.org/docs/reference/repositories/storage/
- Yrs / y-sync / awareness:
  https://docs.rs/yrs/latest/yrs/
- Loro / Loro 1.0:
  https://docs.rs/loro/latest/loro/
  https://loro.dev/blog/v1.0
- typed mapping layers:
  https://docs.rs/autosurgeon/latest/autosurgeon/
  https://docs.rs/lorosurgeon/latest/lorosurgeon/
