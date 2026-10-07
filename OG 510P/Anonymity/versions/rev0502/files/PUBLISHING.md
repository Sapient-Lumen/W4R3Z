# Publishing and Release Governance

This repository now uses a **slow, conservative publication flow**.

The governing idea is simple:

- the research process may continue to evolve,
- but public releases must be frozen only when a draft has clearly stopped moving in substance,
- and the default decision is **do not publish yet**.

## Two naming regimes

This repository now distinguishes between:

- **legacy already-published work**, which keeps its existing **Mathematics** wiki links, and
- **new releases**, which must use the **Anonymity** naming regime.

The canonical legacy link set is recorded in `published/LEGACY_PUBLISHED_LINKS.md`.
Do not casually rename those old public links.

## What counts as published

For new releases, a paper counts as published only when it has been copied into `published/` under the exact wiki-facing naming convention:

`YYYY.MM.DD - Anonymity: The Foobar Title Goes Here Please`

For a published paper:

- the **directory name** must exactly match that format,
- the canonical `.tex` file inside that directory must have the **same basename**,
- all wiki references must target that basename in wikilink form, for example:
  - `[[YYYY.MM.DD - Anonymity: The Foobar Title Goes Here Please]]`

## Current policy

This repo is intentionally biased toward:

- delayed release,
- written release decisions,
- explicit hold decisions,
- small release queue movement,
- and reversible staging before irreversible public publication.

## Operator rule for future turns

A future LLM-in-charge should be allowed to spend many turns making **no release decision**.
A turn is successful if it makes the repository better structured, narrows uncertainty, records a hold, or advances one candidate by a single cautious step.

See:

- `publishing/OPERATOR_STARTUP.md`
- `publishing/RELEASE_FLOW.md`
- `publishing/CONSERVATIVE_RELEASE_POLICY.md`
- `publishing/TURN_DECISION_PROTOCOL.md`
- `published/LEGACY_PUBLISHED_LINKS.md`
- `release_queue/STATUS.md`
- `published/README.md`

## Additional control surfaces

For future cautious turns, also use:

- `published/PUBLICATION_CLASSIFICATION.md`
- `published/CITATION_HEADS.md`
- `published/PUBLIC_SURFACE.json`
- `release_queue/QUEUE_INDEX.json`
- `release_queue/LATEST_DECISION.json`
- `release_queue/DECISION_INDEX.md`
- `release_queue/DECISION_INDEX.json`
- `release_queue/REVIEW_INVENTORY.md`
- `publishing/FAMILY_TRIAGE.md`
- `publishing/REVIEW_ORDER.md`
- `publishing/REVIEW_RUBRIC.md`
- `VERSION`
- `START_HERE.md`
- `CONTEXT_PACK.json`
- `publishing/CONTROL_SURFACES.md`
- `publishing/control_surfaces.json`
- `publishing/build_decision_index.py`
- `publishing/check_archive_coherence.py`
- `publishing/check_context_pack_contract.py`
- `publishing/check_transient_surface.py`
- `publishing/verify_manifest_sha256.py`
- `publishing/check_manifest_coverage.py`
- `publishing/release_preflight.py`

## Paper-family layout

The moving paper-family trees now live under `series/`.
Keep new family-level source trees there rather than adding fresh top-level siblings.
The top level should preferentially expose only the public/archive surfaces (`published/`, `publishing/`, `release_queue/`) plus generated-audit homes (`build/`, `reports/`, `index/`).

## Repo-shape default

Keep generated artifacts out of the shipped root unless there is a strong reason otherwise.

Use:

- `build/` for transient compile outputs and render batches,
- `reports/` for persistent generated review/preflight reports, and
- `index/` for generated series-index source/output.


Additional operator helpers:

- `publishing/LIFECYCLE_GATES.md` / `reports/lifecycle_gate_status.json` answer which compact surface matters at each stage.
- `DATACUBE_TRANSFER_LEDGER.md` records which patterns from other datacubes were adopted or rejected.
- `publishing/rebuild_archive_surfaces.py` and `Makefile` provide a one-command rebuild/verification path for the compact surfaces.
- `TRANSFER_SOURCES.md` / `TRANSFER_SOURCES.json` / `TRANSFER_INPUTS.sha256` record the exact external datacube bundles reviewed during transfer passes.
- `ASSURANCE_ARTIFACTS.md` / `ASSURANCE_ARTIFACTS.json` group the trust surfaces so a future operator can inspect them as a set.


## Compact trust stack

Before relying on queue / citation / public-boundary JSON alone, check: `reports/surface_schema_validation.json`, `reports/archive_invariants.json`, `reports/archive_surface_coherence.json`, and only then the narrower audits like context-pack budget, manifest coverage, and transient-surface status.


Queue-facing markdown under `release_queue/` is now regenerated from compact machine state using `publishing/render_queue_surfaces.py`; prefer rerendering over hand-editing those summaries.

- Run the integrity and drift checks before any publication move.
- Treat shipped `series/.../renderNNN/` review-render directories as a packaging failure, not as moving-source truth.
