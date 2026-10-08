# Crate persistence-surface product plan — 2026-03-17

This note exists to keep **P-0522 Crate Persistence Surface Pack Kit** disciplined.
The archive already decided that the missing value is a **receiver-facing persisted-state / compatibility / durability / recovery contract**.
This pass answers a narrower question:

> If somebody actually started building **P-0522** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps crate authors publish one reviewable answer to:

- which persisted surfaces the crate actually creates or reads,
- which of those surfaces are public contracts versus rebuildable internals,
- what compatibility window each surface claims,
- why a compatibility claim is authoritative,
- what a successful save / commit / persist call actually means,
- what exact atomicity scope that path reaches,
- which interruption or corruption models the maintainer is claiming to survive,
- whether recovery or repair was actually witnessed,
- and what changed between releases.

It should **not** try to become a new serializer, embedded database, migration framework, crash-consistency test harness, or hosted schema registry.
Those are adjacent imports, not the product.

## What the crate should provide other people

For downstream users, operators, and release reviewers, the crate should provide:

1. **One compact persistence contract** instead of folklore spread across README prose, serde attributes, file helpers, storage-engine docs, and issue threads.
2. **A persisted-surface inventory** so config files, caches, snapshots, export files, journals, embedded stores, and wire payloads stop being blurred together.
3. **A contract-level distinction** so teams can tell `public_contract` from `soft_contract`, `rebuildable_cache`, or `internal_only`.
4. **A write-path receipt** so “save succeeded” can be read as `write_in_place`, `tempfile_replace`, `append_journal`, `transaction_commit`, `remote_ack`, or `manual_review_required`.
5. **A compatibility-authority policy** so teams can tell `stable_external_spec` apart from `schema_snapshot_guarded`, `revision_history_guarded`, `engine_documented_contract`, or `serde_shape_best_effort`.
6. **An atomicity-scope report** so “atomic save” does not blur no-intermediate-state replacement with fully durable publication.
7. **A failure-model profile** so maintainers can state whether claims cover process crash, OS crash, power loss, external modification, partial write, or only clean shutdown.
8. **A recovery-witness receipt** so repair and recovery paths can be marked `declared_only` or actually observed on representative surfaces.
9. **A compatibility-window report** so integrators know whether old state is expected to load across patch, minor, major, or an explicitly bounded revision window.
10. **A short human summary** that can be pasted into release notes, upgrade docs, or support templates.
11. **A release diff** that makes hidden persistence-surface regressions loud.

For maintainers, the crate should provide:

1. a small policy file that is cheap to review,
2. explicit `manual_review_required` escape hatches rather than fake certainty,
3. a way to import existing serde / file / storage substrate instead of replacing it,
4. one place to record whether a cache is rebuildable rather than silently “sort of stable”,
5. and a CI gate for “this release changed durable-byte promises”.

## Recommended `0.1` command surface

### `cargo persistence-surface init`
Create a starter `persistence-pack.toml` by importing obvious candidates from:

- maintainer-declared surface inventory,
- known config/export/cache paths,
- serde hints when present,
- optional format adapters such as Postcard or `revision`,
- and selected storage-engine notes when the maintainer points at them.

The generated pack should be incomplete on purpose.
Anything uncertain should be marked `manual_review_required` rather than guessed.

### `cargo persistence-surface capture`
Emit one normalized receipt bundle from a declared persistence workflow.
This should capture:

- surface inventory,
- contract-level and compatibility claims,
- write-path steps,
- failure-model coverage,
- selected recovery/migration notes,
- and imported evidence.

`capture` should work on imported artifacts too.
It must not require that the crate performed a real crash-consistency test in the same invocation.

### `cargo persistence-surface check`
Run the local validation pass:

- do declared surfaces parse,
- do compatibility classes and durability/write-path classes parse,
- do imported serde / format hints agree with declared policy where applicable,
- are rebuildable caches clearly demoted,
- are migration recipes present where compatibility windows narrowed,
- and which parts remain manual-review-only?

### `cargo persistence-surface doctor`
Render human-facing warnings for suspicious situations such as:

