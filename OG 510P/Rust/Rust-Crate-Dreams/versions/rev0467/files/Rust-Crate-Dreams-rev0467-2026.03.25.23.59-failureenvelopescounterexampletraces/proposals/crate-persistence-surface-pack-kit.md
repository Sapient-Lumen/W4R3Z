---
id: P-0522
title: Crate Persistence Surface Pack Kit — on-disk/wire maps, durability receipts, and recovery/migration diffs for library authors
status: idea
domains: [crates, dx, persistence, serialization, storage, durability, schema-evolution, recovery, supportiveness]
last_reviewed: 2026-03-19
evidence:
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://doc.rust-lang.org/std/fs/struct.File.html
  - https://doc.rust-lang.org/std/fs/fn.rename.html
  - https://docs.rs/tempfile/latest/tempfile/struct.NamedTempFile.html
  - https://docs.rs/atomic-write-file/latest/atomic_write_file/
  - https://docs.rs/tokio/latest/tokio/fs/index.html
  - https://serde.rs/
  - https://serde.rs/container-attrs.html
  - https://serde.rs/field-attrs.html
  - https://docs.rs/serde-reflection/latest/serde_reflection/
  - https://docs.rs/postcard/latest/postcard/
  - https://docs.rs/redb/latest/redb/struct.Database.html
  - https://docs.rs/revision/latest/revision/attr.revisioned.html
---

# Problem

The archive now has much better receiver-facing lanes for:

- choosing crates,
- understanding support claims,
- fitting interop profiles,
- getting compile-time guidance,
- handling runtime failure handoff,
- upgrading,
- leaving a crate,
- choosing setup scenarios,
- reasoning about performance posture,
- understanding observability surfaces,
- reviewing authority / determinism posture,
- reviewing lifecycle / shutdown behavior,
- and reviewing resource / saturation posture.

It still lacks a good answer to a different but extremely common downstream question:

> “If this crate writes bytes that will outlive the process, what exactly is it promising about format stability, compatibility, crash safety, recovery, and migration?”

That gap matters because today’s Rust persistence substrate is real but scattered.

The December 2025 Rust vision-doc work explicitly recommends more **supportive interfaces from crates**.
The 2025 State of Rust survey says online docs remain the preferred canonical reference, followed by studying code itself.
That makes persistence truth a crate-support surface, not just a storage-engine implementation detail.

Today’s ecosystem already exposes many sharp persistence ingredients:

- `std::fs::File` distinguishes `sync_data` from `sync_all`, and the docs note that dropping a file ignores close errors.
- Serde gives crate authors many compatibility levers such as `default`, `alias`, `rename`, tagged/untagged enum representations, and `deny_unknown_fields`.
- `serde-reflection` can extract format descriptions and keep them under version control to catch unintended binary-format changes.
- Postcard now has a documented and stable wire format.
- `revision` attaches history metadata to fields and supports version-tolerant reads/writes across schema changes.
- redb documents crash recovery from unclean shutdowns and exposes an integrity-check / repair surface.
- Tokio’s `fs` module runs ordinary blocking file operations behind `spawn_blocking`, which is useful ergonomically but does not by itself create a new persistence or durability contract.

But today that substrate still does **not** give maintainers one boring workflow for questions like:

- which persisted surfaces are internal-only versus meant to survive upgrades,
- whether a stored format is schema-described, version-tagged, opaque, or “best effort only”,
- whether “write completed” means only userspace buffering, OS visibility, data-sync, metadata-sync, transactional commit, or external service acknowledgment,
- what recovery posture exists after app crash, OS crash, power loss, or partial write,
- which migrations are automatic, reversible, lossy, or manual-review-required,
- what compatibility range is actually promised for old files, messages, snapshots, or journals,
- and how that persistence surface changed across releases.

The worthy crate is therefore **not** another serializer, **not** another database engine, **not** another migration runner, and **not** another storage backend by itself.
It is a **Crate Persistence Surface Pack Kit**: a crate that helps maintainers author, test, diff, and export the receiver-facing persistence contract their crate gives other people.

# Main judgment

See also `meta/crate-persistence-surface-product-plan-2026-03-19.md` for the current implementation-ready `0.1` sketch and `meta/crate-persistence-surface-lane-boundaries-2026-03-19.md` for lane separations.

A worthy crate here should provide a receiver-facing answer to:

