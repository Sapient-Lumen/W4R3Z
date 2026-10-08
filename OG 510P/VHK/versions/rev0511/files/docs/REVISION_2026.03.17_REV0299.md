# Revision 0299 — promotion authority envelopes

This revision adds `promotion_authority_envelope_plan` and `promotion_authority_envelope_summary` to the planner and promotion-facing packs.

## What changed

- `vhk plan-project --json` now emits an authority envelope for each promoted surface.
- Human `vhk plan-project` output now shows **Promotion authority envelopes**.
- `gen-promotion-pack`, `gen-operator-pack`, and `gen-capability-audit-pack` now render the same authority-envelope surface.
- The new plan makes Linux ownership clearer per promoted surface:
  - text/package surfaces → `session-userland`
  - remapper surfaces → `input-edge-privileged`
  - portal helper/session surfaces → `desktop-mediated`
  - helper-daemon/uinput surfaces → `helper-daemon-privileged`
  - launcher surfaces → `launch-userland`

## Why it matters

A Linux automation surface can feel warm and still not actually own authority in the same way as another surface. Startup posture, dispatch budget, and actual host authority are separate questions. By making authority explicit in planner JSON and review docs, VHK is less likely to blur user-session services, portal sessions, remappers, and helper daemons into one fake “Linux support” bucket.
