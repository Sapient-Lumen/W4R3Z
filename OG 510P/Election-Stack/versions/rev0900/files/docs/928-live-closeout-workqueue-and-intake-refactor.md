# 928 — Live-closeout workqueue and intake refactor

**Track:** A / deployable core

## What changed

v890 converts the v889 mission-kernel blocker list into a generated live-closeout workqueue:

- `tools/mission_kernel_live_workqueue.py`
- `scripts/check_mission_kernel_live_workqueue.py`
- `schemas/MissionKernelLiveWorkqueue.json`
- `artifacts/examples/example_county_2026_municipal_pilot/live-closeout-workqueue.json`
- `artifacts/examples/example_county_2026_municipal_pilot/live-closeout-workqueue.csv`
- `artifacts/examples/example_county_2026_municipal_pilot/live-closeout-intake-template.json`
- `artifacts/examples/example_county_2026_municipal_pilot/public-live-closeout-workqueue.md`
- `artifacts/reports/mission-kernel-live-workqueue-rev0890.json`

The queue remains `NO_GO_LIVE_CLOSEOUT_EVIDENCE_INCOMPLETE`. It does not close a live-pilot gate. It tells an operator exactly what evidence must be collected before a real jurisdictional closeout can be claimed.

## Why this matters

The riskiest incomplete path is no longer identifying that local authority, custody, export replay, audit/adjudication, independent review, public approval, and incident/remedy evidence are missing. That was done in v889. The next risk is that those blockers remain passive prose and nobody has a concrete collection surface.

The workqueue makes each blocker an intake row with:

- owner role;
- priority;
- kernel element link;
- missing evidence statement;
- minimum evidence classes;
- standards or operating alignment;
- first operator action;
- closure test; and
- non-claim boundary.

## Refactor performed

The workqueue is generated from `tools/mission_kernel_closeout.py` by calling `build_closeout()` instead of retyping the blocker list in another file. The new gate asserts that the generated queue contains seven blocker-derived rows, five critical rows, two high rows, no `TBD` owner, no filled live evidence digests, and no live-readiness overclaim.

A smaller hygiene fix also removed a duplicated `shared_helper` key in the closeout refactor-audit dictionary.

## External operating anchors

The live-closeout queue is intentionally an evidence-sidecar and supporting-technology workflow, not a substitute voting-system certification claim. Keep that boundary aligned with EAC supporting-technology lanes (`xref: eac_estep_program_page`) while using CISA cross-sector Cybersecurity Performance Goals as an operational baseline overlay for live intake, custody, and publication controls (`xref: cisa_cross_sector_cpgs_page`, `xref: cisa_cpg_2_0_pdf`).

## Operator rule

Do not close a workqueue item from narrative summaries, synthetic artifacts, or self-attestation. Close only from digest-bound local evidence with an approving role, redaction/public-boundary decision, and retention/disposition record.

## Boundary

This revision adds executable intake structure. It does not add local jurisdiction evidence, does not prove any outcome, does not certify a system, does not authorize public voter-facing release, does not provide legal advice, and does not replace canvass, audit, certification, recount, statutory retention, public-records, or court process.
