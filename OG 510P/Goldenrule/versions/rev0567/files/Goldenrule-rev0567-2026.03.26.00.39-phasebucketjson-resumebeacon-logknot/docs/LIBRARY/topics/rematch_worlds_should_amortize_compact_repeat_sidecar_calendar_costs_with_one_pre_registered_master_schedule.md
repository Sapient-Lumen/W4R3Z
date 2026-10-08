# Rematch worlds should amortize compact repeat-sidecar calendar costs with one pre-registered master schedule

## Claim
Future inheritors should treat the current `17`-point master audit calendar as a **one-time pre-registration cost** that can amortize away future checkpoint churn across the trusted-repeat fallback and all current exact uncertainty-safe tiers.

## Why this matters
The archive already knew that one sparse master calendar covers:
- the trusted-repeat rewrite-budgeted fallback,
- the exact relaxed `0.85` uncertainty tier,
- the exact near-optimal `0.95` tier,
- the exact near-exact `0.99` tier,
- and the structural-only checkpoints `79` and `191`.

What was missing was the implementor-facing pricing rule.

The new exact amortization card makes that rule explicit:
- if you stay on per-mode calendars, immediate checkpoint burden is smallest, but future upgrades and downgrades keep reopening the calendar question,
- if you pre-register the full `17`-point master calendar once, every current mode switch becomes **calendar-free**: no new audit dates need to be added later,
- the future-proofing gap is largest from the trusted fallback (`+13` dates still needed), smaller from exact `0.85` (`+12`), moderate from exact `0.95` (`+9`), and tiny from exact `0.99` (`+3`: only `56`, `79`, and `191`).

So the archive can now distinguish two different costs:
- **immediate** calendar burden for one chosen mode,
- **amortized** calendar burden for a program that expects mode churn.

## Implementor rule
- When the archive is confident it will stay in one mode for a while, keep the mode-specific checkpoint list and pay only the minimum immediate burden.
- When the archive expects policy churn across the trusted fallback and the current exact uncertainty tiers, pre-register the full `17`-point master calendar once and then choose modes only by cap, guarantee, and tolerance needs.
- Treat exact `0.99` as the cheapest future-proof starting point because it is already only three dates short of the full master schedule.
- Treat the trusted `4`-transition fallback as the smallest immediate calendar, but the worst future-proof launch point.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_master_calendar_amortization_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_master_calendar_amortization_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_master_calendar_amortization.py`
