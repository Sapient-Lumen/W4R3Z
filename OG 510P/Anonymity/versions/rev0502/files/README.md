# Anonymity Repository Operator Guide

This repository contains an active research program plus a slow publication surface.

## Start here in a fresh turn

Read these files in order:

1. `VERSION`
2. `START_HERE.md`
3. `CONTEXT_PACK.json`
4. `README.md`
5. `PUBLISHING.md`
6. `publishing/OPERATOR_STARTUP.md`
7. `publishing/CANONICAL_POLICY.json`
8. `publishing/CONTROL_SURFACES.md`
9. `published/LEGACY_PUBLISHED_LINKS.md`
10. `published/PUBLICATION_CLASSIFICATION.md`
11. `published/CITATION_HEADS.md`
12. `release_queue/QUEUE_INDEX.json`
13. `release_queue/REVIEW_INVENTORY.md`
14. `publishing/FAMILY_TRIAGE.md`
15. `release_queue/STATUS.md`
16. `release_queue/LATEST_DECISION.md`
17. `reports/archive_surface_coherence.json`
18. `reports/context_pack_contract.json`
19. `reports/transient_surface_audit.json`
20. `reports/manifest_sha256_verification.json`
21. `reports/manifest_coverage_audit.json`
22. `reports/lifecycle_gate_status.json`

A future LLM-in-charge should be able to wake up, read only those files, and avoid the most serious mistakes. `START_HERE.md` is the shortest human-facing path; `CONTEXT_PACK.json` is the shortest machine-facing one; `reports/lifecycle_gate_status.json` is the shortest stage-aware answer to which compact surface matters right now.

## Two publication regimes coexist here

### Legacy published work

The older already-published work uses **Mathematics** titles and legacy wiki links.
Those links are already public and must remain valid.
Do **not** casually rename, normalize, or overwrite them.
See `published/LEGACY_PUBLISHED_LINKS.md` for the exact canonical set.

### New published work

All **new** releases must use the new naming rule:

`YYYY.MM.DD - Anonymity: The Foobar Title Goes Here Please`

with wiki links of the form:

`[[YYYY.MM.DD - Anonymity: The Foobar Title Goes Here Please]]`

## Release posture

This repository is intentionally conservative.
A good turn often records **no release**.
The release queue should remain small, explicit, and slow-moving.

## Canonical directories for publishing work

- `published/` — already frozen public papers
- `release_queue/candidates/` — under conservative review
- `release_queue/hold/` — explicitly not ready
- `release_queue/published_ready/` — passed review, waiting for a release slot
- `release_queue/decisions/` — timestamped written decisions

## Paper-family umbrella

The moving paper families now live under `series/` rather than as many top-level siblings.
This keeps the shipped root smaller and makes the repo more clearly series-first while leaving `published/`, `publishing/`, and `release_queue/` visible at top level.

## Generated / non-canonical repo surfaces

- `build/` — transient review renders and compile byproducts that should not clutter the repo root
- `reports/` — persistent generated review reports and preflight summaries
- `index/` — generated series-index source/output

The moving paper source trees now live under `series/`; the generated directories above are convenience / audit surfaces only.

## Important defaults

- Default decision: **do not publish yet**.
- New releases use **Anonymity**, not **Mathematics**.
- Old Mathematics links remain canonical for the already-published work.
- The canonical published artifact is the `.tex` file.

## Extra orientation surfaces

- `published/PUBLICATION_CLASSIFICATION.md` — separates canonical public links from merely frozen in-repo files.
- `published/CITATION_HEADS.md` — compact answer to “what may be cited right now?”.
- `published/PUBLIC_SURFACE.json` — machine-readable description of the stable published-facing surface.
- `release_queue/QUEUE_INDEX.json` — machine-readable queue-state summary.
- `release_queue/LATEST_DECISION.json` — machine-readable latest decision summary.
- `release_queue/DECISION_INDEX.json` — machine-readable decision history.
- `release_queue/REVIEW_INVENTORY.md` — the reviewable paper universe.
- `publishing/FAMILY_TRIAGE.md` — coarse low-regret vs high-churn family map.
- `publishing/REVIEW_ORDER.md` — where to spend attention first.
- `publishing/CONTROL_SURFACES.md` — question-to-file crosswalk for wake-up and reentry.
- `ARCHIVE_INDEX.md` — compact recent revision index for archive-shape/control-surface passes.
- `TRANSFER_SOURCES.md` / `TRANSFER_SOURCES.json` / `TRANSFER_INPUTS.sha256` — exact compared-datacube input provenance for transfer-review turns.
- `ASSURANCE_ARTIFACTS.md` / `ASSURANCE_ARTIFACTS.json` — grouped catalog of trust / integrity / drift / provenance surfaces.

## Root-hygiene rule

Keep the shipped root small.
Do not leave new `_renders*` directories, loose render PNGs, root-level `paper.*` LaTeX byproducts, or ad hoc preflight JSONs at top level.
Move generated artifacts into `build/`, `reports/`, or `index/` instead.

## Integrity / reentry receipts

- `VERSION` — one-line revision identity for quick reentry and consistency checks.
- `START_HERE.md` — shortest human-facing reentry path.
- `CONTEXT_PACK.json` — machine-readable must-read set, quick checks, and current posture.
- `RELEASE_MANIFEST.json` — self-description of the intended bundle name, revision, timestamp, and slug.
- `REVISION_RECEIPT.json` — compact summary of what changed in this revision and why.
- `reports/archive_surface_coherence.json` — latest machine-generated agreement check across revision, queue, citation, public-surface, decision-surface, context-pack-contract, and manifest-coverage state.
- `reports/context_pack_contract.json` — machine-generated validation that the compact reentry packet is structurally complete and points only at real control surfaces.
- `reports/transient_surface_audit.json` — machine-generated audit for disallowed transient build artifacts in the shipped archive.
- `reports/manifest_sha256_verification.json` — machine-generated verification that every listed checksum still matches its file.
- `reports/manifest_coverage_audit.json` — machine-generated audit that every shipped file is either listed in `MANIFEST.sha256` or explicitly allowed as unlisted.
- `reports/transfer_source_receipt.json` — machine-generated check that compared-bundle provenance and the transfer ledger agree.
- `MANIFEST.sha256` — exact file-level checksums for the shipped archive.
- `ARCHIVE_INDEX.md` / `ARCHIVE_INDEX.json` — compact recent revision index for archive reentry.
- `PRUNING_POLICY.md` / `PRUNED_TRANSIENT.paths` — explicit archive-pruning rules plus the log of intentionally removed transient files.


## Compact machine surfaces

The repo now separates three different trust questions:

- structural well-formedness: `schemas/README.md` -> `reports/surface_schema_validation.json`,
- semantic invariants: `publishing/ARCHIVE_INVARIANTS.md` -> `reports/archive_invariants.json`,
- cross-surface agreement: `reports/archive_surface_coherence.json`.


Queue-facing markdown under `release_queue/` is now regenerated from compact machine state using `publishing/render_queue_surfaces.py`; prefer rerendering over hand-editing those summaries.

- `reports/context_pack_budget.json` for compact reentry-pack size discipline
- `reports/archive_budget.json` for archive-size / file-count / shipped-review-render hygiene
