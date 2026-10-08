# Revision 0297 — promotion performance envelopes

This revision adds `promotion_performance_plan` and `promotion_performance_summary` to the planner.

## What changed

- `vhk plan-project --json` now emits a promotion-side performance envelope for each shipped surface.
- Human `vhk plan-project` output now shows **Promotion performance envelopes**.
- `gen-promotion-pack`, `gen-capability-audit-pack`, and `gen-operator-pack` now render the same performance-envelope surface.
- The new envelope makes latency/throughput ownership explicit:
  - text/package surfaces → `throughput-first`
  - remapper surfaces → `low-latency-edge`
  - daemon-backed helpers → `warm-daemon`
  - portal/session helpers → `consent-bound-async`
  - watcher services → `event-pipeline`
  - launchers → `launch-to-dispatch`

## Why it matters

VHK already knew who ships, starts, controls, recovers, and verifies a promoted surface. The missing Linux-native truth was what kind of hot path that surface is supposed to protect.

That matters for an AHK-class Linux product because text expansion, remapping, helper playback, watcher services, and launcher surfaces win in different ways. A planner that hides those differences makes performance regressions easier to rationalize away.
