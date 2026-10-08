# Field execution risk burndown rev0282

## Highest current risk

`FT-0181` is still externally gated: no real owner packet, no real returned CSV,
no accepted import, no live-window readout, and no closure signoff exist. The
most useful local work is therefore not another policy layer. It is reducing the
ways local scratch artifacts can imitate field progress.

Rev0282 burns down the clarification-clock bypass. A first-contact wait state
already requires a send log. Now the one allowed re-ask wait state requires a
reask log.

## Risks reduced

| Risk | Rev0282 reduction |
|---|---|
| A stale due first clock creates a fake reask wait state | Router emits `owner-reask-log` first; contact status rejects direct prior-clock sources. |
| A `RE-ASK-ONCE` intake bundle becomes a second contact clock without a send/adaptation artifact | Intake routes to reask-log; reask status requires the reask-log source. |
| A `REASK-OWNER` workbench review becomes a clock by prose | Workbench reask routes through the same reask-log seam. |
| A reask clock is open-ended | Reask logs and contact status both cap the clarification response window at three days. |
| A reask log leaks owner answers or contact details | Tool argument guard, manifest guard, and direct validator forbid recipient details, owner answers, raw/protected facts, screenshots, credentials, and public-claim language. |
| Registry-only progress replaces field execution | The change is a Make target, recorder, shared guard, router behavior, and validator; the audit is secondary. |

## What remains risky

The human still has to do the real field work outside the archive: identify an
accountable route, send/adapt the bounded packet or re-ask, and receive the real
owner-returned CSV. The archive cannot do that by itself. It can only prevent a
local artifact from pretending that it happened.

## Next useful work

Use the router. In a scratch path with a due first clock, `RE-ASK-ONCE` intake,
or `REASK-OWNER` workbench review, the next useful command should be
`make owner-reask-log ...`. After that, rerun the router and record only the
emitted reask contact clock. If no real owner reply arrives after that bounded
clock, record `NO_OWNER_PACKET` and keep `FT-0181` live without widening the ask.
