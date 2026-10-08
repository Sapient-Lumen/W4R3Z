# Cargo Lock Contention Witness Kit fixtures

This fixture family exists to make **P-0490 Cargo Lock Contention Witness Kit** more concrete.

The goal is to standardize a very small witness bundle for live blocking incidents:

- which cache/build root was involved,
- what wait was actually observed,
- how strong the observation was,
- and which mitigation trade-off is recommended next.

## Intended first scenarios

1. `shared_target_dir_editor_manual`
2. `package_cache_fetch_wait`
3. `separate_target_dir_mitigated`
4. `build_dir_separated_target_still_shared`
5. `wrapper_hash_split_same_target`
6. `imported_build_analysis_session_no_pid_certainty`
7. `build_dir_new_layout_probe_pending`
8. `manual_review_required`

## Minimal bundle for 0.1

- `cache-root.manifest.json`
- `root-sharing.report.json`
- `root-authority.receipt.json`
- `lock-wait.receipt.json`
- `actor-command-lane.receipt.json`
- `wait-window.receipt.json`
- `collision-diagnosis.report.json`
- `mitigation.plan.json`
- `mitigation-cost.report.json`
- `evidence-source.receipt.json`
- `exactness.report.json`
- optional `wrapper-context.receipt.json`
- optional `process-role.snapshot.json`
- optional `build-analysis-session.link.json`
- `contention-support-bundle.manifest.json`
- `notes.md`

Later overlays may add:
- `contention.diff.json`
- richer per-platform observation adapters
- longer-running correlation logs

## Design rule

This family should optimize for **small, reviewable support bundles** rather than giant process dumps.
If the crate cannot prove a specific blocker with high confidence, the artifact should say `manual_review_required` or `unknown_wait` instead of inventing precision it does not have.

## Current planning stance

This family is **not** trying to replace Cargo scheduling, rust-analyzer configuration, or Cargo cache internals.
It is trying to standardize the receiver-facing artifact those surfaces still do not hand people by default.

## 2026-03-16 implementation note

A session imported from Cargo build-analysis is **supporting context**, not blocker proof.
These fixtures should therefore keep three things distinct:

- the observed wait,
- the shared-root topology,
- and any imported session/report context.

If the fixture cannot prove blocker identity, `exactness.report.example.json` should say so explicitly.

## 2026-03-22 implementation note

This family should now keep five truths distinct:

- **root authority** — where the path claim came from,
- **actor command lane** — what the actor really ran,
- **wait window** — what time-bounded wait was observed,
- **mitigation cost** — what the workaround buys and costs,
- **bundle completeness** — which receipts are present and which still require manual review.

## 2026-03-22 refinement

This family should now keep eight truths distinct:

- **root authority** — where the path claim came from,
- **actor command lane** — what the actor really ran,
- **wait window** — what time-bounded wait was observed,
- **package-cache lock mode** — whether package-cache activity should actually conflict,
- **residual contention** — what still remains after the mitigation,
- **mitigation outcome** — what changed before vs after,
- **mitigation cost** — what the workaround buys and costs,
- **bundle completeness** — which receipts are present and which still require manual review.

Add scenario coverage for:
- non-interfering `DownloadExclusive` package-cache activity,
- `MutateExclusive` cache-GC blocking,
- residual proc-macro/build-script overlap after target-dir mitigation,
- and before/after outcome diffs where duplication clearly changed more than the proved contention class.
