# P-0522 — Crate Persistence Surface Pack Kit: product plan refresh (2026-03-19)

## Why this lane deserves another pass

The March 17 plan got the lane to a believable `0.1`.
The sharper move now is to make **persistence support** answer a more concrete downstream question:

> “When this crate says it saved something, what path object changed, what metadata survived, what durability boundary was reached, and what recovery/migration story can I actually trust?”

That question is now unusually buildable because the Rust ecosystem already has real substrate for it:

- `std::fs::File` documents `sync_all` versus `sync_data`, and still warns that drop ignores close errors.
- `std::fs::rename` documents same-mount limits and platform-specific replacement behavior.
- `tempfile::NamedTempFile::persist` documents atomic replacement while also warning that neither contents nor containing directory are synchronized on return.
- `atomic-write-file` documents a stronger no-intermediate-state overwrite path, while also documenting symlink replacement and metadata-retention limitations.
- `tokio::fs` documents that ordinary file IO runs through `spawn_blocking`, which changes scheduling/perf posture but not the underlying persistence contract.
- Postcard, `serde-reflection`, and `revision` each provide a different kind of compatibility authority rather than one uniform “stable format” story.
- redb documents automatic recovery from crashes / power loss plus a separate integrity-check / repair boundary for suspected external modification.

The missing value is therefore **not** another serializer, **not** another database, and **not** another helper that merely says “atomic write”.
It is the support layer that turns those scattered facts into one compact contract another maintainer can inspect.

## Main judgment

A worthy `0.1` should treat five review objects as first-class:

1. **publication target** — which path object changes, including symlink-versus-target truth,
2. **identity retention** — which metadata classes survive replacement and which may drift,
3. **durability boundary** — what success means at return time,
4. **compatibility authority** — why a stable-format claim should be trusted,
5. **recovery witness** — which recovery/repair paths were actually observed.

Those objects sit naturally above the archive’s earlier format / migration / durability / recovery work.
They do not replace it.
They make it reviewable in the places where operational surprises usually happen.

## What the crate should provide other people

For downstream integrators, operators, and maintainers, the crate should provide:

1. **a persisted-state contract they can read quickly**
   - which durable surfaces matter,
   - which ones are public contracts versus rebuildable caches or internal state,
   - and what a successful save actually means.

2. **a publication-target report**
   - destination path replaced,
   - symlink replaced versus canonical target modified,
   - same-mount requirement or manual-review boundary,
   - and whether the save path leaves temporary names behind on abrupt interruption.

3. **an identity-retention report**
   - permissions,
   - owner/group,
   - timestamps,
   - ACLs,
   - xattrs / SELinux contexts,
   - and other metadata classes that may or may not survive replacement.

4. **a durability-boundary report**
   - userspace-buffer only,
   - OS-visible,
   - data-synced,
   - metadata-synced,
   - transaction-committed,
   - remote-acked,
   - or manual-review-required.

5. **a compatibility-authority map**
   - stable external specification,
   - schema snapshot under version control,
   - revision-history guard,
   - engine-documented contract,
   - or only best-effort Serde shape.

6. **a recovery-witness receipt**
   - declared only,
   - integrity-check observed,
   - repair path observed,
   - clean-shutdown-only,
   - or manual-review-required.

7. **checked migration recipes**
   - read old / write new,
   - offline conversion,
   - eager rewrite,
   - lossy path,
   - no automatic migration,
   - or manual review.

8. **release-to-release diffs**
   - hidden format drift,
   - narrowed compatibility windows,
   - changed save/replace semantics,
   - downgraded metadata retention,
   - recovery posture drift,
   - or newly unwitnessed repair paths.

## Recommended `0.1` artifact set

Keep the earlier artifact set, but promote two more files into first-class review objects:

- `publication-target.report.json`
- `identity-retention.report.json`

The complete compact bundle should revolve around:

- `persistence-pack.toml`
- `persistence-surface.receipt.json`
- `surface-contract.policy.json`
- `format-compat.report.json`
- `compatibility-window.report.json`
- `compatibility-authority.policy.json`
- `publication-target.report.json`
- `identity-retention.report.json`
- `write-path.receipt.json`
- `atomicity-scope.report.json`
- `durability-boundary.report.json`
- `failure-model.profile.json`
- `recovery-posture.report.json`
- `recovery-witness.receipt.json`
- `migration-recipe.manifest.json`
- `persistence-check.report.json`
- `persistence-diff.report.json`
- `persistence.summary.md`

