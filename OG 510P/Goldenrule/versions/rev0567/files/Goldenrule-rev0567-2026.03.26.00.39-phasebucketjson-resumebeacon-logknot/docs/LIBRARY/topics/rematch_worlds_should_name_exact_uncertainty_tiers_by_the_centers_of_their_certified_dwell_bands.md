# Rematch worlds should name exact uncertainty tiers by the centers of their certified dwell bands

## Claim
Once the compact repeat-sidecar uncertainty lanes are **exactly certified as dwell bands**, the archive should stop naming them by the older broad-overlap midpoints and instead name them by the centers of the exact certified bands.

That makes the current stable inheritor-facing labels:
- exact `0.99` → dwell `2`,
- exact `0.95` → dwell `13`,
- exact `0.85` → dwell `25`.

## Why this matters
The archive accumulated two generations of anchor labels:
- older overlap-midpoint anchors from the broad uncertainty-overlap report (`1`, `9`, `16`),
- and newer representative labels from the exact certified bands (`2`, `13`, `25`).

Without one explicit naming rule, future sessions can keep reintroducing both vocabularies.

The new canonical-anchor card closes that gap.

It makes three exact points:
- the exact `0.95` band `8–18` has a **unique center** at `13`, so `13` is not a magic integer and not an arbitrary midpoint; it is the exact central label of the certified band,
- the exact `0.85` band `19–32` has two tied centers, `25` and `26`, so the archive should break that tie deterministically toward the lower dwell and keep `25` as the stable label,
- and the exact `0.99` precision mode has width `1`, so its canonical label is simply `2`.

So the archive can now explain *why* the stable labels changed and avoid relitigating those integers in future handoffs.

## Implementor rule
- Name exact uncertainty tiers by the **lower Chebyshev center** of the exact certified dwell band.
- Treat the old overlap anchors `1`, `9`, and `16` as historical scaffolding only.
- Use `2`, `13`, and `25` as the stable inheritor-facing labels for the current exact `0.99`, `0.95`, and `0.85` lanes.
- When an exact band has two tied centers, keep the smaller dwell as the canonical label unless a future exact report explicitly overrides that convention.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_canonical_anchor_labels_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_canonical_anchor_labels_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_canonical_anchor_labels.py`