1. **What bytes or state produced by this crate are expected to outlive the process?**
2. **Which persisted surfaces are stable contracts, and which are internal implementation details?**
3. **What compatibility range is promised for old files/messages/snapshots/journals?**
4. **What durability boundary is actually promised when an operation returns?**
5. **What kind of compatibility authority backs that promise: stable spec, guarded schema snapshot, revision metadata, or only best-effort shape?**
6. **What recovery posture exists after interruption, crash, corruption, or partial write, and was it witnessed?**
7. **How does a downstream user migrate persisted state across releases?**
8. **How did that persistence surface change across releases?**
9. **What path object was actually published or replaced, especially when symlinks or temp-file replacement are involved?**
10. **Which metadata classes survive replacement and which can drift even when the bytes are safely swapped in?**

That is more valuable than leaving users to reconstruct persistence truth from README prose, scattered serde attributes, storage-engine docs, and incident archaeology.

# What it provides

- `persistence-pack.toml` — versioned declaration of persisted surfaces, format classes, stability lanes, durability boundaries, recovery posture, and migration lanes.
- `persistence-surface.receipt.json` — observed receipt for files, messages, snapshots, WAL/journal surfaces, schema/version tags, and selected write/read flows.
- `format-compat.report.json` — explicit classification such as `schema_described`, `version_tagged`, `stable_wire_spec`, `best_effort_serde_shape`, `internal_only`, or `manual_review_required`.
- `durability-boundary.report.json` — explicit boundary such as `memory_only`, `userspace_buffer_only`, `os_visible`, `data_synced`, `metadata_synced`, `transaction_committed`, `remote_acked`, or `manual_review_required`.
- `recovery-posture.report.json` — explicit classification such as `stateless_retry`, `replay_journal`, `copy_on_write_recover`, `backup_restore_required`, `partial_write_risk`, `corruption_detected_manual_repair`, or `manual_review_required`.
- `migration-recipe.manifest.json` — smallest before/after examples for supported migration lanes, including whether old data is read in place, rewritten, upgraded eagerly, or converted offline.
- `compatibility-window.report.json` — declared compatibility promises such as `same_minor`, `same_major`, `explicit_revision_window`, `best_effort`, or `internal_only`.
- `compatibility-authority.policy.json` — why a compatibility claim should be trusted, such as `stable_external_spec`, `schema_snapshot_guarded`, `revision_history_guarded`, `engine_documented_contract`, or `serde_shape_best_effort`.
- `persistence-check.report.json` — verifies fixtures still match declared format, durability, and migration claims.
- `persistence-diff.report.json` — compares two releases and classifies `format_surface_changed`, `compatibility_window_narrowed`, `durability_boundary_changed`, `migration_lane_added`, `migration_lane_removed`, `recovery_posture_changed`, and `manual_review_required`.
- `surface-contract.policy.json` — explicit meaning and minimum evidence for `public_contract`, `soft_contract`, `rebuildable_cache`, `internal_only`, and `manual_review_required`.
- `write-path.receipt.json` — declared or observed save/commit steps such as temp-file replace, sync calls, directory sync, transaction commit, or remote acknowledgement.
- `atomicity-scope.report.json` — what the save path actually guarantees, such as `no_intermediate_state_only`, `destination_replace_same_mount`, `data_synced_without_directory_entry`, `fully_synced_local_publish`, or `manual_review_required`.
- `failure-model.profile.json` — explicit coverage for `clean_shutdown_only`, `process_crash`, `os_crash`, `power_loss`, `partial_write`, and `external_modification`.
- `recovery-witness.receipt.json` — whether recovery or repair was merely declared, or actually observed on representative artifacts.
- `publication-target.report.json` — explicit path-object truth such as `destination_path_replaced`, `symlink_replaced_target_untouched`, or `canonical_target_modified`.
- `identity-retention.report.json` — per-metadata truth for permissions, ownership, timestamps, ACLs, xattrs, and security-context retention.
- `persistence.summary.md` — short human-facing explanation of what a downstream integrator is actually buying.
- `cargo persistence-pack check` — run persistence fixtures and verify receipts against the pack.
- `cargo persistence-pack diff <old> <new>` — show how persistence promises changed.
- `cargo persistence-pack summary` — render a concise operator/integrator summary.

# What the crate should provide other people

