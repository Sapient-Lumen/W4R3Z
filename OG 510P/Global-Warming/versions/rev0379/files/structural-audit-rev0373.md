
# Structural audit rev0373

## Highest-risk unfinished work

1. **Public-meeting packet capture** remains the highest-risk incomplete task. The FEMA notice/public meeting clock is not evidence. The cube now has a status ledger and a ready FEMA/DHS packet, but no response packet is imported.
2. **EN58200 EOF follow-up** remains open. The NRC event notice is a trigger for repair/retest/corrective-action evidence, not a proofcut closure.
3. **ANS transition evidence** remains absent. Plans, public pages, mailers, and notices are insufficient to close demonstrated alerting performance.
4. **State/local evidence routes** are reverified but not yet packetized beyond triage. They should be built after federal dispatch receipts or sooner if the public-meeting trail is weak.

## Corrected source-graph failure

Rev0373 fixed a concrete integrity defect:

- S1359-S1364 were present in `cube/source.csv` but absent from `sources/register.md`.
- S1365-S1371 were referenced by index rows but absent from `cube/source.csv` and `sources/register.md`.
- `cube/source-use-ledger.csv` was stale for recent source IDs and for older IDs reused in recent index rows.

The repair recomputed the ledger and edge table from `cube/index.csv` rather than hand-editing only the visible tail.

## Active-surface refactor

The new active-surface capsule is a real burn-down control for cloudtainer waste. It does not delete historical evidence. It gives the next pass a default small work surface containing front doors, route/request controls, source graph, key BVPS proofcut/hotpath artifacts, and validators.

## Remaining non-claim controls

No route page, public notice, source register line, request template, or active-surface capsule is readiness evidence. Only imported, hashed, redacted when necessary, and proofcut-adjudicated response packets can change the claim state.
