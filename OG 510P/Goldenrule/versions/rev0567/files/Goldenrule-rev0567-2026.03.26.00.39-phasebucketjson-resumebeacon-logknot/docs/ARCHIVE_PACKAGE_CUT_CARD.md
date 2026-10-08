# Archive Package Cut Card

Compact package-cut discipline for future inheritors: which package-boundary facts matter, which files to protect or trim first, and in what order to refresh the small archive-truth surfaces before cutting the next revision zip.

## Headline findings

- The live archive is still package-ready: package_boundary_ready=True with pdf_count=0 and scratch_file_count=0.
- The protected blocked-session handoff stack remains compact at 185 files and 1925278 raw bytes (1.836 MiB), so package dieting should not start there.
- The first safe diet pack still sits in 4 large markdown files and would recover 1398919 bytes (1.334 MiB) at a 128 KiB cap.
- The archive cut should treat `make test-quick` and `make test-full` as pre-size mutators because the harness records `artifacts/timing/env_<mode>.json` before the Rust lane.
- The minimal stable package-cut ritual is inventory writes first, then a two-pass `size -> triage -> size -> triage` refresh, then validator checks and only then the revision zip.
- The compact control stack now has a one-command integrity probe: `python3 scripts/tools/verify_archive_handoff_pack.py` checks every retained handoff-pack doc/report hash before you trust the blocked-session surface.
- The authoritative external winner now has a one-command verifier too: `python3 scripts/tools/verify_authoritative_archive_zip.py` proves that the winning sibling zip still exists and matches the live authority rule, selected path, and live bytes.
- The canonical one-command wrapper for that settle order is `make settle-archive-truth`, which tolerates the expected blocked Rust gate and then refreshes the package-cut, reentry, handoff-pack, revision-cut, zip-lineage, zip-chronology, zip-authority, zip-digest, and zip-size-truth cards after the size/triage fixed point.
- The normalized next-name planner is `python3 scripts/tools/plan_archive_revision_cut.py --descriptor your-summary-slug`, so the final root/zip stem does not need to be improvised by hand after the tree is settled.
- The canonical last-mile cutter is `python3 scripts/tools/cut_archive_revision.py --descriptor your-summary-slug --summary "one-line summary"`, which runs the settle wrapper, appends the next changelog stub, renames the archive root, refreshes the name-sensitive cards, and writes the zip.

## Canonical wrapper

- wrapper_command: `make settle-archive-truth`
- wrapper_role: run the mutating harness gate first, settle the inventory and size/triage fixed point, then refresh the package-cut, reentry, revision-cut, zip-lineage, zip-chronology, and zip-authority cards before final validation.
- revision_planner_command: `python3 scripts/tools/plan_archive_revision_cut.py --descriptor your-summary-slug`
- canonical_cut_command: `python3 scripts/tools/cut_archive_revision.py --descriptor your-summary-slug --summary "one-line summary"`

## Current package boundary

- retained_file_count: `2081`
- raw_bytes: `15798342` (15.066 MiB)
- approx_revision_zip_bytes: `4343060` (4.142 MiB)
- package_boundary_ready: `True`
- pdf_count: `0`
- scratch_file_count: `0`

## Protect first, trim second

- protected_stack_files: `185`
- protected_stack_raw_bytes: `1925278` (1.836 MiB)
- cap_first_pack_files: `4`
- cap_first_pack_recoverable_bytes_at_128k: `1398919` (1.334 MiB)

Cap-first markdown pack:

- `docs/AGENT_LOG.md`
- `CHANGELOG.md`
- `docs/RESEARCH_SOURCES.md`
- `artifacts/process/2026-03-21-research-pass.md`

## Live mutators that must run before the final size refresh

- `make test-quick` -> `artifacts/timing/env_quick.json`: scripts/test/run_harness.sh records env metadata before the Rust lane and can therefore perturb the retained tree even when the Rust step fails.
- `make test-full` -> `artifacts/timing/env_full.json`: the same harness records a full-mode env receipt before the slower test ladder continues, so full-mode gates also belong before the final package-boundary size refresh.

## Stable package-cut refresh order