- `public_contract_without_version_story`
- `atomic_replace_without_sync_boundary`
- `atomic_no_intermediate_state_presented_as_durable`
- `cache_surface_presented_as_public_contract`
- `stable_wire_claim_without_compatibility_authority`
- `serde_unknown_field_policy_narrowed`
- `compatibility_window_narrowed_without_migration_recipe`
- `recovery_claim_exceeds_evidence`
- `recovery_path_declared_but_unwitnessed`
- `manual_review_required`

`doctor` should be a human-first renderer over captured artifacts, not a magical verifier.

### `cargo persistence-surface summary`
Render a short receiver-facing note for release docs or operator runbooks.
A good summary answers:

- which persisted surfaces matter,
- which ones are public contracts,
- what write/commit success means,
- how recovery is supposed to work,
- and where the caveats are.

### `cargo persistence-surface diff <old> <new>`
Compare two receipts or packs and classify:

- `surface_added`
- `surface_removed`
- `contract_level_changed`
- `compatibility_window_changed`
- `write_path_changed`
- `failure_model_changed`
- `recovery_posture_changed`
- `migration_recipe_added`
- `migration_recipe_removed`
- `manual_review_required`

### `cargo persistence-surface pack`
Emit one compact `.persistencesurface.zip` bundle for CI artifacts, release review, downstream support, or operational handoff.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `persistence_surface_model`
  - shared Rust types for packs, receipts, reports, manifests, evidence classes, and diffs
- `persistence_surface_discovery`
  - import logic for declared surfaces, serde hints, stable-wire adapters, and file-write / store-write declarations
- `persistence_surface_check`
  - policy validation, compatibility/durability classification, drift checks, and doctor warnings
- `persistence_surface_pack`
  - summary rendering, diff writing, markdown output, and zip bundle emission
- `cargo-persistence-surface`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core vocabulary is trusted:

- `persistence_surface_serde`
- `persistence_surface_postcard`
- `persistence_surface_revision`
- `persistence_surface_redb`
- `persistence_surface_fs`

## `0.1` artifact set

The archive already had the right center of gravity.
`0.1` should still revolve around:

- `persistence-pack.toml`
- `persistence-surface.receipt.json`
- `format-compat.report.json`
- `durability-boundary.report.json`
- `recovery-posture.report.json`
- `migration-recipe.manifest.json`
- `compatibility-window.report.json`
- `persistence-check.report.json`
- `persistence-diff.report.json`
- `persistence.summary.md`

This pass adds six more important artifacts:

- `surface-contract.policy.json` — what `public_contract`, `soft_contract`, `rebuildable_cache`, `internal_only`, and `manual_review_required` mean and what minimum evidence each class expects.
- `write-path.receipt.json` — the declared or observed save/commit path, including steps like temp-file replace, sync class, journal append, transaction commit, directory sync, or remote acknowledgement.
- `failure-model.profile.json` — which interruption/corruption models the claim covers, such as process crash, OS crash, power loss, external modification, or clean-shutdown-only.
- `compatibility-authority.policy.json` — why a compatibility claim should be trusted, such as a stable external specification, a guarded schema snapshot, revision metadata, engine docs, or only best-effort shape.
- `atomicity-scope.report.json` — whether the write path guarantees only no-intermediate-state replacement, same-mount destination swap, synced data, durable directory publication, or some narrower boundary.
- `recovery-witness.receipt.json` — whether recovery/repair was merely declared, or actually witnessed on representative surfaces.

Those files matter because persistence gets vague again if the archive only records format and compatibility but not:

- whether the bytes are a public promise,
- why the compatibility story is authoritative,
- what happened on the path to durable publication,
- what exact atomicity scope that path reaches,
- and whether recovery claims were actually exercised.

## Discovery order

A disciplined import order helps prevent fake certainty.

1. **Declared surface inventory**
   - `persistence-pack.toml`
   - maintainer-declared surface names, classes, and contract levels
2. **Observed/imported format hints**
   - serde attributes
   - format adapters such as Postcard or `revision`
3. **Write-path declarations**
   - temp-file replacement
   - in-place writes
   - journal append / transaction commit / remote ack
4. **Failure-model and recovery notes**
   - process crash, OS crash, power loss, external mutation, repair paths
