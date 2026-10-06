# Priority-0 current-tail external bundle audit — 2026-06-15

## Risk burned

`rev0365` made the right ethical move by refusing to claim an external replay before a response exists. The remaining operational risk was sharper: the handoff was still a set of files inside the public archive, and its responder-only packet was keyed to the `rev0365` live successor (`OQ-0257`) rather than the current tail after this revision.

That is not a semantic failure of `rev0365`; it is a handoff-use failure. A future operator could grab the old responder-only packet, believe it is current, and unknowingly replay a stale question while the cube has moved on.

## Change made

This revision resolves `OQ-0257` narrowly by replacing the raw handoff with a physically separated, deterministic current-tail responder bundle:

- `assays/priority-zero-current-tail-external-replay-responder-only-2026-06-15.json`
- `assays/priority-zero-current-tail-external-replay-response-template-2026-06-15.json`
- `handoffs/priority-zero-current-tail-external-replay-responder-bundle-2026-06-15.zip`
- `handoffs/priority-zero-current-tail-external-replay-handoff-manifest-2026-06-15.json`
- `assays/priority-zero-current-tail-external-replay-scorer-intake-2026-06-15.json`
- `assays/priority-zero-current-tail-external-replay-bundle-2026-06-15.json`
- `tools/check_priority_zero_current_tail_external_bundle_contract.py`

Only the responder packet and blank response template are inside the ZIP. The scorer intake remains outside the responder bundle and is for after a completed response exists.

## Finding

The `rev0365` handoff remains useful as historical handoff-readiness evidence, but it is no longer the current-tail input. The current-tail bundle points at `OQ-0258`, records bundle and file hashes, and keeps compact reentry narrowed until response evidence is actually produced.

## Scores

| Variant | Score | Operator cost | Interpretation |
|---|---:|---:|---|
| Legacy raw handoff stale-current control | 10 / 18 | 6 min | Leak-sealed, but stale-current and not physically bundled. |
| Current-tail responder bundle | 17 / 18 | 4 min | Operational blind input with current routing and bundle custody. |
| Scorer intake after response | 15 / 18 | 8 min | Ready to score after a response, but not response evidence. |
| Completed external response evidence | 0 / 18 | 0.5 min | Correctly absent; compact gate cannot be strengthened. |

## Non-takes

This is not external certification, not deletion authority, not benchmark authority, not minimality proof, and not a review court. It is a leak/stale-cue correction and a runnable handoff object.

## Next action

Hand only `handoffs/priority-zero-current-tail-external-replay-responder-bundle-2026-06-15.zip` to a separate responder. Do not expose `assays/priority-zero-current-tail-external-replay-scorer-intake-2026-06-15.json` or the full archive before the responder fills the template. Then score the completed response and decide whether compact reentry confirms, narrows, or reverses under `OQ-0258`.
