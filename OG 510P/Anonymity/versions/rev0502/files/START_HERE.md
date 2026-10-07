# Start Here

This is the shortest honest reentry path for a future operator.

Read in this order:

1. `VERSION`
2. `START_HERE.md`
3. `CONTEXT_PACK.json`
4. `README.md`
5. `PUBLISHING.md`
6. `publishing/OPERATOR_STARTUP.md`
7. `publishing/CANONICAL_POLICY.json`
8. `publishing/CONTROL_SURFACES.md`
9. `publishing/ARCHIVE_INVARIANTS.md`
10. `published/CITATION_HEADS.md`
11. `release_queue/QUEUE_INDEX.json`
12. `release_queue/LATEST_DECISION.md`
13. `reports/surface_schema_validation.json`
14. `reports/archive_invariants.json`
15. `reports/lifecycle_gate_status.json`
16. `reports/archive_surface_coherence.json`
17. `reports/context_pack_budget.json`
18. `TRANSFER_SOURCES.md`
19. `ASSURANCE_ARTIFACTS.md`

Cheap trust checks:

- `python3 publishing/rebuild_archive_surfaces.py --root .`
- `python3 publishing/check_surface_schemas.py --root . --write-report reports/surface_schema_validation.json`
- `python3 publishing/check_archive_invariants.py --root . --write-report reports/archive_invariants.json`
- `python3 publishing/check_archive_coherence.py --root . --write-report reports/archive_surface_coherence.json`
- `python3 publishing/check_context_pack_contract.py --root . --write-report reports/context_pack_contract.json`
- `python3 publishing/check_context_pack_budget.py --root . --write-report reports/context_pack_budget.json`
- `python3 publishing/check_transient_surface.py --root . --write-report reports/transient_surface_audit.json`
- `python3 publishing/verify_manifest_sha256.py --root . --write-report reports/manifest_sha256_verification.json`
- `python3 publishing/check_manifest_coverage.py --root . --write-report reports/manifest_coverage_audit.json`
- `python3 publishing/check_transfer_source_receipt.py --root . --write-report reports/transfer_source_receipt.json`
- `python3 publishing/build_lifecycle_gate_status.py --root . --write-report reports/lifecycle_gate_status.json`

Current posture:

- default decision remains **no publication**,
- the only approved public citation heads remain the five legacy Mathematics-era entries,
- no post-policy Anonymity paper has been published yet,
- the queue remains 6 Candidate / 22 Published-ready / 52 Hold,
- this revision tightens the replayable-verifier seam: Boss Fight~C now states the smallest fail-closed cutover between staying inside the declared public verifier-bundle card and silently reusing the same replayed $p\le d\le B$ numbers after checker-version or plan/dual-schema drift, and it adds an explicit reopen ladder into Boss Fight~A / Boss Fight~B / the Boss Fight~B addendum / Eval~1 / ABOM-OINL / Release~A while leaving publication state unchanged and keeping the note in Published-ready.

Generated queue surfaces (`release_queue/STATUS.md`, `release_queue/QUEUE.md`, and `release_queue/LATEST_DECISION.md`) should be treated as derived views of machine state, not hand-maintained prose; rerender them with `python3 publishing/render_queue_surfaces.py --root .` or `make rebuild-surfaces` when queue state changes.

- run the compact trust stack if the archive shape feels uncertain
- if `reports/archive_budget.json` fails, prune archive clutter before trusting the bundle
