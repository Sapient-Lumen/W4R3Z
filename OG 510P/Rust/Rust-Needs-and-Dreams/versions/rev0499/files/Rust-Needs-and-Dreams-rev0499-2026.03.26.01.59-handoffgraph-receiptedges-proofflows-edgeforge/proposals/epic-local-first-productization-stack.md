# Epic proposal: Local-First Productization Stack (`cargo local-product`, `local-first-product-pack/v0`)

## One-line thesis
Build a thin Rust companion layer for **local-first and collaborative products** that links **replica/document/history/storage truth**, **client-vs-relay/runtime-role truth**, **runtime and identity activation**, **recovery/export/migration truth**, and **support/docs truth** into one portable review boundary without pretending one CRDT engine, one sync protocol, one relay pattern, or one app shell has already won.

## Why this is now worth doing
Rust’s local-first story is now strong enough that the missing contribution looks like a **product boundary above the ingredients** rather than another ingredient:
- The local-first essay still gives the clearest product bar: software should work offline, sync across devices, and improve ownership, privacy, longevity, and user control.
  https://www.inkandswitch.com/essay/local-first/
- Automerge explicitly positions itself as a library for building collaborative local-first applications, and its docs split the world into **documents** and **repositories**. The repository docs are unusually direct that the CRDT plus sync protocol still leave “a lot of plumbing” around storage and networking, and the storage docs say a repo without a `StorageAdapter` is transient across restart.
  https://automerge.org/docs/hello/
  https://automerge.org/docs/tutorial/concepts/
  https://automerge.org/docs/reference/repositories/
  https://automerge.org/docs/reference/repositories/storage/
- The Rust `automerge_repo` crate then shows that this plumbing is already a real architectural layer in Rust rather than a browser-only detail: repo handles, peer-doc state, and background event-loop orchestration are public API surface.
  https://docs.rs/automerge_repo
- Yrs is likewise a serious but different lane: it is a high-performance Rust port of Yjs, and its `Awareness` docs explicitly say awareness is for **non-persistent** state like cursor, username, and status. That means durable shared-document truth and ephemeral live-presence truth are already separate public concepts.
  https://docs.rs/yrs/latest/yrs/
  https://docs.rs/yrs/latest/yrs/sync/awareness/struct.Awareness.html
- Loro now makes the “above raw CRDT containers” pressure even clearer. Its docs say the project wants better DevTools for local-first apps; Loro 1.0 says the storage format is stable and reports major loading-speed improvements; the new Loro Protocol ships matching Rust client/server implementations; and Loro Mirror explicitly exists to bridge CRDT state and UI state because that glue is repetitive and easy to get wrong.
  https://loro.dev/docs
  https://loro.dev/blog/v1.0
  https://loro.dev/blog/loro-protocol
  https://loro.dev/blog/loro-mirror
- Typed mapping layers are also now plainly real instead of aspirational. `autosurgeon` gives Automerge a serde-like Rust mapping story, and `lorosurgeon` does the same for Loro. That is exactly the shape of evidence that says product-state truth is escaping raw engine APIs.
  https://docs.rs/autosurgeon
  https://docs.rs/lorosurgeon
- The client shell side is no longer hypothetical either. Tauri 2 positions Rust-backed apps as cross-platform across desktop and mobile from one codebase, which increases the value of an honest boundary for offline state, relay use, sync posture, and supported recovery behavior instead of per-app README folklore.
  https://v2.tauri.app/

What is still missing is the **stack-level boundary that says one local-first product subject was reviewed with these replicated documents, these sync/storage assumptions, these client and relay roles, these runtime and identity settings, these recovery/export promises, these support caveats, and these bounded consumer handoffs**.

## Working name
- CLI: `cargo local-product`
- primary artifact: `local-first-product-pack/v0`

## Scope
### This epic should own
- local-first product subject identity
- imported replica-surface / client-app / event-or-service / runtime-settings / identity / support attachments
- diffable review points across document/sync/history/storage, client-vs-relay roles, runtime and auth posture, recovery/export/migration, and support claims
- bounded release / support / atlas / assistant handoffs
- verification of pack integrity and import references

