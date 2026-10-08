# Rematch worlds should keep the current exact uncertainty menu as an irreducible three-tier basis

## Claim
The current exact compact repeat-sidecar uncertainty menu should be treated as an **irreducible three-tier basis**, not as a cluttered menu that can be safely collapsed.
Each current exact tier owns a live request region that the other two do not cover:
- exact `0.85` is the **cap-limited relaxed basis row**,
- exact `0.95` is the **positive-slack bridge row** above floor `0.870482`,
- exact `0.99` is the **high-floor precision row** above floor `0.980481`.

## Why this matters
The archive already had enough threshold, selector, and fragility information to compare the tiers, but it did not yet state the stronger maintenance rule:
**none of the three current exact rows is removable without losing a real request region.**

That matters because future inheritors will be tempted to simplify the menu:
- drop `0.85` because it looks weaker,
- drop `0.95` because it looks like a middle tier,
- or drop `0.99` because it looks fragile.

The new basis card makes the loss from each move explicit:
- without exact `0.85`, cap-limited deployments at hard cap `3–4` lose every current exact option,
- without exact `0.95`, the menu jumps straight from the relaxed `0.85` band to the fragile single-point `0.99` precision mode whenever positive slack is required,
- without exact `0.99`, the archive has no current exact answer above floor `0.980481` at all.

So the current exact menu is not redundant.
It is the smallest current exact menu that still covers the archive’s live low-cap, positive-slack, and high-floor request regions.

## Implementor rule
- Keep all three current exact uncertainty tiers unless new frontier evidence creates a replacement row for one of their basis regions.
- Treat exact `0.85` as the low-cap relaxed row for hard-cap budgets `3–4`.
- Treat exact `0.95` as the only current exact row that both exceeds floor `0.870482` and survives positive slack / band width above `1`.
- Treat exact `0.99` as the only current exact row above floor `0.980481`.
- When someone proposes “simplifying” the menu, require an explicit witness that their replacement still covers each of those three basis regions.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_menu_basis_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_menu_basis_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_menu_basis.py`
