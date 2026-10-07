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
7. Read `publishing/REVIEW_ORDER.md`.
8. Read `release_queue/STATUS.md`.
9. Read `release_queue/LATEST_DECISION.md`.
10. Read `VERSION`, `reports/lifecycle_gate_status.json`, `reports/release_readiness_audit.json`, `reports/evidence_pack_audit.json`, `release_queue/NEXT_RELEASE_FREEZE_PLAN.md`, `reports/review_inventory_coverage.json`, `reports/review_inventory_integrity.json`, `reports/operator_command_hygiene.json`, and `reports/archive_surface_coherence.json`, `reports/manifest_canonicality.json`, `reports/freeze_warning_resolution.json`, `reports/toolchain_fingerprint.json` if you need a quick identity/stage/consistency check before trusting the compact surfaces.
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

If you need to check whether the compact surfaces still agree before digging deeper, read `reports/archive_surface_coherence.json`, `reports/manifest_canonicality.json`, `reports/freeze_warning_resolution.json`, `reports/toolchain_fingerprint.json`; if you just edited those surfaces, rerun `publishing/check_archive_coherence.py` before trusting them.
If you need to check bundle identity or the shipped bytes, read `VERSION`, `RELEASE_MANIFEST.json`, `REVISION_RECEIPT.json`, and `MANIFEST.sha256`.


## Reentry receipts

When a future turn needs to reorient quickly without crawling the whole repo, prefer these compact surfaces:

- `VERSION` and `RELEASE_MANIFEST.json` for bundle/revision identity,
- `REVISION_RECEIPT.json` for what this revision changed,
- `reports/archive_surface_coherence.json`, `reports/manifest_canonicality.json`, `reports/freeze_warning_resolution.json`, `reports/toolchain_fingerprint.json` for compact-surface agreement,
- `ARCHIVE_INDEX.md` for the recent revision sequence, and
- `MANIFEST.sha256` when exact shipped-file checksums matter.


## Fast reentry surfaces

When the goal is simply to regain bearings, start with `VERSION`, `START_HERE.md`, and `CONTEXT_PACK.json` before widening into the longer narrative docs.
If you need to trust the shipped bundle itself, also read `reports/archive_surface_coherence.json`, `reports/manifest_canonicality.json`, `reports/freeze_warning_resolution.json`, `reports/toolchain_fingerprint.json`, `reports/transient_surface_audit.json`, and `reports/manifest_sha256_verification.json`.


## Additional fail-closed trust checks

- `reports/context_pack_contract.json` should pass before trusting `CONTEXT_PACK.json` as the short machine reentry surface.
- `reports/manifest_coverage_audit.json` should pass before trusting `MANIFEST.sha256` as a complete map of the shipped bundle.
- `reports/release_readiness_audit.json`, `reports/evidence_pack_audit.json`, `release_queue/NEXT_RELEASE_FREEZE_PLAN.md`, `reports/review_inventory_coverage.json`, `reports/review_inventory_integrity.json`, and `reports/operator_command_hygiene.json` should pass before treating Published-ready as statically closed; they still do not authorize publication.
- `release_queue/LATEST_DECISION.json` and `release_queue/DECISION_INDEX.json` are the shortest machine-readable answers to “what happened recently?” and “what kinds of decisions have accumulated here?”.
- For exact spectral witnesses, run `python3 -B published/2026-01-23_spectral_anonymity/supplement/spectral_reconstruction.py --check-raw`, `--tail-sanity`, `--random-length-sanity`, `--ergodicity-floor-sanity`, and `--archive-guard`; fail closed on `chi2-general` unless it has direct t-step, ordered-product, hidden-length, Markov, Cantelli-with-certified-variance, evaluator-quantile, pointwise, or stronger tail/pointwise evidence.


## Rebuild path

When compact surfaces drift or feel stale, do not patch them one by one by hand first. Prefer `python3 -B publishing/rebuild_archive_surfaces.py --root .` or `make rebuild-surfaces`, which now also regenerates `release_queue/STATUS.md`, `release_queue/QUEUE.md`, and `release_queue/LATEST_DECISION.md` from machine state, then re-check `reports/archive_surface_coherence.json`, `reports/manifest_canonicality.json`, `reports/freeze_warning_resolution.json`, `reports/toolchain_fingerprint.json` and `reports/lifecycle_gate_status.json`.


## Structural contracts before action

Before trusting a machine-readable surface, check three different things in this order:

1. `reports/surface_schema_validation.json` — is the JSON well-formed against the intended contract?
2. `reports/archive_invariants.json` — are the archive's semantic truths still holding?
3. `reports/archive_surface_coherence.json`, `reports/manifest_canonicality.json`, `reports/freeze_warning_resolution.json`, `reports/toolchain_fingerprint.json` — do the compact surfaces agree with one another?
4. `reports/path_portability.json`, `reports/archive_packaging_reproducibility.json`, and `reports/json_surface_catalog.json` — is the archive shell safe to move, package, and parse?


Extra provenance / assurance helpers:

- `TRANSFER_SOURCES.md` / `TRANSFER_SOURCES.json` / `TRANSFER_INPUTS.sha256` — exact compared-datacube inputs for transfer-review passes.
- `ASSURANCE_ARTIFACTS.md` / `ASSURANCE_ARTIFACTS.json` — grouped catalog of trust / integrity / drift / provenance surfaces.