1. **A receiver-facing persistence contract** above serializer docs, backend docs, and folklore.
2. **A surface inventory** so teams can tell config files, caches, snapshots, journals, exports, and wire messages apart instead of treating “bytes on disk” as one thing.
3. **A durability-boundary map** so operators know whether a successful call implies buffering, OS visibility, fsync-class durability, transaction commit, or something weaker/stronger.
4. **A compatibility-authority map** so integrators know whether “stable” means external spec, guarded snapshot, revision history, engine docs, or only best-effort Serde shape.
5. **An atomicity-scope report** so “atomic write” is not allowed to blur no-intermediate-state replacement with durable publication.
6. **A publication-target report** so path replacement, symlink replacement, and canonical-target mutation do not get blurred together.
7. **An identity-retention report** so safe replacement is not lazily mistaken for full metadata preservation.
8. **Checked migration recipes** so upgrades of persisted state stop being guesswork.
9. **Recovery posture reports plus witnesses** so incident responders know whether to retry, replay, repair, restore, or expect loss — and whether that path was actually exercised.
10. **A diffable persistence surface** so release reviewers can spot hidden format changes, narrowed compatibility, downgraded durability semantics, or changed publication/retention behavior.
11. **Importable vocabulary** for docs portals, selection/pathfinder tools, release review bots, and operational runbooks.

# Persona / who it’s for

- library authors whose crates write config files, snapshots, journals, caches, embedded databases, or durable message/state artifacts
- SDK/client maintainers whose APIs persist tokens, sessions, cursors, or offline state
- framework teams that expose storage adapters, export/import formats, or wire protocols
- downstream integrators trying to make stored-data risk reviewable
- docs/tool authors who want stable artifacts instead of scraping prose

# Users & user stories

- **Config-crate maintainer**: “Publish whether unknown fields are ignored or rejected, which renamed fields still load, and when a config file must be rewritten.”
- **Embedded-store maintainer**: “State exactly what `commit` means, whether crash recovery is automatic, and when external repair or backup restore is required.”
- **Protocol crate maintainer**: “Tell users whether my wire format is stable, version-tagged, or internal-only, and show the compatibility window.”
- **Platform engineer**: “Diff two releases and see whether the persisted format changed, whether compatibility narrowed, or whether migration became mandatory.”
- **Support engineer**: “When a customer hits corruption after power loss, show whether the crate promised journal replay, copy-on-write recovery, or only best-effort persistence.”

# Prior art (and why it’s insufficient)

- `std::fs::File` documents `sync_data`, `sync_all`, and the fact that dropping a `File` ignores close errors.
- `std::fs::rename` documents replacement-on-rename within the same mount-point boundary.
- `tempfile::NamedTempFile::persist` documents atomic replacement while also warning that neither file contents nor the containing directory are synchronized when `persist` returns.
- `atomic-write-file` documents “no intermediate state” atomic overwrite helpers.
- Serde documents powerful compatibility knobs like `default`, `alias`, `rename`, enum-tag choices, `deny_unknown_fields`, and custom conversion hooks.
- `serde-reflection` can capture format descriptions and test them under version control.
- Postcard documents a stable wire format.
- `revision` provides version-tolerant serialization with field history metadata.
- redb documents ACID, crash-safety, and crash-recovery / repair substrate.

What remains missing is a **crate-authored persistence contract workflow** above those pieces:

- author one persistence support contract,
- verify it against fixtures,
- classify durability and recovery semantics honestly,
- export stable receipts,
- and diff the persistence surface over time.

That is a different lane from:

- **P-0514** release-to-release upgrade packs,
- **P-0516** configuration scenarios,
- **P-0519** authority / offline / determinism posture,
- **P-0520** lifecycle / shutdown truth,
- **P-0521** resource / saturation truth,
- generic serializer crates,
- embedded database engines,
- or domain-specific schema-evolution workbenches.

# Why now / why this can win now

1. The archive’s supportiveness frontier has gotten much better at “live with this crate” but still lacks a good “trust the bytes this crate leaves behind” lane.
2. Rust’s official messaging now explicitly makes supportive interfaces from crates feel strategic, not ornamental.
3. The substrate is mature enough to build on:
   - durability primitives exist,
   - serializer compatibility knobs exist,
   - some formats now publish stable wire specs,
   - and some storage crates already document recovery behavior.
4. Real incidents around corrupted caches, incompatible config files, and failed on-disk upgrades are rarely caused by one missing primitive; they are usually caused by missing **support artifacts**.
5. The crate can start with conservative declared facts + fixture-checked receipts rather than pretending all durability or compatibility facts can be inferred automatically.

# MVP surface

## CLI
- `cargo persistence-pack init`
- `cargo persistence-pack capture`
- `cargo persistence-pack check`
- `cargo persistence-pack diff <old> <new>`
- `cargo persistence-pack summary`

