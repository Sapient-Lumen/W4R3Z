# 2026-03-17 Research Pass

## What changed

- Added one compact rebuild audit for the standing rematch-world benchmark seed:
  - `schemas/rematch_world_benchmark_frozen_handoff_audit_receipt.schema.json`
  - `scripts/tools/audit_rematch_world_benchmark_frozen_handoffs.py`
  - `scripts/report/build_rematch_world_benchmark_frozen_handoff_audit_example.py`
  - `examples/snapshots/rematch_world_benchmark_frozen_handoff_audit_receipt.json`
  - `scripts/test/check_rematch_world_benchmark_frozen_handoff_audit.py`
  - `docs/LIBRARY/topics/standing_rematch_world_benchmark_seed_should_be_rebuild_audited_before_fill_work_begins.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` so fill work now starts from an explicitly rebuild-audited frozen seed rather than from visual trust in a large copied artifact.

## Main local result

- The standing seed currently rebuild-matches exactly (`seed_sha256 = rebuilt_seed_sha256 = 3e8e882161f779754d4cf52fabd801ec7854690b166f8563909190d061a917e7`).
- All `8` audited frozen sections exact-match their source artifacts (`7` copied handoffs + `1` compact decision bundle).
- The new retained receipt stays small and citation-first: it points back to `8` source artifacts instead of copying another large benchmark-facing note family into `artifacts/reports`.

## Inheritor guidance

- Rerun the frozen-handoff audit before any new world-dependent fill work whenever a copied handoff, the standing decision contract, or the seed builder changes.
- If the audit fails, rebuild the standing seed first; do not start fill work from a silently drifted baseline.
- Keep this as one durable audit receipt rather than widening the archive with more seed walkthroughs or duplicate snapshots.

## Additional pass: compiled-artifact copy-forward audit

- Added one compact copy-forward audit for filled rematch-world benchmark artifacts:
  - `schemas/rematch_world_benchmark_copy_forward_audit_receipt.schema.json`
  - `scripts/tools/audit_rematch_world_benchmark_copy_forward.py`
  - `scripts/report/build_rematch_world_benchmark_copy_forward_audit_example.py`
  - `examples/snapshots/rematch_world_benchmark_copy_forward_audit_receipt.json`
  - `scripts/test/check_rematch_world_benchmark_copy_forward_audit.py`
  - `docs/LIBRARY/topics/filled_rematch_world_benchmarks_should_carry_one_copy_forward_audit_receipt.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` so publication now carries one tiny proof that copied seed handoffs survived unchanged into the filled artifact.

## Additional local result

- The standing compiled benchmark artifact currently preserves all `8` copied frozen sections exactly (`7` copied handoffs from the seed + `1` compact decision bundle from the standing contract).
- The new receipt composes cleanly with the frozen seed audit instead of reprinting standalone source provenance again: it cites the seed audit receipt once and then only proves compiled-artifact continuity.

