# Feedback integration ledger

## v900 — 2026-06-18

- User direction: continue prioritizing risky unfinished work over doctrine/registry expansion, while auditing/refactoring part of the cube.
- Integrated change: reduced the release-completion risk by eliminating nested subprocess fan-out in the four newest replay/accounting/event release-gate checks.
- Audit/refactor: compacted superseded non-current source-byte, trust-policy, replay, and provenance history into a deterministic in-carrier recovery bundle instead of weakening the 16 MiB governed-tree budget.
- Verification target: keep CDF/accounting/event negative controls intact while making the full release gate less likely to time out in the cloudtainer.
- Boundary: synthetic-only release closure work; no live pilot, certification, conformance, outcome-proof, voter-instruction, or legal-advice claim.

## v899 — 2026-06-18

User direction: continue pushing the riskiest unfinished work with substance, avoid registry bureaucracy, and include an audit/refactor of part of the cube.

Implemented response:

- Added a synthetic election-event-log reconciliation lane that binds BD, CVR, ERR, ballot accounting, replay reports, CRO, and public-boundary docs by digest, event hash, previous-event hash, timestamp, and required role.
- Added negative controls for broken previous hash, artifact digest mismatch, timestamp regression, and missing required event role.
- Wired the event-chain verifier into the release gate, go/no-go decision, maintainer handoff, mission-kernel closeout, current-fixture sweep, and pilot-data ledger.
- Refreshed stale current-version entrypoints exposed by the sweep: source-byte workplans, trust-policy lockfile/receipt, PacketVerificationReport template/packet, and Example County scenario outputs.
- Added `docs/936-event-log-provenance-chain-and-current-entrypoint-audit.md` to record the risk closed and the current-entrypoint drift firewall.

Boundary: still synthetic/non-production only; no live Election Event Log evidence, no full NIST EEL/CDF conformance, no certification, no outcome proof, no current voter instruction, and no legal advice.


## v898 — 2026-06-18

User direction: keep pushing the riskiest unfinished work with substance instead of doctrine/registry bureaucracy, and include an audit/refactor of part of the cube.

Implemented response:

- Moved CDF replay from aggregate contest totals to reporting-unit comparison rows.
- Expanded the synthetic fixture to two reporting units and six CVRs.
- Added a total-preserving unit-swap negative control so aggregate-only replay cannot pass.
- Kept the independent verifier aligned with the primary adapter without importing or executing it.
- Refreshed ballot-accounting reconciliation and release decision artifacts around the larger fixture.
- Added a v898 audit note documenting the blind spot and release-gate runtime pressure.
- Compacted superseded source-byte/cache history into a deterministic in-carrier bundle to keep package size from crowding out current executable evidence.

Boundary: still synthetic/non-production only; no live jurisdiction export, no certification, no outcome proof, no current voter instruction, and no legal advice.