## Library crates
- `persistencepack-core` — schemas, diff logic, summary rendering, vocabularies.
- `persistencepack-serde` — serde-shape imports, tag/default/alias/rename capture, format-class helpers.
- `persistencepack-fs` — durability-boundary vocabulary and selected file-write receipts.
- `persistencepack-capture` — common capture helpers for files/messages/snapshots.
- `cargo-persistence-pack` — CLI.

## Feature flags
- `serde`
- `std`
- `postcard`
- `json-schema-export`
- `diff`

# Compatibility story

- Must work with declared-by-maintainer facts first; automatic inference is optional support, not the only path.
- Should import serde-shape hints when available, but must not pretend serde attributes alone settle full compatibility or durability.
- Should support both on-disk and on-wire surfaces with the same high-level vocabulary.
- Should interoperate with upgrade packs without collapsing into them: an upgrade pack explains moving code between releases, while a persistence pack explains moving **persisted state** safely.
- Should interoperate with authority/resource/lifecycle packs without collapsing into them: persistence surfaces can depend on authority, background work, and resource posture, but they remain a separate contract.
- Should stay neutral about the storage engine or serializer backend.

# Conformance & fixtures

The crate should ship fixture families that exercise both declared and observed truth:

1. **Versioned config file**
   - renamed field,
   - missing field with default,
   - unknown-field policy,
   - old config still loads / fails as declared.

2. **Binary snapshot**
   - stable or unstable format classification,
   - explicit revision tag presence/absence,
   - before/after sample bytes,
   - migration recipe verdict.

3. **Embedded durable store**
   - commit path,
   - declared durability boundary,
   - clean shutdown vs crash-recovery flow,
   - repair/manual-review boundary.

4. **Journal / WAL-backed state**
   - interrupted write,
   - replay path,
   - recovery-posture classification,
   - compatibility-window report.

5. **Ephemeral persistent cache surface**
   - explicitly marked non-contract storage,
   - best-effort compatibility,
   - discard/rebuild recommendation.

# Path to boring stability

- Freeze the pack/report schemas before promising broad automatic capture.
- Keep the vocabulary conservative where full certainty is impossible.
- Require every surface to declare whether it is a public contract, soft contract, or internal-only artifact.
- Preserve which facts were **declared**, which were **observed**, and which were **imported** from another tool.
- Make `manual_review_required` a first-class success state instead of forcing fake certainty.
- Reach 1.0 only after at least:
  - one config-file workflow,
  - one stable wire-format workflow,
  - one crash-recovery workflow,
  - and one migration-diff workflow
  are exercised end-to-end.

# Distinctive implementation shape

## Surface vocabulary

Each persisted surface should declare:

- `surface_kind`: `config_file`, `snapshot`, `wal_or_journal`, `embedded_db`, `cache`, `wire_message`, `export_file`, `manual_review_required`
- `contract_level`: `public_contract`, `soft_contract`, `internal_only`
- `format_class`: `schema_described`, `version_tagged`, `stable_wire_spec`, `opaque_binary`, `best_effort_serde_shape`, `manual_review_required`
- `durability_boundary`: `memory_only`, `userspace_buffer_only`, `os_visible`, `data_synced`, `metadata_synced`, `transaction_committed`, `remote_acked`, `manual_review_required`
- `recovery_posture`: `stateless_retry`, `replay_journal`, `copy_on_write_recover`, `restore_from_backup`, `discard_and_rebuild`, `manual_repair`, `manual_review_required`
- `compatibility_window`: `same_patch`, `same_minor`, `same_major`, `explicit_revision_window`, `best_effort`, `internal_only`, `manual_review_required`

## Example receipt fragment

```json
{
  "crate": "example-kv",
  "surface": "main_store",
  "surface_kind": "embedded_db",
  "contract_level": "public_contract",
  "format_class": "opaque_binary",
  "durability_boundary": "transaction_committed",
  "recovery_posture": "copy_on_write_recover",
  "compatibility_window": "same_major",
  "migration": {
    "strategy": "read_old_rewrite_new",
    "manual_review_boundary": false
  },
  "evidence": [
    "redb-like copy-on-write store",
    "commit path emits receipt on successful transaction"
  ]
}
```

# Example scenario families

1. **Versioned config file** — serde defaults/aliases/unknown-field policy, rewrite-on-save behavior, compatibility window.
2. **Stable wire payload** — tagged binary/text payload with explicit format stability and cross-version fixtures.
3. **Embedded KV store** — commit semantics, crash-recovery posture, repair/manual-review boundaries.
4. **Snapshot export/import** — offline migration recipe, version bump, compatibility window narrowing.
5. **Ephemeral persistent cache** — explicit internal-only / discard-and-rebuild classification.

# Early implementation plan

