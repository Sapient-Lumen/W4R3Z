# REV0332 — runtime next-action control plane

This revision strengthens the flagship i3/X11 warm-runtime stack with a small next-action layer.

## What changed

- fixed the generated `assert_runtime_ready.sh` helper so it consumes its JSON payload correctly
- added `bin/next_action_json.sh` to generated i3/X11 stacks
- added `bin/next_action.sh` to generated i3/X11 stacks
- extended `control-plane.json` so those next-action helpers are part of the stable operator/LLM contract
- updated README and runtime-stack docs to reflect the stronger guidance surface

## Why it matters

The stack can now say more than “here is raw state.” It can also say “here is the next thing to do,” which is useful both for a human operator and for a private LLM that should not have to reverse-engineer the warm-runtime posture from scratch on every turn.
