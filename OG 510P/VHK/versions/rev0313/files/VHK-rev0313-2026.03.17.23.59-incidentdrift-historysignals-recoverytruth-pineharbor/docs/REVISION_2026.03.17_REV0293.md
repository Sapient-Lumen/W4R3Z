# REV0293 — promotion startup routes

This revision adds a new planner/promotion contract: `promotion_activation_route_plan`.

## What changed

- `plan-project` now emits `promotion_activation_route_plan` so each promotion surface names:
  - its startup posture (`resident`, `session-bound`, `launcher-first`, `reviewed`, `orthogonal`)
  - the primary activation route that owns wake-up and steady-state lifecycle
  - alternate activation routes
  - related host requirements / alternative requirement groups
  - merged review commands, evidence, and cautions
- `vhk plan-project` human output now shows a **Promotion startup routes** table.
- `gen-promotion-pack` now carries and renders startup-route ownership alongside shipping-lane ownership.
- `gen-capability-audit-pack` now renders the same startup-route ownership so capability review includes lifecycle truth.
- README/spec/plan/issues docs now describe startup ownership as a first-class promotion concern.

## Why it matters

VHK already had a good answer for “which lane should own shipped input?”.
This revision adds the missing Linux-native answer for “who actually starts and
keeps that surface alive?”

Those are different questions on Linux:

- text surfaces often want a resident service-like route
- remapper exports often want a remapper/service ownership route
- portal shortcut surfaces are session-bound
- launcher surfaces are intentionally on-demand
- helper-sensitive flows must keep helper/session review explicit

Treating those as one problem makes release docs drift back toward vague
“backend support” language. This revision keeps shipping ownership and startup
ownership visible side-by-side.
