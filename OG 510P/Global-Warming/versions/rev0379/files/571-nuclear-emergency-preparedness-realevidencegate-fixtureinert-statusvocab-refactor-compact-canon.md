# 571 — Nuclear emergency preparedness: real evidence gate, inert fixture refactor, and validation status vocabulary

Revision: **rev0364**  
Base: **rev0363**  
Status: P0 evidence-path hardening, safe package refactor, and validator-report truthfulness upgrade. Public-context-only; no real-site readiness claim.

## Why this revision exists

Rev0363 fixed a false-green validator path. Rev0364 turns that fix into forward motion on the highest-risk incomplete work: the cube still lacks the **real or lawfully anonymized exercise evidence packet** needed to say anything stronger than capture-ready / claim-frozen / public-context-only.

This revision does three concrete things instead of expanding doctrine:

1. It creates a **real evidence critical path** for the Beaver Valley June 2026 exercise window: exactly what must be captured, how it should be accepted, and what remains blocked until the packet exists.
2. It makes a **safe fixture refactor**: actual `.exe`, `.vbs`, `.ps1`, `.docm`, `.xlsm`, `.lnk`, `.eml`, `.msg`, and `.7z` fixture files have been renamed to inert `.fixture.txt` paths with byte hashes preserved. Historical rev0356 CSVs retain the original observed filenames; the rev0364 map is the translation layer.
3. It replaces plain validation `pass` language in the current report with an explicit status vocabulary: `executed_pass`, `executed_fail`, `static_pass`, `info`, and `pending`.

## P0 rule

A public exercise notice, public meeting notice, exercise schedule, source register row, source alias, generated validator fixture, historical scanner result, zip manifest, or preliminary finding clock can route evidence collection. It cannot close readiness.

Readiness remains blocked until the cube contains a real or lawfully anonymized packet with dated artifacts, custodians, hashes, evaluator/provenance context, open-deficiency status, and corrective-action/retest disposition.

## What changed materially

### Evidence gate

`cube/nuclear-emergency-bvps-real-evidence-critical-path-rev0364.csv` is now the action surface. It names the workstreams most likely to be missed: preliminary findings and AAR/IP, alert and notification evidence, protective-action/dose timeline, AFN transportation, EOC/EOF/JIC operations, reception/decontamination, field monitoring, medical/EMS, county/ORO participation, public communications, corrective-action closure, and source/authority boundary controls.

`cube/nuclear-emergency-bvps-evidence-request-packet-rev0364.csv` converts those gaps into concrete requests. The acceptance tests are deliberately plain: artifact exists, source and custodian are named, timestamp and hash are recorded, scope limits are stated, and unresolved deficiencies remain open rather than being turned into narrative confidence.

### Source cluster weighting

`cube/nuclear-emergency-bvps-source-cluster-weighted-proof-register-rev0364.csv` records the raw source ID count separately from canonical cluster count. Duplicate source IDs for the same URL may show review history, but they do not create independent corroboration.

### Fixture inerting

`cube/nuclear-emergency-bvps-fixture-inert-rename-map-rev0364.csv` records every actual risky-extension fixture renamed to an inert marker path. The validator checks the filesystem, not just tables: there should be no actual shipped fixture files with executable-looking, macro-enabled, link, email-export, or `.7z` names.

### Validation vocabulary

`cube/validation-report-status-vocabulary-rev0364.csv` defines the only statuses allowed for current validation reports. The rev0364 report uses these statuses and a validator enforces them. Plain `pass` is no longer accepted for the current report because it hides whether a check was executed, static, informational, or still pending.

## Current non-closure state

The cube is better after rev0364, but the high-stakes truth is unchanged: it is still **not** a Beaver Valley readiness proof. It is now a more useful machine for preventing false closure and for capturing the first real evidence packet without losing chain-of-custody, source independence, or claim boundaries.