## 0.1
- Stabilize the pack/report schemas.
- Implement `init`, `capture`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows.
- Treat `surface-contract.policy`, `write-path.receipt`, and `failure-model.profile` as first-class review artifacts.
- Ship six scenario packs:
  - `versioned_config_file`
  - `binary_snapshot`
  - `embedded_kv_store`
  - `atomic_replace_without_directory_sync`
  - `serde_unknown_field_policy_narrowing`
  - `copy_on_write_recovery_vs_external_corruption`

## 0.2
- Add serde-shape importers for rename/default/alias/tag policy capture.
- Add basic file-write receipt capture helpers.
- Add `persistence-check` fixture runner.

## 0.3
- Add stable-wire-format adapters for formats with published specs.
- Add recovery-posture vocabulary and receipt rendering.
- Publish docs showing how to separate public-contract versus internal-only surfaces.

## 0.4
- Add release-to-release diff classification for hidden format changes and narrowed compatibility windows.
- Add import/export hooks for docs portals, pathfinder/selection tools, and upgrade-review tooling.

## 1.0
- Freeze the pack/report schema.
- Publish a conservative glossary for format class, durability boundary, recovery posture, and compatibility windows.

# Adoption strategy

- Start with crates that already write bytes users care about but document them piecemeal.
- Make the 0.1 value mostly documentation + fixture honesty, not deep fs instrumentation.
- Produce summaries that are useful even when only part of the surface is mechanically captured.
- Integrate with docs generation and release review so the persistence pack becomes part of normal maintenance, not a specialist audit ritual.
- Encourage crates to mark some surfaces `internal_only` explicitly, so silence stops being mistaken for compatibility promises.

# Why this could be epic

Because many painful Rust operational questions are really persistence-contract questions hiding behind other labels:

- “Can I roll back and still read yesterday’s state?”
- “Why did this config stop loading after the upgrade?”
- “What did `commit` or `save` actually guarantee?”
- “Did the power loss corrupt data or will the crate recover automatically?”
- “Is this on-disk format part of the public contract, or just internal cache trivia?”
- “Can two app versions share the same files/messages safely?”

Today teams answer those with source dives, changelog archaeology, and incidents.
A crate that makes the **persistence surface** reviewable, exportable, and diffable would turn a wide class of vague storage folklore into one boring support artifact.

# Non-goals

- building a new serializer, storage engine, or migration framework
- proving crash-safety on every filesystem / kernel / power-failure model by itself
- replacing formal schema languages or domain-specific conformance workbenches
- promising that every persisted format must be stable forever
- pretending all compatibility/durability facts can be inferred automatically without maintainer input

# Open questions

- Which persisted surfaces deserve first-class vocabulary in 0.1: config, snapshots, journals, caches, exports, wire messages, embedded DBs, or others?
- How should the crate represent “best effort but usually works” compatibility honestly without encouraging false confidence?
- Which parts of durability posture can be captured mechanically and which must remain maintainer-declared plus fixture-checked?
- How should persistence packs compose with upgrade packs when code migration and data migration diverge?
- Which lane should own warnings about wire-format changes that are semver-legal but operationally painful?

# Sources

- Rust vision doc (supportive interfaces from crates): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (docs + code remain the main learning surfaces): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `std::fs::File` docs (`sync_all`, `sync_data`, dropping ignores close errors): https://doc.rust-lang.org/std/fs/struct.File.html
- `std::fs::rename` docs (replace existing destination on the same mount point): https://doc.rust-lang.org/std/fs/fn.rename.html
- `tempfile::NamedTempFile::persist` docs (atomic replacement, but contents and containing directory are not synchronized on return): https://docs.rs/tempfile/latest/tempfile/struct.NamedTempFile.html
- `atomic-write-file` docs (atomic overwrite without intermediate state): https://docs.rs/atomic-write-file/latest/atomic_write_file/
- Serde overview: https://serde.rs/
- Serde container attributes (`deny_unknown_fields`, enum tags, defaults): https://serde.rs/container-attrs.html
- Serde field attributes (`alias`, `default`, `flatten`, custom adapters): https://serde.rs/field-attrs.html
- `serde-reflection` docs: https://docs.rs/serde-reflection/latest/serde_reflection/
- Postcard docs (documented stable wire format): https://docs.rs/postcard/latest/postcard/
- redb database docs (automatic recovery from crashes / unclean shutdowns): https://docs.rs/redb/latest/redb/struct.Database.html
- `revision` docs (`revisioned`, field history metadata): https://docs.rs/revision/latest/revision/attr.revisioned.html
