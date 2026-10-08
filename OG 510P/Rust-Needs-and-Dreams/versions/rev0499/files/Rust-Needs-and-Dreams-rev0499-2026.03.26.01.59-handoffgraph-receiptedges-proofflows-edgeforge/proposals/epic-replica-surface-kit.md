# Epic proposal: Replica Surface Kit

## Thesis
Rust’s local-first / collaborative-state ecosystem is now mature enough that the missing contribution is no longer “yet another CRDT implementation.”
The higher-leverage missing piece is a **portable replicated-state contract** that lets teams declare, diff, validate, and ship what their applications actually promise: collaborative document identities, sync/snapshot/storage assumptions, merge/history posture, offline/reconnect expectations, and checked convergence evidence.

In other words: Rust needs a boring, attachable `replica-pack/v0` more than it needs one more engine-specific “offline sync helper.”

## Why now
The ecosystem signals line up:
- `automerge` is explicit about collaborative local-first use, offline editing, later sync, merge, history, and transport-agnostic operation.
- Automerge’s own repository docs explicitly say the core CRDT + sync protocol still leave substantial application plumbing.
- Yrs is a serious Rust Yjs-compatible implementation with update encoding, awareness/y-sync, undo/redo, and past-revision support already treated as real concerns.
- persistence adapters like `yrs-lmdb` show that durable local stores are already part of the real stack.
- Loro now positions itself as local-first state management with better DevTools, version control, import/export, time travel, and a stable data format in 1.0.
- cross-runtime use is already happening rather than hypothetical, because Loro explicitly spans Rust, JS/WASM, and Swift.

That means the missing substrate is not raw CRDT capability.
It is the **reviewable boundary above today’s pieces**.

Sources:
- https://automerge.org/automerge/automerge/index.html
- https://automerge.org/docs/hello/
- https://automerge.org/docs/reference/repositories/
- https://docs.rs/yrs/latest/yrs/
- https://docs.rs/yrs-lmdb/latest/yrs_lmdb/
- https://loro.dev/docs
- https://loro.dev/docs/tutorial/loro_doc
- https://loro.dev/blog/v1.0

## What should be built
A first credible version should ship:
1. `replica-surface/v0`, `replica-doc-catalog/v0`, `sync-capability-profile/v0`, `merge-history-profile/v0`, optional `replica-storage-profile/v0`, `replica-check-plan/v0`, `replica-check-report/v0`, optional `replica-diff-report/v0`, and `replica-pack/v0`
2. adapters for common Rust collaboration lanes (`automerge`, Automerge-style repo/storage/network attachments, Yrs docs/updates, Yrs persistence layers, Loro docs/exports/history artifacts)
3. generated support/reference docs for collaborative surfaces, supported document families, offline/history claims, and cross-runtime support posture
4. validation/reporting support for divergence, format mismatch, broken snapshot/update compatibility, missing history support, restore/recovery failures, and unchecked support lanes
5. release/CI examples showing replica packs attached to desktop/mobile apps, browser-backed clients, server relays, and hybrid local-first systems

The winning version is boring, adapter-heavy, and explicit about what it does **not** own.
It should make today’s pieces legible together rather than replacing them.

## Initial pilots
- one Automerge-backed Rust app with explicit storage/network adapter choices and checked offline/reconnect flows
- one Yrs-backed collaborative editor with awareness/y-sync, history checks, and persistence/reload evidence
- one Loro-backed local-first app with version/time-travel support, snapshot/update exports, and cross-runtime compatibility claims
- one hybrid app proving the artifacts can link a client surface, an optional relay/service surface, and durable local storage without flattening them into one monolith

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve document identity, sync posture, history posture, and storage posture
2. **v0.2 adapters**
   - support Automerge, Yrs, and Loro attachments plus basic local persistence lanes
   - support raw engine/update/snapshot artifacts without flattening them into one fake universal format
3. **v0.3 cross-kit integration**
   - integrate with Client App Surface, Runtime Settings, Identity Surface, Event/Service Surface, and Dataset/Database export lanes
   - support diff/baseline workflows across devices/runtimes/releases
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one engine or one UI stack

## Success metrics
- Teams can review collaborative/offline-support changes as explicit artifacts instead of reading adapter code, snapshots, and prose.
- Supported replicated documents and sync assumptions remain documented from one declared source.
- Cross-runtime/local-first claims become easier to trust because checked and illustrative material stay distinct.
- History/branching/compaction/recovery behavior becomes less folkloric and more reviewable.
- Rust local-first systems become easier to hand off to client, platform, docs, and ops workflows without bespoke glue.

## Archive fit
This proposal fills a real gap between several existing concise-archive kits:
- Client App Surface Kit covers mobile/desktop packaging, permissions, bridge APIs, and lifecycle truth,
- Runtime Settings Kit covers deployment configuration,
- Event/Service Surface Kits cover network/API boundaries,
- Dataset Surface Kit and Database Contract Kit cover data/export/storage contracts,
- Identity Surface Kit covers collaborative access assumptions,
- and Replay/DST/Background Work style kits cover execution evidence.

But none of those is the portable contract for the **replicated local-state boundary itself**.
Replica Surface Kit is the missing substrate that keeps collaborative document identities, sync capabilities, history posture, and convergence evidence attached to one reviewable interface without absorbing the rest of the stack into one mega-format.