## Suggested command surface

### `cargo persistence-surface init`
Create a starter `persistence-pack.toml` plus empty review-object stubs.
Anything uncertain should begin as `manual_review_required`, not guessed.

### `cargo persistence-surface capture`
Emit a normalized receipt bundle from a named persistence scenario.
In `0.1`, this should support imported evidence and fixture-driven capture, not pretend to universally prove crash consistency.

### `cargo persistence-surface check`
Validate that:
- surface classes parse,
- compatibility-authority classes parse,
- publication target is explicit,
- identity-retention claims are explicit or marked unknown,
- write-path steps and durability boundary do not contradict one another,
- recovery posture and failure model align,
- migration recipes are present when compatibility narrows.

### `cargo persistence-surface doctor`
Render human-first warnings such as:
- `atomic_replace_without_sync_boundary`
- `atomic_no_intermediate_state_presented_as_durable`
- `symlink_replace_presented_as_target_update`
- `metadata_retention_overclaimed`
- `stable_wire_claim_without_compatibility_authority`
- `compatibility_window_narrowed_without_migration_recipe`
- `recovery_path_declared_but_unwitnessed`
- `tokio_async_surface_presented_as_stronger_commit`
- `manual_review_required`

### `cargo persistence-surface diff <old> <new>`
Compare two packs or receipts and classify:
- `publication_target_changed`
- `identity_retention_changed`
- `durability_boundary_changed`
- `compatibility_authority_changed`
- `compatibility_window_changed`
- `recovery_posture_changed`
- `recovery_witness_changed`
- `migration_recipe_added`
- `migration_recipe_removed`
- `manual_review_required`

### `cargo persistence-surface summary`
Render a short support note answering:
- which persisted surfaces matter,
- what success means,
- what path object really changed,
- what metadata is or is not retained,
- how recovery is supposed to work,
- and where the caveats are.

### `cargo persistence-surface pack`
Emit one compact `.persistencesurface.zip` bundle for CI artifacts, release review, support handoff, or pathfinder imports.

## Scenario families that should anchor `0.1`

1. **temp-file replace without durable publication**
   - atomic replace,
   - but no directory-sync proof,
   - no fake “power-loss durable” badge.

2. **symlink replacement versus target mutation**
   - save path replaces the symlink itself,
   - target file left untouched,
   - publication target must be honest.

3. **metadata retention drift**
   - overwrite path is safer than truncate-in-place,
   - but timestamps / ACLs / xattrs / SELinux contexts are not preserved.

4. **async wrapper does not upgrade durability semantics**
   - Tokio file IO remains ordinary file IO behind `spawn_blocking`,
   - scheduling/perf improvements are not a new commit contract.

5. **stable-wire authority versus Serde-shape best effort**
   - Postcard stable spec,
   - `serde-reflection` schema snapshot,
   - `revision` history guard,
   - plain derive-only shape.

6. **automatic recovery versus external-modification repair**
   - automatic recovery for unclean shutdown,
   - integrity-check / repair for suspected external mutation,
   - witness status kept explicit.

## Recommended workspace split

- `persistence_surface_model`
  - schema types and diff classes
- `persistence_surface_check`
  - validation and doctor warnings
- `persistence_surface_summary`
  - markdown and support-bundle rendering
- `persistence_surface_capture`
  - imported-evidence adapters and fixture harness
- `cargo-persistence-surface`
  - CLI

Optional adapters can stay optional in `0.1`:
- `persistence_surface_fs`
- `persistence_surface_tempfile`
- `persistence_surface_atomic_write_file`
- `persistence_surface_tokio_fs`
- `persistence_surface_postcard`
- `persistence_surface_serde_reflection`
- `persistence_surface_revision`
- `persistence_surface_redb`

## Adoption strategy

- Start with crates whose durable surfaces already create operational questions.
- Prefer fixture-backed scenario evidence over grand crash-simulation claims.
- Make the first value mostly about **honest support truth**, not exhaustive verification.
- Optimize for release review and downstream support bundles rather than benchmarking contests.

## What to keep separate

Do **not** let future revisions collapse these lanes:

- serializer or wire-format libraries,
- storage engines and backends,
- release-code upgrade packs,
- lifecycle/resource/authority support packs,
- embedded flash/filesystem adoption kits,
- async file wrappers,
- and durable-byte support contracts.

The point of **P-0522** is the receiver-facing artifact above those pieces.
