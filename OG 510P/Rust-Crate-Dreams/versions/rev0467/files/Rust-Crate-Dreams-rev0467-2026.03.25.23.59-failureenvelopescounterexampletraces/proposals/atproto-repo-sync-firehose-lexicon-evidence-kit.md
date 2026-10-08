---
id: P-0382
title: AT Protocol Repo Sync + Firehose + Lexicon Evidence Workbench Kit — relay/PDS drift, backfill replay, and migration-safe bundles
status: idea
domains: [social-web, federation, protocol, interoperability, validation, replay, data-portability]
last_reviewed: 2026-03-06
evidence:
  - https://atproto.com/specs/atp
  - https://atproto.com/specs/lexicon
  - https://atproto.com/specs/sync
  - https://atproto.com/guides/backfilling
  - https://docs.rs/atrium-api
  - https://docs.rs/atproto-lexicon
  - https://docs.bsky.app/blog/introducing-tap
---

# Problem

Rust now has real AT Protocol substrate: generated API types, Lexicon tooling, OAuth helpers, identity helpers, and multiple community implementations. The protocol itself also has a clearer operational story around repository sync, firehose consumption, backfill, and account migration.

But production pain is still concentrated at the seam between:

- **relay firehose ordering and app-specific indexing assumptions**,
- **live stream consumption and historical backfill correctness**,
- **Lexicon schema updates and what older consumers actually tolerate**,
- **PDS/repo exports and migration or recovery workflows**,
- and **“we saw a weird repo event” incidents that are hard to share without leaking user data**.

The missing Rust contribution is not another PDS, AppView, or full social product. It is an **evidence and replay workbench** for repo-sync correctness, Lexicon pinning, backfill semantics, and migration-safe debugging.

# What it provides

- `at-sync.lock` — pins sync semantics, Lexicon set, collection scope, firehose source, backfill policy, and redaction rules.
- `atreplay` IR — neutral representation of `subscribeRepos` events, account lifecycle transitions, backfill windows, repo CAR metadata, and expected application-level interpretations.
- `lexicon-pack` — fetches, snapshots, and validates the exact Lexicon set in scope.
- `event-normalizer` — canonicalizes relay/PDS/tap outputs into one comparable trace shape.
- `cargo at-evidence` — emits `*.atbundle.zip` with lockfile, normalized stream slices, backfill receipts, repo summaries, and notes.

# What the crate should provide other people

1. **A boring incident bundle for AT sync bugs**.
2. **Lexicon-pinned replay** instead of “works against current docs”.
3. **Backfill and migration receipts** that survive team or vendor handoff.
4. **Safe redaction** for repo content, handles, DIDs, and blobs.
5. **A way to compare sync interpretations** across raw firehose, direct repo fetches, and simplified tap-style streams.

# Persona / who it’s for

- Rust maintainers building AT Protocol clients, services, feeds, or labelers
- Teams consuming the firehose for indexing or moderation pipelines
- Operators debugging repo sync, migration, or backfill correctness
- Researchers and archivists who need shareable, minimal replay bundles

# Users & user stories

- **Feed author**: “Replay the exact repo events that caused my feed index to diverge after a schema change.”
- **PDS operator**: “Produce a minimal, shareable bundle that explains why one repo backfill failed or replayed duplicates.”
- **SDK maintainer**: “Pin a Lexicon snapshot and prove whether a generated type change is source-breaking, wire-breaking, or harmless.”
- **Migration engineer**: “Show whether a repo export/import mismatch is due to sync semantics, missing blobs, or app-layer assumptions.”

# Prior art (and why it’s insufficient)

- Official AT Protocol specifications document repositories, sync, Lexicon, and account behavior.
- Official guidance now exists for backfilling and for the Tap service that simplifies repo synchronization.
- Rust already has `atrium-api`, `atproto_lexicon`, OAuth/identity helpers, and adjacent crates.

What Rust still lacks is a **coordination artifact**: one default way to pin protocol/schema assumptions, normalize event streams, record backfill decisions, and ship redacted replay bundles.

# Design goals

1. **Version- and Lexicon-aware** — pin the schema set in the lockfile.
2. **Ordering-honest** — represent per-repo ordering, backfill concurrency, and cursor assumptions explicitly.
3. **Migration-aware** — repo export/import and account lifecycle traces must be first-class.
4. **Privacy-preserving** — bundles must be shareable with aggressive redaction.
5. **Implementation-neutral** — work above official and community clients/relays, not replace them.

