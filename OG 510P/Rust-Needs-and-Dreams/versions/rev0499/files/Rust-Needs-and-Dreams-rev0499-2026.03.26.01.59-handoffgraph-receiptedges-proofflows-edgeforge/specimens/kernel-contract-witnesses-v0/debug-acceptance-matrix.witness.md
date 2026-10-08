
# Contract witness: Debug Acceptance Matrix

Status: **illustrative witness, not live proving-ground evidence**

## Identity
- candidate: **Feedback / Debug Acceptance Commons**
- governing packet: `packets/top-band-v0/debug-acceptance.deepen.current.md`
- governing kernel: `kernels/top-band-v0/debug-acceptance-matrix.v0.md`
- governing slice: `slices/top-band-v0/debug-acceptance-matrix.slice0.md`
- governing contract: `contracts/top-band-v0/debug-acceptance-matrix.contract0.md`
- witness role: `contract-witness/v0`

## Invocation shape
Illustrative command family:
- `debug-accept collect --fixture async-mpsc-01 --tuple lldb-linux-stable --out debug-session-pack.example.json`
- `debug-accept tuple-card --session debug-session-pack.example.json --out debug-tuple-card.example.json`
- `debug-accept replay --baseline debug-session-pack.example.json --candidate nightly-session-pack.example.json --out debug-replay-result.example.json`

## Example files
- `debug-acceptance-matrix.debug-session-pack.example.json`
- `debug-acceptance-matrix.debug-tuple-card.example.json`
- `debug-acceptance-matrix.debug-replay-result.example.json`
- `debug-acceptance-matrix.unsupported-state-receipt.example.json`

## Truth preserved
This witness is allowed to show:
- tuple identity,
- async visibility posture,
- expression-evaluation posture,
- and one replayable regression signal.

## Negative or partial-state posture
This witness keeps one explicit yellow posture and one explicit unsupported-state receipt:
- async task visibility is partial, so the tuple card must stay yellow even though stepping and locals are usable.

## Refused wider interpretations
Do **not** read this witness as:
- a debugger ranking,
- evidence that one tuple generalizes to all Linux or all LLDB usage,
- or proof that a missing export format has been solved.

## Refresh trigger
Refresh this witness when:
- the debugging survey results are published with materially different scope,
- tuple-card fields change materially,
- or replay-result posture becomes more exact.
