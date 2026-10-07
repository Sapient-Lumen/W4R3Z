# Operator Startup for Future Turns

This file is for an LLM waking up with little or no short-term memory.

## Objective

Protect the integrity of the archive while allowing a gentle release queue.
The goal is **not** to release something every turn.
The goal is to make one cautious, well-recorded decision at a time.

## Five-minute wake-up path

1. Read `PUBLISHING.md`.
2. Read `published/LEGACY_PUBLISHED_LINKS.md`.
3. Read `published/PUBLICATION_CLASSIFICATION.md`.
4. Read `published/CITATION_HEADS.md`.
5. Read `release_queue/QUEUE_INDEX.json`.
6. Read `release_queue/REVIEW_INVENTORY.md`.
7. Read `publishing/FAMILY_TRIAGE.md`.
8. Read `release_queue/STATUS.md`.
9. Read `release_queue/LATEST_DECISION.md`.
10. Read `VERSION`, `reports/lifecycle_gate_status.json`, and `reports/archive_surface_coherence.json` if you need a quick identity/stage/consistency check before trusting the compact surfaces.
11. If the file set still feels wide, read `publishing/CONTROL_SURFACES.md` as the question-to-file crosswalk.
12. If you need to know why certain cross-datacube patterns already landed or were rejected, read `DATACUBE_TRANSFER_LEDGER.md`.
13. If needed, open the referenced full decision note in `release_queue/decisions/`.
14. Only then inspect candidate source papers.

## Non-negotiable facts

- The old already-published papers keep their **Mathematics** wiki links.
- New releases must use the **Anonymity** naming regime.
- A paper does not become published merely because it seems good.
- A paper becomes published only when a dated `.tex` freeze is placed in `published/` with the exact required name.

## What to avoid

Do not:

- rename old public links without an explicit migration plan,
- improvise a new naming scheme,
- publish directly from a moving draft,
- collapse multiple cautious steps into one irreversible jump,
- or assume that a sparse queue means something is wrong.

## What a successful turn can do

A successful turn may do any one of the following:

- improve documentation,
- add or refine a crosswalk,
- record a hold decision,
- create a candidate note,
- move one paper into `published_ready/`,
- or publish one already queued paper.

Zero publication actions is a normal and healthy outcome.

## Safe default after waking up

If the repo still feels confusing after those files, do **not** pick a paper at random.
Choose either a standalone-series paper from `release_queue/REVIEW_INVENTORY.md` or a family-level hold note for the late synthesis tail.


## Current repo shape

The moving paper-family trees now live under `series/`.
Do not reintroduce many top-level family directories unless there is a strong reason to break that umbrella.

## Repo hygiene while operating

Do not leave new root-level `_renders*` directories, loose render PNGs, root `paper.*` LaTeX byproducts, or generated preflight reports at top level.
Generated review surfaces belong in `build/`, `reports/`, or `index/`.

## Compact reentry receipts

If you need to check whether the compact surfaces still agree before digging deeper, read `reports/archive_surface_coherence.json`; if you just edited those surfaces, rerun `publishing/check_archive_coherence.py` before trusting them.
If you need to check bundle identity or the shipped bytes, read `VERSION`, `RELEASE_MANIFEST.json`, `REVISION_RECEIPT.json`, and `MANIFEST.sha256`.


## Reentry receipts

When a future turn needs to reorient quickly without crawling the whole repo, prefer these compact surfaces:

- `VERSION` and `RELEASE_MANIFEST.json` for bundle/revision identity,
- `REVISION_RECEIPT.json` for what this revision changed,
- `reports/archive_surface_coherence.json` for compact-surface agreement,
- `ARCHIVE_INDEX.md` for the recent revision sequence, and
- `MANIFEST.sha256` when exact shipped-file checksums matter.


## Fast reentry surfaces

When the goal is simply to regain bearings, start with `VERSION`, `START_HERE.md`, and `CONTEXT_PACK.json` before widening into the longer narrative docs.
If you need to trust the shipped bundle itself, also read `reports/archive_surface_coherence.json`, `reports/transient_surface_audit.json`, and `reports/manifest_sha256_verification.json`.


## Additional fail-closed trust checks

- `reports/context_pack_contract.json` should pass before trusting `CONTEXT_PACK.json` as the short machine reentry surface.
- `reports/manifest_coverage_audit.json` should pass before trusting `MANIFEST.sha256` as a complete map of the shipped bundle.
- `release_queue/LATEST_DECISION.json` and `release_queue/DECISION_INDEX.json` are the shortest machine-readable answers to “what happened recently?” and “what kinds of decisions have accumulated here?”.


## Rebuild path

When compact surfaces drift or feel stale, do not patch them one by one by hand first. Prefer `python3 publishing/rebuild_archive_surfaces.py --root .` or `make rebuild-surfaces`, which now also regenerates `release_queue/STATUS.md`, `release_queue/QUEUE.md`, and `release_queue/LATEST_DECISION.md` from machine state, then re-check `reports/archive_surface_coherence.json` and `reports/lifecycle_gate_status.json`.


## Structural contracts before action

Before trusting a machine-readable surface, check three different things in this order:

1. `reports/surface_schema_validation.json` — is the JSON well-formed against the intended contract?
2. `reports/archive_invariants.json` — are the archive's semantic truths still holding?
3. `reports/archive_surface_coherence.json` — do the compact surfaces agree with one another?


Extra provenance / assurance helpers:

- `TRANSFER_SOURCES.md` / `TRANSFER_SOURCES.json` / `TRANSFER_INPUTS.sha256` — exact compared-datacube inputs for transfer-review passes.
- `ASSURANCE_ARTIFACTS.md` / `ASSURANCE_ARTIFACTS.json` — grouped catalog of trust / integrity / drift / provenance surfaces.

4. Run the trust stack if anything seems stale or surprising.
5. If `reports/archive_budget.json` fails, prune archive clutter before trusting the shipped bundle.
