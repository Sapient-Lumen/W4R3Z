# Revision 0298 — promotion dispatch budgets

This revision adds `promotion_dispatch_budget_plan` and `promotion_dispatch_budget_summary` to the planner and promotion-facing packs.

## What changed

- `vhk plan-project --json` now emits a promotion-side dispatch budget for each shipped surface.
- Human `vhk plan-project` output now shows **Promotion dispatch budgets**.
- `gen-promotion-pack`, `gen-capability-audit-pack`, and `gen-operator-pack` now render the same dispatch-budget surface.
- The new plan makes cold-start versus warm-path ownership explicit:
  - text/package surfaces → `service-resident`
  - remapper surfaces → `edge-resident`
  - helper dossiers → `daemon-warm` or `session-resume`
  - watcher services → `service-resident`
  - launchers → `launch-cold`

## Why it matters

Linux-native automation can look healthy on paper while still feeling slow in the hand. Startup routes, operator controls, recovery lanes, and performance envelopes were already visible, but the repo still lacked one concrete answer to the AHK-parity question: which path is allowed to be cold, and which path must already be warm when the user hits the trigger?

That distinction matters because a resident text surface, a remapper at the input edge, a watcher service, a helper daemon, and a launcher should not all inherit the same latency story. Putting that expectation into planner JSON and review docs makes regressions easier to spot before they become “Linux just feels slower” folklore.
