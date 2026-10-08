# Rematch worlds should choose exact uncertainty weakening regimes by capability promises, not threshold numerology

## Claim
Once the archive already exposes named weakening regimes, future inheritors should select them by the smallest promise bundle they need to satisfy rather than by reading raw threshold numbers directly.

## Why
- the current six weakening regimes already expose an exact capability ladder: suffix-only relaxed release appears at `7`, middle-band precision relief appears at `11`, neutral-anchor relaxed release appears at `12`, direct entry-boundary release appears at `17`, and direct precision release appears at `23`,
- threshold `11` is the only way to add middle-band precision relief **without** enlarging the relaxed-floor release basin beyond neutral exit boundary `18`,
- some promise bundles are genuinely impossible in the current menu, for example demanding neutral-anchor relaxed release while forbidding any relaxed-basin growth.

## Current archive consequence
- the archive now carries a weakening-capability selector that returns the **smallest named regime** satisfying a requested promise bundle,
- the selector also marks impossible bundles explicitly instead of letting the inheritor chase nonexistent threshold values,
- the main impossible family is “allow stronger relaxed-floor release, but forbid relaxed-basin growth beyond `18`.”

## Operational rule
1. decide which release promises are actually needed: any relaxed release, middle-band precision relief, neutral-anchor release, direct entry-boundary release, or full precision release,
2. state separately whether relaxed-basin growth beyond neutral exit boundary `18` is forbidden,
3. choose the smallest regime returned by the selector,
4. if the selector says the bundle is impossible, relax the promise set rather than searching for an unseen threshold.

## Pointers
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_capability_selector_snapshot_20260308.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_capability_selector.py`
