# Structural audit rev0377

## Finding 1 — West Virginia lane was under-specified

The FEMA exercise surface includes Pennsylvania and West Virginia, while the package had much stronger Pennsylvania and Ohio/Columbiana request machinery than West Virginia/Hancock machinery. That was the highest-risk acquisition gap because it could leave local West Virginia evidence out of the dispatch sequence.

Repair: add WV DHS/WVEMD and Hancock County OEM request packets, a tri-state dispatch board, and a proofcut/request crosswalk.

## Finding 2 — Dispatch surface remained fragmented

Request templates existed across rev0373 through rev0376, but the next operator still had to reconstruct priority, custodian, proofcut, and clock relationships.

Repair: add `cube/bvps-tristate-custodian-dispatch-board-rev0377.csv` and mirror it into `records-requests/bvps-rev0377/dispatch-board-rev0377.csv`.

## Finding 3 — Active surface still too large for the next human action

The full archive remains intentionally preserved, but the next step is not a full-cube read; it is dispatch and receipt capture.

Repair: add `evidence-bags/bvps-tristate-dispatch-capsule-rev0377.zip` with a compact workset. No historical evidence was deleted.

## Remaining blockers

- Official FEMA preliminary findings packet not imported.
- WV/Hancock response packets not imported.
- Ohio/Columbiana ENS/IPAWS response packet not imported.
- NRC/EN58200 EOF repair-retest-CAP packet not imported.
- Dispatch receipts absent.
- Proofcut closure remains blocked.
