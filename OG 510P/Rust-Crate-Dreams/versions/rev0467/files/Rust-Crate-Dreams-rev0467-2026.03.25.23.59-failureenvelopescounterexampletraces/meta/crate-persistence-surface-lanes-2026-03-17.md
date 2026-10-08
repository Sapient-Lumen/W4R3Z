# Crate persistence-surface lane boundaries — 2026-03-17

This note keeps one promising crate lane from getting flattened into several neighbors.

The lane here is:

- **crate-authored persistence-surface contracts**:
  stable artifacts that tell downstream users what bytes or state may outlive the process, what compatibility window is promised, what durability boundary an operation reaches, how recovery works, and how persisted state migrates across releases.

That is **not** the same as generic serialization, storage engines, upgrade tooling, or domain-specific schema workbenches.

## What belongs in this lane

A proposal belongs here when its main output is something like:

- one `persistence-pack`,
- one `persistence-surface.receipt`,
- one `format-compat.report`,
- one `durability-boundary.report`,
- one `recovery-posture.report`,
- one `migration-recipe.manifest`,
- one `compatibility-window.report`,
- one `persistence-check.report`,
- and one `persistence-diff.report`.

The center of gravity is **receiver-facing persistence truth**.

## What does not belong in this lane

### 1. Not generic serializer or format substrate

Serde, postcard, version-tolerant serde helpers, and format-description tools are valuable substrate.
But the lane here is not “yet another serializer helper”.
It is the contract layer that tells users which persisted surfaces are public, stable, versioned, migratable, or internal-only.

### 2. Not embedded databases or storage engines

redb, sqlite wrappers, sled-like stores, journals, caches, and file-backed indexes are implementation substrate.
The lane here is not a new engine or adapter.
It is the artifact that explains what a chosen engine-backed crate promises to downstream users.

### 3. Not async file wrappers or convenience I/O layers

Tokio `fs`, io_uring wrappers, and similar crates may change *how* a caller reaches file operations, but they do not automatically answer what compatibility authority, atomicity scope, durability boundary, or recovery witness a crate should publish.
A persistence-surface pack may import those facts, but it sits above them as the receiver-facing contract layer.

### 4. Not release-to-release upgrade packs

**P-0514** explains how a downstream user moves code and configuration from crate release N to N+1.
Persistence packs explain how **persisted data** moves — or fails to move — across those releases.
Those are related, but they are not the same lane.

### 5. Not configuration-scenario packs

**P-0516** explains how to instantiate a crate for a named scenario.
Persistence packs explain what happens after the crate starts leaving durable bytes behind.

### 6. Not authority-surface packs

**P-0519** explains what ambient powers a crate may use and how deterministic/offline/sandboxed it can be.
Persistence packs explain what it writes, how durable those writes are, and what survives interruption.

### 7. Not lifecycle-surface packs

**P-0520** explains background work, cancellation, shutdown, flush/close/join/drain obligations.
Persistence packs explain the durable artifact after that work finishes or is interrupted.

### 8. Not resource-surface packs

**P-0521** explains queues, buffers, pools, workers, and saturation posture.
Persistence packs explain format stability, migration, recovery, and durability boundaries for long-lived bytes/state.

### 9. Not domain-specific schema / protocol workbenches

The repo already has many domain workbenches for specific standards and ecosystems.
A persistence-surface pack is broader and more receiver-facing: it gives a portable vocabulary for persisted-state promises across many crates.

## The tell

If the proposal’s core user question is:

- “What bytes does this crate leave behind?”
- “Will old data still load?”
- “What does `save`, `flush`, or `commit` really guarantee?”
- “How does this recover after interruption or crash?”
- “What changed about persisted-state compatibility across releases?”

then it belongs here.

If the core user question is instead:

- “Which serializer/backend should I choose?”
- “How do I configure this crate?”
- “How do I migrate my code?”
- “What powers/resources/background work does this crate use?”
- “Does this domain standard validate?”

then it belongs in some other lane.

## Portfolio rule

When future passes revisit this area, keep these lanes distinct:

1. **task-first selection / decision packs**,
2. **producer-side capability contracts**,
3. **shared interop profiles**,
4. **compile-time guidance packs**,
5. **runtime handoff packs**,
6. **upgrade packs**,
7. **off-ramp packs**,
8. **configuration-scenario packs**,
9. **performance-envelope packs**,
10. **observability-surface packs**,
11. **authority-surface packs**,
12. **lifecycle-surface packs**,
13. **resource-surface packs**,
14. **persistence-surface packs**,
15. **serializer / storage-engine substrate**,
16. **domain schema/protocol workbenches**.

Do **not** let the archive quietly rephrase persistence support as “better serde docs”, “better migration notes”, or “better storage-engine docs”.