1. `make test-quick` — Run any live mutating gate first so env/timing receipts land before the final package-boundary size snapshot.
2. `make update-command-inventory` — Refresh the command inventory before any size-sensitive package cards read the tree.
3. `make update-validator-inventory` — Refresh the validator inventory before any size-sensitive package cards read the tree.
4. `make update-artifact-buckets` — Refresh the artifact bucket summary before the package-boundary cards measure the live retained tree.
5. `make update-archive-size-guardrail-card` — Take a first live package-boundary size snapshot after the inventory writes have settled.
6. `make update-archive-byte-triage-card` — Refresh the protect-versus-trim card from the new size snapshot.
7. `make update-archive-size-guardrail-card` — Re-take the size snapshot after the triage card itself has rewritten retained files.
8. `make update-archive-byte-triage-card` — Reconfirm the trim-first pack against the final post-guardrail tree; this second pair is the fixed-point pass.
9. `make update-archive-package-cut-card` — Refresh the package-cut card itself from the settled size and triage surfaces.
10. `make update-archive-reentry-card` — Refresh the role-annotated head pointer after the package boundary and comeback surfaces have settled.
11. `make update-archive-handoff-pack` — Refresh the hash-bearing blocked-session control-plane pack after the reentry, comeback, package, and external zip surfaces have settled.
12. `make update-archive-revision-cut-card` — Refresh the normalized next-name card from the settled package boundary and current head.
13. `make update-archive-zip-lineage-card` — Refresh the sibling-zip audit card so the external package lane is checked against the settled current head before the cut.
14. `make update-archive-zip-chronology-card` — Refresh the sibling-zip chronology card so timestamp regressions across revision labels stay visible before the cut.
15. `make update-archive-zip-authority-card` — Refresh the exact sibling-zip reopen target after the lineage and chronology cards have settled.
16. `make update-archive-zip-digest-card` — Refresh the authoritative sibling-zip digest card so the winning external package bytes stay directly verifiable before the cut.
17. `make update-archive-zip-size-truth-card` — Refresh the zip-size truth card so the internal proxy is not mistaken for the final sibling zip bytes.
18. `make test-archive-size-guardrail-card && make test-archive-byte-triage-card && make test-archive-package-cut-card && make test-archive-reentry-card && make test-archive-handoff-pack && make test-archive-handoff-pack-verify-tool && make test-authoritative-archive-zip-verify-tool && make test-archive-revision-cut-card && make test-archive-zip-lineage-card && make test-archive-zip-chronology-card && make test-archive-zip-authority-card && make test-archive-zip-digest-card && make test-archive-zip-size-truth-card` — Verify that the package-boundary, head-pointer, hash-bearing handoff pack, naming, sibling-zip audit, sibling-zip chronology, exact sibling-zip authority card, authoritative sibling-zip digest card, and zip-size truth card all match the settled tree before cutting the revision zip.

## Settle rule

- After the first inventory writes and the first package-card pass, rerun size and triage one more time. Cut the revision zip only after both package-card validators pass on that post-second-pass tree.
- Fixed-point pair:
  - `make update-archive-size-guardrail-card`
  - `make update-archive-byte-triage-card`
- Final validation commands:
  - `make test-archive-size-guardrail-card`
  - `make test-archive-byte-triage-card`
  - `make test-archive-package-cut-card`
  - `make test-archive-reentry-card`
  - `make test-archive-handoff-pack`
  - `make test-archive-handoff-pack-verify-tool`
  - `make test-authoritative-archive-zip-verify-tool`
  - `make test-archive-revision-cut-card`
  - `make test-archive-zip-lineage-card`
  - `make test-archive-zip-chronology-card`
  - `make test-archive-zip-authority-card`
  - `make test-archive-zip-digest-card`
  - `make test-archive-zip-size-truth-card`

## Guardrails

- Run any mutating harness gate (`make test-quick` or `make test-full`) before the final package-boundary refresh; otherwise the env receipt can stale the size card after you thought the tree was settled.
- Prefer `make settle-archive-truth` when you want the whole package-boundary truth surface settled from one command instead of retyping the ritual by hand.
- Run `python3 scripts/tools/verify_archive_handoff_pack.py` when you want the compact blocked-session control stack verified from one command before reopening neighboring docs.
- Run `python3 scripts/tools/verify_authoritative_archive_zip.py` when you want the external winning zip proved from one command before trusting the selected sibling package bytes.
- Use `python3 scripts/tools/plan_archive_revision_cut.py --descriptor your-summary-slug` immediately after the settle pass when you need the exact normalized next root/zip stem for the new revision.
- Prefer `python3 scripts/tools/cut_archive_revision.py --descriptor your-summary-slug --summary "one-line summary"` when you want the final rename/changelog/zip step executed from one command instead of stitching the last mile together by hand.
- Check the sibling zip lane after the cut so duplicate revision labels, missing current-root zips, revision/timestamp chronology inversions, and proxy-vs-exact zip-size confusion are caught from files on disk rather than inferred later from chat history.
- Treat the second `update-archive-size-guardrail-card` + `update-archive-byte-triage-card` pair as the fixed-point pass, not as redundant ceremony.
- If the archive needs bytes before a cut, condense the cap-first markdown pack before touching the protected Rust/cloudtainer/archive-size/package-cut handoff stack.
- Keep the long-term package boundary PDF-free and scratch-free; reacquire any large external body only as temporary scratch and delete it before the final size/triage refresh.

## Source surfaces

- `artifacts/reports/archive_size_guardrail_card.json`
- `artifacts/reports/archive_byte_triage_card.json`
- `scripts/test/run_harness.sh`
- `scripts/report/build_archive_size_guardrail_card.py`
- `scripts/report/build_archive_byte_triage_card.py`
- `scripts/tools/settle_archive_truth.py`
- `scripts/tools/cut_archive_revision.py`
- `scripts/report/build_archive_handoff_pack.py`
- `scripts/test/check_archive_handoff_pack.py`
- `scripts/report/build_archive_zip_size_truth_card.py`
- `scripts/test/check_archive_zip_size_truth_card.py`
- `scripts/tools/verify_authoritative_archive_zip.py`
- `scripts/test/check_authoritative_archive_zip_verify_tool.py`
