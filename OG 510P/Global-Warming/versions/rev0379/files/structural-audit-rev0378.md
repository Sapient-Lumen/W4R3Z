# Structural audit — rev0378

## Highest-risk finding

The cube had accumulated enough records-request packets that dispatch itself became error-prone. More drafting could make the problem worse: duplicate federal tickets, stale state/local requests, missed route changes, and missing receipts would all prevent proofcut closure.

## Repair

Rev0378 creates a canonical active dispatch batch, marks older packets as superseded or lineage-only, and generates one receipt sidecar per active request. The dispatch clock table is explicitly provisional because clocks start from actual custodian receipt, not from static package creation.

## Audit/refactor scope

- Request packet inventory and supersession state.
- Active capsule content and historical dispatch-surface pruning.
- Response sidecar coverage for every active request.
- File/source normalized table coverage through file 585.

## Remaining structural risk

The static archive cannot submit records requests. The next non-bureaucratic step is actual dispatch plus receipt capture. Until that occurs, all proofcuts remain open.

## Source graph alias repair

The rev0378 source validator exposed 11 legacy external/SRE source identifiers used by older index rows but absent from `cube/source.csv`. Rev0378 registers them as legacy aliases/fixtures, not as new readiness evidence.
