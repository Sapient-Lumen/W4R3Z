# Lint idempotence audit

This generated surface exposes validation-side effects so a green lint cannot silently rewrite release provenance, repair generated surfaces in place, or leave transient bytecode artifacts.

- Revision: `rev0374`
- Bundle: `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`
- Resolved question: `OQ-0265`
- Live successor: `OQ-0266`
- Failures: `0`

## Non-claim
lint-idempotence-court, provenance-sovereign, generator-authority-board, bytecode-tribunal, clean-extraction-notary, release-provenance-court, mutation-waiver-senate, and idempotence-certification-authority are forbidden; this audit blocks validation side effects and release-provenance drift, but it does not certify semantic truth, legal status, minimality, or continuation authority.

## Rows
- `RELEASE-PROVENANCE.json#generator` — expected `tools/package_release.py`, observed `tools/package_release.py`: `pass`
- `RELEASE-PROVENANCE.json#command` — expected `make package-release STAMP=2026.06.16.13.45 SLUG=preanswerclamp-scoretime-leakcut`, observed `make package-release STAMP=2026.06.16.13.45 SLUG=preanswerclamp-scoretime-leakcut`: `pass`
- `tools/gen_release_integrity.py#write_release_integrity_call` — expected `canonical package provenance`, observed `canonical package provenance`: `pass`
- `tools/release_integrity_lib.py#canonical_package_command` — expected `present`, observed `present`: `pass`
- `Makefile#PYTHON` — expected `PYTHONDONTWRITEBYTECODE=1`, observed `PYTHONDONTWRITEBYTECODE=1`: `pass`
- `tools/run_lint_suite.py#sys.dont_write_bytecode` — expected `True`, observed `True`: `pass`
- `tools/generated_surface_lib.py#generated_surface_drift.validation_mode` — expected `temporary-copy-read-only-target`, observed `temporary-copy-read-only-target`: `pass`
- `tools/check_generated_surface_nonmutation_canary.py#validation_toolchain_membership` — expected `True`, observed `True`: `pass`
- `worktree#bytecode_artifacts` — expected `[]`, observed `[]`: `pass`

## Repaired findings
- `rev0329-lint-mutates-release-provenance` — A clean rev0329 extraction could pass make lint while rewriting RELEASE-PROVENANCE.json from tools/package_release.py to tools/gen_release_integrity.py. Repair: rev0330 makes gen_release_integrity emit canonical package provenance derived from RELEASE-MANIFEST.json, so lint regeneration and package-release provenance agree.
- `rev0329-lint-bytecode-side-effect` — A clean rev0329 make lint invocation left tools/__pycache__ bytecode artifacts even though release hygiene excluded them from packaging. Repair: rev0330 sets PYTHONDONTWRITEBYTECODE=1 in the Makefile and sets sys.dont_write_bytecode before the lint wrapper imports helper modules.

## Scan policy
- Scope: release provenance generator/command stability, read-only generated-surface drift detection, lint bytecode side effects, and integrity-regeneration routing
- Repair: fail closed on validation-side mutation; repair lint/package helper behavior instead of treating a green lint count as evidence that no files changed
- Boundary: idempotence evidence is operational hygiene only, not a proof of semantic correctness, canon sufficiency, or release legitimacy
