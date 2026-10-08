# 583 — Nuclear emergency preparedness: ENS alias repair, normalized table rebuild, and dispatch cut sheet

Revision: rev0376  
Base: rev0375  
Status: canon  
Claim posture: current-plan terminology captured / ENS-IPAWS request lane sharpened / dispatch payloads made copy-pasteable / derived file-normalization layer rebuilt / claim-frozen / no local readiness conclusion

## Substance-first priority

Rev0376 works the riskiest unfinished branch in a more operational way: after the exercise-day public meetings, the package still has no official findings packet, no dispatch proof, and no response packet. The highest near-term risk is not another doctrine layer; it is sending imprecise requests or importing a response into stale derived tables that make the cube look more complete than it is.

The current Columbiana County Radiological Emergency Response Plan provides a concrete terminology correction. Its January 2026 Rev. 38 change log says WENS was removed and replaced with ENS, and its table of contents routes emergency notification through Emergency Notification Methods and Procedures, Public Warning, EAS Messages, and an ENS/IPAWS Concept of Operations. Rev0376 therefore adds an ENS/IPAWS alias gate so future request, search, and intake terms do not miss records by using old alert-system language only.

## Priority changes made

- Added `cube/bvps-columbiana-current-plan-gap-extraction-rev0376.csv` to convert current public-plan sections into proofcut-specific request targets without treating the plan as performance proof.
- Added `cube/bvps-ens-ipaws-terminology-alias-audit-rev0376.csv` so `WENS`, `ENS`, `IPAWS`, `EAS`, `WEA`, `siren`, and `public warning` become a controlled search/request alias set.
- Added two sharper ready-not-sent packets under `records-requests/bvps-rev0376/`:
  - `rrt-0376-009-columbiana-ema-ens-ipaws-current-plan-exercise-logs.md`
  - `rrt-0376-010-ohio-dps-public-records-center-ema-ens-ipaws-exercise-logs.md`
- Added `records-requests/bvps-rev0376/online-form-payloads-rev0376.csv` and `dispatch-cut-sheet-rev0376.md` so the next human action can be a payload copy/paste rather than a drafting session.
- Added `cube/bvps-response-sidecar-completion-gate-rev0376.csv` to make receipt metadata, DLP status, proofcut mapping, and withheld-record indexes mandatory before any packet can support claims.
- Rebuilt the derived file-normalization tables from `cube/index.csv`: `cube/file.csv`, `cube/file-field-value.csv`, and `cube/file-tag-edge-normalized.csv`.

## Audit/refactor performed

Rev0376 fixes a concrete derived-layer defect: `cube/index.csv` had rows through 582, but `cube/file.csv` stopped at 579. Tag and field-value normalized tables also failed to cover the current tail. The revision regenerates the affected derived tables from the canonical index and writes `cube/file-normalization-sync-audit-rev0376.csv` and `cube/normalized-tail-coverage-rev0376.csv` so this does not stay hidden.

This is a refactor, not a claim upgrade. It makes the cube easier to query and safer to validate, but it does not import the missing official evidence.

## Non-claims

- No real Beaver Valley response packet has been imported.
- No records request has been sent from this static archive.
- No official preliminary-findings packet has been adjudicated.
- No 11:00 Columbiana results packet is imported.
- No ANS/ENS/IPAWS transition proofcut is closed.
- No EN58200 EOF repair/retest/corrective-action proofcut is closed.
- No local readiness conclusion is made.
