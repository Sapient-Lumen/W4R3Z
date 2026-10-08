# Rematch worlds should price uncertainty guarantee upgrades by exact operating tariffs

## Claim
Future inheritors should treat upgrades between the exact compact repeat-sidecar uncertainty tiers as **priced moves**, not just as three disconnected operating modes.

## Why this matters
The archive already knows the exact tiers:
- relaxed `0.85` on dwell `19`–`32` with hard cap `3` and `5` union checkpoints,
- near-optimal `0.95` on dwell `8`–`18` with hard cap `5` and `8` union checkpoints,
- near-exact `0.99` at dwell `2` with hard cap `11` and `14` union checkpoints.

The new useful fact is the **marginal tariff** between them:
- moving `0.85 -> 0.95` costs only `+2` cap steps and `+3` net checkpoints while buying `+0.109999` worst-case gain share,
- moving `0.95 -> 0.99` costs `+6` cap steps and `+6` net checkpoints while buying only `+0.019341` more worst-case gain share.

So the current `0.95` lane is the real **upgrade knee**. It is where the archive still buys a large guarantee improvement without yet paying the near-exact maintenance explosion.

## Implementor rule
- Default to the exact `0.95` lane when the archive wants the best bargain between guarantee strength and operating burden.
- Relax to `0.85` only when the archive intentionally wants the smaller maintenance surface and can really surrender the late-tail checkpoints `230/239`.
- Upgrade to `0.99` only when near-exact preservation is itself the objective, because that final step is structurally expensive.
- Keep the direct `0.85 -> 0.99` span in mind as the full envelope: `+8` cap steps and `+9` net checkpoints.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_upgrade_tariff_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_upgrade_tariff_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_upgrade_tariff.py`
