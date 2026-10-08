# Decision — the flagship i3/X11 stack must self-install and self-rehearse

The flagship `vhk gen-i3-busd-stack` output now owns its own XDG-local install, uninstall, and smoke-rehearsal path.

## Decision

Treat the generated flagship stack as a deployable operator/LLM handoff, not just a pile of review artifacts.

That means each generated stack should ship:

- one install script that copies the units, wrappers, control manifest, and i3 snippet into stable XDG-local locations
- one uninstall script that removes those installed artifacts cleanly
- one smoke script that rehearses install/uninstall into a throwaway XDG root before touching the live desktop

## Why

Without this layer, the repo kept saying the warm i3/X11 lane was the primary product path, but a human still had to manually copy units, wrappers, autostart entries, and i3 config fragments into place.

That gap hurt exactly the things the flagship lane is supposed to optimize:

- speed of first useful setup
- reliability of startup-owner changes
- observability of what is actually installed
- practical usefulness for a private LLM that needs stable deploy/rollback entrypoints instead of shell-history folklore

## Boundaries

This is still an i3/X11-first decision.

- The primary owner remains the graphical-session-bound user unit lane.
- XDG autostart remains an explicit fallback bridge, disabled by default.
- Ad hoc CLI runs stay available, but the resident runtime remains the optimized path.
- This does not expand Wayland/portal/app-native scope.

## Consequences

The flagship stack now has a smaller but more honest lifecycle:

1. generate
2. smoke-install
3. install into XDG-local paths
4. include the installed i3 snippet
5. run/repair through the resident control plane
6. uninstall cleanly when testing or rolling back
