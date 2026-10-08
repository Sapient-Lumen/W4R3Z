# 563 — Nuclear emergency preparedness: forensic dropbox, intake CLI, and evidence-firewall refactor

Revision: **rev0356**  
Scope: **BVPS public-only first-drop intake operations; no real-site readiness claim**

## Purpose

Rev0355 created media quarantine folders and scan-gate concepts. Rev0356 makes the first-drop path executable: it adds a forensic dropbox CLI, a synthetic payload-like smoke test, a positive allow/hold/deny matrix, a custody-minimum event schema, hash indexing, quarantine routing, and no-auto-closure validation.

## Operational route

`external file or media drop → forensic dropbox CLI → hash and filetype classification → allow/hold/deny decision → custody minimum event → quarantine lane → candidate-for-adjudication only → CAP/retest/verifier if applicable → integrated claim-kernel release gate`

## Hard rule

A file, hash, scan pass, filetype decision, quarantine lane, redacted surrogate, public notice, preliminary finding, AAR paragraph, dashboard, PI page, MSEL event, source ID, duplicate URL, or complete-looking packet can demand, cap, route, contradict, or reopen a claim. It cannot automatically close local emergency-readiness evidence.

## Validator classes

The validator permits only:

- `rejected_closure_attempt`
- `hold_no_upgrade`
- `candidate_for_adjudication_not_closure`
- `accepted_reopen_signal`
- `context_no_upgrade`

There is no auto-close state.

## Caveat

The smoke-test files are synthetic dry-run artifacts. No real/anonymized June 2026 Beaver Valley exercise evidence has been imported.