### This epic should not own
- a universal CRDT engine or merge algorithm
- a hosted collaboration control plane
- a universal sync backend or relay protocol
- a universal desktop/mobile shell
- a one-number “collaboration ready” badge
- flattening peer-to-peer, relay-assisted, and import/export-only products into one fake runtime story

## Candidate artifact family
### `local-first-product-brief/v0`
Why the product exists, intended consumer set, local-first lanes in scope, supported environments, freshness budget, and review status.

### `local-first-product-subject/v0`
The exact app/workspace/release/deployment subject, imported replica/client/relay/runtime/identity surfaces, comparison base, and environment/support scope.

### `local-first-product-pack/v0`
The portable review bundle linking:
- imported `replica-surface` / `replica-doc-catalog` / `sync-capability-profile` / `merge-history-profile` attachments
- imported client-app / event-surface / service-surface attachments for device and relay roles
- imported runtime-settings / room / peer / auth / storage / endpoint attachments
- imported export / recovery / migration / support handoffs
- local notes, waivers, caveats, and integrity metadata

### `local-first-product-diff/v0`
What changed between two review points, with separate sections for:
- collaborative document or collection identity
- sync / transport / awareness / presence posture
- history / retention / compaction / storage posture
- client-vs-relay / runtime-role boundaries
- runtime / room / peer / auth activation posture
- recovery / export / migration guarantees
- support / docs / platform claims

### `local-first-product-handoff/v0`
Bounded consumer summaries for:
- release review
- support / incident review
- atlas / adoption review
- policy / privacy / ownership review
- assistant / editor rendering

## Recommended rollout
1. single-device durable lane
2. multi-replica sync + presence lane
3. relay / auth / runtime activation lane
4. recovery / export / migration lane
5. support / release / atlas / ownership handoff lane

This should be driven by [`design/local-first-productization-pilot-program.md`](../design/local-first-productization-pilot-program.md).

## What makes this epic “epic” rather than incremental
A merely incremental tool would improve one lane:
- a nicer CRDT engine,
- a nicer WebSocket relay,
- a nicer persistence adapter,
- a nicer Tauri starter template,
- or a nicer sync debugging dashboard.

An epic contribution here instead gives Rust one **portable local-first product contract** above those lanes.
That is strategically different because it can:
- make release/support/atlas/privacy reviews share the same subject and evidence boundary;
- let replica engines, awareness protocols, relay servers, and client shells stay specialized without pretending any one defines the whole product;
- keep durable replica truth, ephemeral presence truth, client/relay role truth, runtime/auth activation, recovery/export posture, and support/docs truth distinct but linked;
- and give downstream tooling a bounded artifact to import instead of re-scraping storage adapters, WebSocket notes, auth setup, mobile/desktop caveats, and issue-thread archaeology.

## Design principles
- **Replica truth is not client or relay truth.**
- **Awareness/presence truth is not durable document truth.**
- **Storage durability is not sync reachability.**
- **Local-first does not imply one networking topology.**
- **Live collaboration is not recovery or export truth.**
- **Support/docs/platform caveats are part of the product boundary.**
- **Consumer summaries are lossy on purpose and say so.**
- **The stack remains thin.**

## Success conditions
This epic is succeeding when Rust teams can say:
- “this is the exact local-first product subject,”
- “these are the replicated documents/collections and history/storage assumptions we actually support,”
- “these are the client, relay, and runtime roles that were actually checked,”
- “these are the room/peer/auth/storage settings that materially changed behavior,”
- “these are the recovery/export/migration guarantees,”
- “these are the docs/support/platform caveats,”
- “this is what changed from the prior review,”
- and “this is what release/support/atlas/privacy consumers may safely conclude,”

without inventing a bespoke collaboration-readiness schema for every repository.

## Read this with
- `gaps/local-first-and-replicated-state-contracts.md`
- `design/local-first-productization-stack.md`
- `design/local-first-productization-pilot-program.md`
- `design/replica-surface-kit.md`
- `design/client-app-surface-kit.md`
- `design/event-surface-kit.md`
- `design/service-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/identity-surface-kit.md`
- `design/support-envelope-kit.md`