4. Run the trust stack if anything seems stale or surprising.
5. If `reports/archive_budget.json` fails, prune archive clutter before trusting the shipped bundle.

## rev0805 hardening checks

Before treating an artifact-governance paper as releaseable, run the stronger release lane rather than relying on queue state alone:

- `python3 -B publishing/check_release_readiness.py --root . --write-report reports/release_readiness_audit.json`
- `python3 -B publishing/check_review_inventory_integrity.py --root . --write-report reports/review_inventory_integrity.json`
- `python3 -B publishing/check_operator_command_hygiene.py --root . --write-report reports/operator_command_hygiene.json`
- `python3 -B publishing/check_support_manifest_integrity.py --root . --write-report reports/support_manifest_integrity.json`
- `python3 -B publishing/release_preflight.py --root . --date YYYY.MM.DD --title "Title Without Prefix" --source path/to/paper.tex --json`
- `python3 -B publishing/rebuild_archive_surfaces.py --root .`

For papers that make receipt, resolver, support-bundle, or artifact-governance claims, treat a minimal evidence pack as part of the public boundary. The evidence pack should include the relevant support manifest, artifact inventory, validation report, validator script, and any resolver map needed to reproduce the claim.


## Release-lane source-byte binding

Before freezing any Published-ready source, check that its queue note carries `Queue-bound source SHA-256` and that `reports/release_readiness_audit.json`, `reports/review_inventory_integrity.json`, `reports/operator_command_hygiene.json` reports zero missing or mismatched source-hash rows. A source edit after review is not silent: either refresh the queue-bound hash with a maintenance decision or move the item back for review.

Maintenance helper: after an intentional edit to a Candidate or Published-ready source, run `python3 -B publishing/refresh_queue_source_hashes.py --root .` and record why the queued source remains in that state. Then rerun `make verify-surfaces`.


## rev0808 evidence gate and freeze plan

Run `python3 -B publishing/check_review_inventory_coverage.py --root .`, `python3 -B publishing/check_evidence_pack_policy.py --root .`, and read `release_queue/NEXT_RELEASE_FREEZE_PLAN.md` before any release attempt. The plan is a dry-run pointer to the next low-friction source, not a publication authorization. Resolve the evidence-pack gate, clean compile gate, explicit decision gate, and metadata/provenance refresh gate before copying anything into `published/`.

## rev0810 freeze-packet and publication-boundary guard

After evidence and compile gates pass, inspect `reports/freeze_packet_integrity.json` before any publication execution. The selected Certified Menus target is staged in a non-public freeze packet, but it is still not a public citation head.

Before copying anything into `published/`, run `python3 -B publishing/check_publication_boundary.py --root .` and use the guarded `publishing/create_published_entry.py` arguments. A direct unguarded copy into `published/` is a policy failure even if the source compiles.

## rev0812 release-lane wake-up note

First read `reports/freeze_toolchain.json`, then `reports/freeze_compile_witness.json`. A source-bound carried-forward compile witness is acceptable archive evidence, but it does **not** close the current publication compile gate. The guarded helper requires `compile_gate_status=pass`, which means a current deterministic `SOURCE_DATE_EPOCH` compile witness exists.

Run `python3 -B publishing/check_freeze_toolchain.py --root .`, then `python3 -B publishing/build_freeze_compile_witness.py --root .`. In a TeX-equipped environment this should refresh the witness; without TeX it will carry forward the prior source-bound evidence and leave the gate pending. Read `reports/publication_rehearsal.json` before any publication decision.

For an actual publication decision, start from `release_queue/PUBLICATION_DECISION_TEMPLATE.md`; do not improvise the decision fields. The final zip should be produced through `make package`, not by an implicit manual zip command.


### rev0814 — rebuild fixed-point guard

The archive now includes `publishing/check_rebuild_fixed_point_coverage.py` and `reports/rebuild_fixed_point_coverage.json` so tail-mutated rebuild surfaces cannot escape the declared convergence target set. No publication was authorized.

## Publication-decision authorization scan

Before treating any decision note as authorizing publication, run:

``bash
python3 -B publishing/check_publication_decision_authorization.py --root . --write-report reports/publication_decision_authorization.json
python3 -B publishing/check_archive_index_integrity.py --root . --write-report reports/archive_index_integrity.json
``

## rev0823 source/command safety reminder

Before considering any publication action, check `reports/tex_source_safety.json`, `reports/secret_material_quarantine.json`, and `reports/makefile_target_integrity.json`. They are fail-closed blockers only; a clean result does not authorize publication.


## rev0824 guard note

Check `reports/manifest_canonicality.json`, `reports/freeze_warning_resolution.json`, and `reports/toolchain_fingerprint.json` before trusting a freeze packet or clean-compile witness. These reports are non-authorizing blockers only.


## rev0825 guard note

Run `python3 -B publishing/check_unicode_control_hygiene.py --root . --write-report reports/unicode_control_hygiene.json` if text surfaces have been edited outside the canonical rebuild. Any finding is publication-blocking and should be repaired before packaging.
