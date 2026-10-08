# Rematch worlds should pre-register one master audit calendar for compact repeat sidecars

## Claim
The archive should keep one **master audit calendar** for compact repeat-sidecar reevaluation instead of juggling separate checkpoint lists for the exact uncertainty tiers, structural flips, and the practical rewrite-budgeted fallback.

## Why this matters
The saved exact uncertainty lanes already form a checkpoint staircase, but the deeper operational fact is even simpler:
- the near-exact `0.99` checkpoint union already contains the full near-optimal `0.95` union,
- covering the relaxed exact `0.85` lane needs only one extra transition checkpoint, `56`,
- and the only mandatory structural checkpoints outside the exact transition unions are `79` and `191`.

So the full current operational surface compresses to one sparse 17-point audit calendar:
`9, 15, 24, 31, 38, 47, 54, 56, 63, 79, 111, 143, 159, 191, 230, 239, 255`.

That same calendar also covers the trusted-repeat four-transition fallback because its checkpoints `56, 111, 159, 239` are already inside the master set.

## Implementor rule
- If one sparse review schedule must cover every currently certified uncertainty-safe lane, start from the near-exact `0.99` calendar.
- Add `56` to cover the relaxed exact `0.85` lane.
- Never drop `79` or `191`, because they are structural filter/route order flips even though they are not transition checkpoints for the current exact uncertainty tiers.
- Use the resulting 17-point master calendar instead of per-append polling.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_master_audit_calendar_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_master_audit_calendar_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_master_audit_calendar.py`
