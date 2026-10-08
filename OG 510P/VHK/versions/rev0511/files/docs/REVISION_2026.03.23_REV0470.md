# Revision 0470 — warm runtime repair recipe becomes explicit

This revision turns the resident-runtime repair lane into an explicit compact contract instead of leaving it spread across `status_id`, `latest_runtime_repair`, and startup-owner side surfaces.

## What changed

- `warm_runtime_ticket` now carries `runtime_repair_recipe`.
- The recipe classifies the active repair family and scope, preserves the bounded recommended command, and carries a retry guard for recent failed reload/restart attempts.
- The recipe can also surface startup-owner drift as `secondary_attention` so login-time durability issues stay visible without replacing the live-session repair lane.
- `warm_runtime_ticket.sh` and `stack_state.sh` now print compact `runtime_repair_*` lines for operators.
- The helper manifest now advertises a `runtime_repair_recipe_projection` contract for `warm_runtime_ticket_json.sh` and an inline human-summary digest contract for `warm_runtime_ticket.sh`.

## Why it matters

The repo already knew how to detect warm-runtime drift, but the compact resident ticket still made callers infer too much: whether the problem was restart-vs-reload-vs-sync, whether a retry was safe, and whether startup ownership still needed follow-up.

Now the resident i3/X11 control plane can answer that in one read, which is exactly the kind of sharp bounded contract a private LLM and a human operator both need.
