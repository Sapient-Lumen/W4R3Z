# Decision: explicit startup owner and bounded session bridge for the i3/X11 flagship

Date: 2026-03-23
Status: accepted for the flagship lane, not yet fully wired into `gen-i3-busd-stack`

## What this tightens

VHK's flagship story is **not** “generic Linux desktop automation.” It is a fast i3/X11 lane with a resident user service, thin emit/dispatch paths, honest recorder-cleanup-replay loops, reliable X11 control, and a private-LLM control plane that can author, revise, and execute macros without rebuilding runtime assumptions each turn.

That means startup ownership must stay explicit:

- the **primary startup owner** is the `systemd --user` graphical session target
- the **fallback owner** is an XDG autostart bridge
- both should not be treated as default co-owners of the same warm lane

## Why this matters

The repo already has strong policy primitives for:

- session activation environment sync
- graphical-session target binding
- session readiness probes
- startup-handoff ownership

But the product story was still easier to read in the service-compose lane than in the flagship i3/X11 lane. That made the warm-runtime contract look more implicit than it should be.

## Concrete flagship contract

This revision adds a focused builder module:

- `src/vhk/project/i3_x11_flagship_startup_bridge.py`

It composes the existing policy builders into one explicit contract for the i3/X11 flagship lane:

- X11 desktop backend
- i3 as the primary window manager
- `socket-activated-busd` as the default service mode
- `graphical-session.target` as the default startup owner
- XDG autostart as a fallback bridge, not a second default owner
- explicit helper paths for activation sync, readiness probe, and bounded session start
- explicit private-LLM triage/edit/dispatch/runtime-repair entrypoints

## Why this cut is worth taking now

It sharpens the X11/i3 core without reopening broad Linux-native ambition:

- no new abstraction layer over X11 control
- no portal-first runtime story
- no Wayland-first generalization
- no app-native adapter detour

It also gives the repo a smaller target for the next implementation step: wire the composed contract into `gen-i3-busd-stack` so the exported stack surfaces match the already-explicit policy story.

## Next implementation step

Promote this composed contract into the generated flagship stack so `control-plane.json`, `README.md`, and exported helper surfaces all agree on:

1. one primary startup owner
2. one bounded autostart fallback bridge
3. one readiness probe before session-bound startup
4. one small activation-sync helper instead of login-magic handwaving
