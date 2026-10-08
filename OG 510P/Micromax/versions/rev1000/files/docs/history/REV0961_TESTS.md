# Revision 0961 validation

Rev0961 was accepted through bounded executable slices around the changed trust,
worker, lifecycle, and screen-model seams. No complete full-suite claim is made.
The groups below can overlap and must not be added into one synthetic total.

## Final acceptance slices

- Exact-byte activation/reload, stale-grant invalidation, lexical snapshot
  containment after symlink retarget, package budgets, queue receive-before-join,
  broken-result teardown, and the complete restricted user journey: **15 passed**.
- Zero-origin flattened screen models plus the real ruler/cursorline/curses
  consumers and selected shared-screen composition/rendering seams: **20 passed**.
- Repository guardrails for audit metrics, context lineage, revision-index shape,
  living-document hygiene, and the generated effect/resource contract: **18
  passed** in split bounded runs.
- Revision packaging source snapshot, embedded context, archive verification CLI,
  verified-byte copying, and mutation refusal: **6 passed**.

## Broader focused regression evidence

- Changed restricted-plugin snapshot/journey/worker surfaces: **44 passed**.
- Plugin containment, callback rollback, and reload recovery: **78 passed**.
- Runtime-group transactions and registration ownership: **94 passed**.
- The default `make test` route exercised `tests/test_plugin_package_snapshots.py`
  through the process-group-aware runner: **8 passed**.

## Repository checks

- `bash scripts/lint.sh`: **ok**.
- `python tools/mxaudit.py --check`: **ok**.
- `python tools/mxeffects.py --check`: **ok**.
- `python tools/mxcontext.py --check`: **ok** after the final context refresh.
- `bash scripts/typecheck.sh`: mypy is unavailable in the offline environment,
  so the repository script reported its documented skip rather than a pass.

## Honest limits

A complete current suite was not demonstrated. Oversized combined batches and a
whole `test_editor_screen_layout.py` attempt met the cloud command ceiling under
concurrent worktree CPU load. Focused `tools/mxtest.py` batches completed cleanly,
and its process-group boundary removed active pytest descendants when a bounded
run was interrupted. Archive creation and verification are performed only after
source cleanup and the final context refresh.
