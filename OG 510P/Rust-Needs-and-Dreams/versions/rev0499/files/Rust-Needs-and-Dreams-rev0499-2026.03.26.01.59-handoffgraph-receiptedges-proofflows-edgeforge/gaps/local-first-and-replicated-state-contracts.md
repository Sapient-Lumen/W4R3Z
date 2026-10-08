# Gap: local-first and replicated-state contracts

## What is missing
Rust now has several credible engines for collaborative, local-first, and replicated state, but it still lacks a **shared replica-surface contract**.

Today there is no standard way to describe, exchange, diff, and review:
- which documents or state collections are replicated collaboratively,
- which parts of the state are official shared surfaces versus local/cache-only state,
- which sync/update/snapshot formats and transport assumptions are part of the support promise,
- which offline, branching, undo/history, and merge behaviors are officially supported,
- which persistence/compaction/GC/version-retention assumptions matter,
- which cross-language/runtime compatibility claims are in scope,
- which convergence and reconnect scenarios were actually checked,
- and what evidence exists that the declared replicated-state surface still matches the shipped application.

That missing layer matters because Rust no longer just has isolated CRDT experiments. `automerge` explicitly positions itself as a library for collaborative local-first applications and ships a sync protocol plus binary storage format; Yrs is a high-performance Rust port of Yjs with shared types, updates, undo/redo, past-revision support, and awareness/y-sync material in the docs; and Loro 1.0 explicitly targets real-time collaboration, version control, stable data format, and multi-language use from Rust, JS/WASM, and Swift. The remaining pain is increasingly the **portable support boundary above those engines**, not the bare existence of mergeable data structures.

Sources:
- https://automerge.org/automerge/automerge/index.html
- https://automerge.org/docs/hello/
- https://automerge.org/docs/reference/repositories/
- https://docs.rs/yrs/latest/yrs/
- https://docs.rs/yrs-lmdb/latest/yrs_lmdb/
- https://loro.dev/blog/v1.0
- https://loro.dev/docs
- https://loro.dev/docs/tutorial/loro_doc

## The current seam is awkward
The ecosystem clearly has ingredients:
- `automerge` gives Rust a local-first CRDT, sync protocol, binary format, and history/merge model, but its own docs note that the API is fairly low-level and point many application authors toward higher-level helpers;
- Automerge’s repository docs explicitly say the core CRDT + sync protocol still leave a lot of application plumbing, and `automerge-repo` exists to supply storage and network adapters;
- Yrs gives Rust a serious Yjs-compatible document/update engine, including update encoding, undo/redo, past revisions, and awareness/y-sync support;
- `yrs-lmdb` and `yrs-kvstore` show that persistence and document-store plumbing are already practical concerns rather than hypothetical future work;
- Loro explicitly frames syncing data and realtime collaboration as hard, positions itself as local-first state management, and emphasizes import/export, version control, time travel, peer IDs, and better DevTools as key value propositions;
- cross-language use is already real rather than aspirational, because Loro 1.0 explicitly spans Rust, JS/WASM, and Swift.

But actual application support truth still gets split across:
- ad hoc document ids and local/remote replica naming,
- raw CRDT document/update/snapshot files,
- persistence adapters and sync transport glue,
- app-level schema assumptions or JSON-like shape constraints,
- history/branching/time-travel behaviors,
- awareness/presence side channels,
- migration and compaction lore,
- and bespoke integration tests for “offline edit, reconnect, merge, and reload” cases.

The result is not that Rust lacks CRDT libraries.
The result is that there is still no portable way to say:
- “these are the collaborative documents/state collections we officially support,”
- “these are the sync, snapshot, and storage assumptions attached to them,”
- “this is the merge/history/retention posture we claim,”
- “these cross-runtime or cross-language lanes are supported,”
- or “these convergence/recovery scenarios were actually checked.”

That is the exact archive pattern worth elevating: strong point libraries, weak shared review layer.

Sources:
- https://automerge.org/automerge/automerge/index.html
- https://automerge.org/docs/reference/repositories/
- https://docs.rs/yrs/latest/yrs/
- https://docs.rs/yrs-lmdb/latest/yrs_lmdb/
- https://loro.dev/docs
- https://loro.dev/blog/v1.0
- https://loro.dev/docs/tutorial/loro_doc

## Why this matters
This gap is bigger than “better CRDT docs.”
It affects:
1. **product honesty** — “supports offline collaboration” can hide very different realities around persistence, reconnection, branch history, or transport assumptions;
2. **compatibility review** — changing document structure, update encodings, compaction rules, or snapshot compatibility can be a real breaking change for synced applications;
3. **cross-runtime collaboration** — multi-language/local-first stacks need a way to preserve support claims across Rust, browser, mobile, desktop, and server components;
4. **operational clarity** — compaction, history retention, redaction, import/export, and peer-identity rules are support claims, not invisible implementation details;
5. **testing realism** — many apps test happy-path sync but not one portable artifact saying which concurrent-edit, offline/reconnect, or persistence-reload scenarios were checked;
6. **ecosystem composition** — Client App Surface Kit, Event Surface Kit, Runtime Settings Kit, Identity Surface Kit, Dataset Surface Kit, and Background Work Kit all need a local replicated-state boundary without owning it.

There is also an important honesty constraint: local-first/CRDT systems do not solve every class of application correctness. Loro’s own guidance explicitly warns that applications requiring strong consistency or transactional integrity may need different designs. A good Rust ecosystem contribution should therefore make support posture and non-goals explicit instead of selling “offline sync” as a magical universal answer.

Sources:
- https://automerge.org/docs/hello/
- https://loro.dev/docs
- https://loro.dev/blog/v1.0
- https://docs.rs/yrs/latest/yrs/

## What “good” looks like
A worthy contribution here is **not** another CRDT algorithm crate, another hosted collaboration backend, or another opinionated full-stack local-first framework.

It is a shared replica-surface boundary:
- one `replica-surface/v0` describing app/workspace identity, collaborative surface ids, and supported replica roles,
- one `replica-doc-catalog/v0` giving stable identities for replicated documents/collections, schema attachments, support levels, and local-only versus sync-visible boundaries,
- one `sync-capability-profile/v0` describing transport classes, snapshot/update formats, awareness/presence lanes, peer-id assumptions, and cross-runtime compatibility claims,
- one `merge-history-profile/v0` describing conflict/merge posture, undo/redo, branching/time-travel, retention/GC/compaction, and migration/import/export assumptions,
- one optional `replica-storage-profile/v0` describing persistence adapters, durability levels, encryption/redaction posture, and backup/restore notes,
- one `replica-check-plan/v0` describing which convergence/offline/reconnect/reload scenarios were exercised,
- one `replica-check-report/v0` recording checked peers/runtimes, divergence findings, format-compatibility results, recovery/merge evidence, and raw attachment pointers,
- one optional `replica-diff-report/v0` for additive/breaking replicated-surface changes,
- and one `replica-pack/v0` bundle for CI, release review, device/app handoff, and later archaeology.

That would let Rust teams treat collaborative replicated state as a reviewable support surface instead of a pile of CRDT files, adapter code, and folklore about what happens when users go offline for a week and reconnect later.