5. **Migration and compatibility notes**
   - read-old/write-new, offline conversion, explicit compatibility windows
6. **Manual review zones**
   - anything still uncertain or backend-specific

The importer should prefer visible uncertainty over synthesis.

## Contract-level policy

The first implementation should treat **contract levels as first-class review objects** and keep them separate from file type or serializer choice.

### What should count as contract levels in `0.1`

- `public_contract`
- `soft_contract`
- `rebuildable_cache`
- `internal_only`
- `manual_review_required`
- `unknown`

### What should *not* be encoded as contract levels in `0.1`

- “the bytes probably stay compatible because they use Serde”
- “the format is on disk so it must be a public contract”
- “a cache happened to survive upgrades so it is now promised”
- “the project never documented migration, therefore migration does not matter”

The contract-level policy should be versioned and diffable.
If a maintainer cannot explain why a persisted surface is a `public_contract`, the surface should fall back to `soft_contract` or `manual_review_required`.

## Compatibility-authority policy

The first implementation should treat **why a compatibility promise is trustworthy** as explicit review material.
A good `0.1` should model:

- `stable_external_spec`
- `schema_snapshot_guarded`
- `revision_history_guarded`
- `engine_documented_contract`
- `serde_shape_best_effort`
- `manual_review_required`
- `unknown`

The crate should not let one strong surface (for example, a Postcard-backed packet with a published stable wire specification) silently upgrade every other persisted surface in the crate to “stable”.
That distinction is exactly why the compatibility-authority artifact needs to exist.

## Write-path policy

The first implementation should treat **write/commit semantics** as explicit review material.
A good `0.1` should model:

- `write_in_place`
- `tempfile_replace`
- `append_journal`
- `transaction_commit`
- `remote_ack`
- `manual_review_required`

with optional step hints such as:

- `flush_called`
- `sync_data_called`
- `sync_all_called`
- `rename_used`
- `directory_sync_observed`
- `repair_tool_available`

The crate should not pretend that an atomic replace helper proves full durability.
That distinction is exactly why the write-path receipt needs to exist.

## Failure-model policy

The first implementation should treat **failure models** as explicit coverage claims, not hidden assumptions.

A good `0.1` should model:

- `clean_shutdown_only`
- `process_crash`
- `os_crash`
- `power_loss`
- `partial_write`
- `external_modification`
- `manual_review_required`

The crate should allow a maintainer to say “we cover process crash but not power loss” or “we recover from unclean shutdown but external file mutation may require repair”.
That is more honest than one flat “crash safe” badge.

## Proving-ground archetypes

A worthy first implementation should prove itself against at least five archetypes:

1. **Config crate**
   - field rename/default/unknown-field behavior
   - rewrite-on-save caveats
2. **Local durable store**
   - transaction commit versus repair/manual-review boundary
3. **Stable wire/export format**
   - explicit wire stability and compatibility window
4. **Rebuildable cache**
   - non-contract state that must be demoted explicitly
5. **Credential/session persistence**
   - on-disk state that matters operationally even if it is not a general database

If `0.1` cannot survive those five, the vocabulary is still too narrow.

## Adoption staircase

Do not require the ecosystem to jump to deep automatic inference at once.

### Stage 1 — inventory and annotate
- generate a starter pack
- let maintainers mark surface names and contract levels

### Stage 2 — import obvious hints
- serde policy hints
- stable-wire adapters
- file/store write-path declarations

### Stage 3 — local checks and doctor warnings
- catch narrowed compatibility and overclaimed recovery
- keep manual-review zones explicit

### Stage 4 — release diffs
- compare current release versus previous release
- make durable-byte regressions visible in review

### Stage 5 — docs/review export
- stable summary and bundle output for release review, support docs, and operator handoff

## What should wait until later

Leave these for later unless `0.1` proves cramped without them:

- a generic crash-consistency lab that tries to model every filesystem and power-failure edge
- full automated inference of durability from arbitrary code paths
- registry-wide scraping of all crates
- hosted schema registries or migration services
- deep IDE/editor integrations
- broad domain-specific format adapters before the core contract vocabulary is trusted