# MVP surface

- Minimal types: `AtSyncLock`, `LexiconSnapshot`, `RepoEventTrace`, `BackfillReceipt`, `AtBundle`
- Minimal functions:
  - `snapshot_lexicons()`
  - `normalize_events()`
  - `replay_repo_trace()`
  - `write_bundle()`
- Feature flags:
  - `firehose`
  - `backfill`
  - `migration`
  - `lexicon-pin`
  - `redaction`

# Compatibility story

- Ingests traces from live firehose consumers, relay logs, PDS fetches, or Tap-like simplifiers.
- Treats Lexicon resolution/generation as an adapter around one stable evidence format.
- Makes the distinction between raw repo semantics and app-specific indexing semantics explicit.
- Supports both minimal schema-only bundles and richer replay bundles with fixture content.

# Conformance & fixtures

- Tiny corpora for handle changes, repo deletions, empty commits, blob fetch misses, and backfill-after-live races.
- Goldens for “same repo state, different consumer interpretation”.
- Lexicon fixture packs that pin generated models alongside raw schema docs.
- Account lifecycle fixtures for deactivation, deletion, and migration edge cases.

# Path to boring stability

- Stabilize the bundle schema, Lexicon snapshot format, and redaction policy first.
- Keep the first release focused on repo sync and replay, not generic social-web analytics.
- Make ordering and backfill assumptions explicit everywhere.
- Ship with a small public fixture corpus rather than giant network captures.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 25/30**

# Minimum lovable MVP

A library and CLI that pin a Lexicon set, normalize `subscribeRepos` traces and repo fetches, replay backfill decisions, and emit compact `*.atbundle.zip` artifacts for debugging or compatibility testing.

# De-risk plan

1. Start with read-only normalization and replay.
2. Keep blob content optional and aggressively redactable.
3. Model per-repo ordering and cursor semantics explicitly.
4. Separate raw protocol replay from application semantics in the IR.

# Non-goals

- Not a replacement for a PDS, relay, or AppView.
- Not a feed-generator framework.
- Not a user-data warehouse.
- Not a moderation policy engine.

# Architecture & API sketch

```rust
pub struct AtSyncLock {
    pub sync_profile: String,
    pub lexicon_snapshot: String,
    pub collections: Vec<String>,
    pub backfill_policy: String,
}

pub fn snapshot_lexicons(sources: &[String]) -> Result<LexiconSnapshot>;
pub fn normalize_events(input: &[u8]) -> Result<RepoEventTrace>;
pub fn replay_repo_trace(trace: &RepoEventTrace, lock: &AtSyncLock) -> ReplayResult;
```

Bundle draft: `at-sync.lock`, `lexicons.json`, `events.json`, `backfill.json`, `repo-summary.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Default to structural summaries instead of raw record content.
- Support selective removal or hashing of DIDs, handles, blobs, and collection payloads.
- Record the precise sync source and normalization version in each bundle.
- Make “content omitted” explicit so redaction is not mistaken for absence.

# Maintenance & governance plan

- Keep the core about lockfiles, trace normalization, replay, and redaction.
- Version any schema adapters separately.
- Publish small public fixture bundles tied to concrete protocol/Lexicon snapshots.
- Resist product creep into full-hosting or feed infrastructure.

# Milestones

## 0.1
- event normalization
- Lexicon snapshotting
- replay bundle format

## 0.2
- backfill receipts
- account lifecycle fixtures
- CAR/repo summary helpers

## 1.0
- stable `*.atbundle.zip`
- public replay corpus
- documented compatibility policy for schema and sync changes

# Open questions

- What is the smallest useful public replay corpus that still covers migration and backfill races?
- How should the crate model app-layer interpretation without overfitting to Bluesky-specific products?
- Which parts of sync v1.1 evolution belong in the stable lockfile versus experimental overlays?

# Sources

- AT Protocol overview: https://atproto.com/specs/atp
- Lexicon spec: https://atproto.com/specs/lexicon
- Sync spec: https://atproto.com/specs/sync
- Backfill guide: https://atproto.com/guides/backfilling
- `atrium-api`: https://docs.rs/atrium-api
- `atproto_lexicon`: https://docs.rs/atproto-lexicon
- Tap introduction: https://docs.bsky.app/blog/introducing-tap
