# Cargo lock-contention witness — lock-mode and mitigation-outcome plan (2026-03-22)

## Main judgment

**P-0490 Cargo Lock Contention Witness Kit** is strongest when it models three receiver-facing truths separately:

1. **package-cache lock mode**,
2. **residual contention after mitigation**,
3. **before/after mitigation outcome**.

That is the missing layer above today’s Cargo/rust-analyzer substrate.

## Why these artifacts matter now

Current official docs now make the sharper gap unusually concrete.

### 1. Package cache is not one undifferentiated lock story

Cargo’s current internal `cache_lock` docs now spell out three lock classes:

- `DownloadExclusive`
- `Shared`
- `MutateExclusive`

They also say `DownloadExclusive` does **not** interfere with `Shared`, while `MutateExclusive` acquires both underlying locks and should block readers.

That means a serious witness bundle should not say only “package cache lock”.
It should say which package-cache lock mode was relevant and how exact that classification is.

### 2. A mitigation can help and still leave residual contention

The Cargo 1.94 development-cycle update says that even after recent locking work, there are still easy-to-overlook but significant contention cases:

- `cargo clippy` can still contend on non-workspace members,
- `cargo check` versus `cargo test` can still contend around proc-macros and build scripts,
- and upstream locking/layout work is still in flight.

That means “set a different target dir” or “split build-dir” is not an honest universal success verdict.
A witness bundle should say what **residual contention surfaces** remain.

### 3. The bundle needs a stable before/after contract

rust-analyzer’s `cargo.targetDir` setting may prevent one build-lock / `Cargo.lock` symptom but duplicate artifacts.
A build-dir change may alter route topology without removing package-cache serialization.
A future layout or locking change may improve one collision class and leave another untouched.

So the crate needs one stable before/after artifact to answer:

- what changed,
- what did not,
- whether only confidence changed,
- whether only artifact duplication changed,
- and whether the original contention class actually moved.

## Receiver-facing artifacts to freeze next

### `package-cache-lock-mode.receipt.json`

Purpose: record which package-cache lock mode was relevant to the witness.

Minimum fields:
- workspace / machine / toolchain context
- actor
- lock mode (`download_exclusive`, `shared_read`, `mutate_exclusive`, `unknown`)
- evidence source (`stderr`, imported session, config+command inference, internal adapter, manual note)
- interference expectation (`non_interfering_with_shared`, `blocks_shared`, `blocks_download`, `manual_review_required`)
- exactness class
- older-cargo-compat caveat when relevant

### `residual-contention.report.json`

Purpose: record what contention surfaces remain after a mitigation or topology change.

Minimum fields:
- baseline bundle reference
- current bundle reference
- residual classes (`package_cache_serialization`, `proc_macro_build_script_overlap`, `non_workspace_member_lock_overlap`, `wrapper_hash_split_cost_only`, `upstream_locking_unknown`, `manual_review_required`)
- whether the original wait class moved, narrowed, disappeared, or became ambiguous
- supporting facts
- manual-review flag

### `mitigation-outcome.diff.json`

Purpose: compare two contention witnesses conservatively.

Minimum fields:
- before bundle reference
- after bundle reference
- changed roots
- changed lock mode
- changed wait class
- changed residual surfaces
- duplication/cost delta
- outcome class (`resolved_same_class`, `moved_to_new_class`, `reduced_wait_same_class`, `artifact_duplication_without_clear_resolution`, `confidence_only_change`, `manual_review_required`)

## Suggested scenario families

1. **download-exclusive package fetch alongside shared build**
   - same package cache root
   - should *not* be described as direct interference with a shared-read build lane

2. **cache GC mutate-exclusive blocks ordinary build**
   - proves package-cache lock mode matters more than merely “same cache root”

3. **separate target dir but residual proc-macro/build-script contention remains**
   - based on current Cargo 1.94 notes

4. **clippy non-workspace-member residual overlap**
   - shows that target-dir/workspace-member uniqueness is not a universal guarantee

5. **mitigation changed artifact duplication more than contention class**
   - honest before/after outcome for rust-analyzer-specific target-dir mitigation

## Guardrail

Do not let future P-0490 work collapse these into one fake “contention fixed” story:

1. same root,
2. conflicting lock mode,
3. residual contention,
4. artifact duplication cost,
5. before/after outcome.

A worthy crate here should hand another person all five truths separately.
