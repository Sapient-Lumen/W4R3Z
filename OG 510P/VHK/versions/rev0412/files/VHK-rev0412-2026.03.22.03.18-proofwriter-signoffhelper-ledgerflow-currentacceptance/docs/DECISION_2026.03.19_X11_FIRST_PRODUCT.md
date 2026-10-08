# Decision — VHK is i3/X11 first

## Status
Accepted in revision 0325.

## Decision

VHK's active product identity is now:

**"VHK is an i3/X11-first desktop automation engine and future studio."**

The repo no longer treats broad Linux/Wayland parity as a co-equal near-term
product promise.

## Why

- i3/X11 is the environment the maintainer actually lives in.
- The repo already has strong momentum around recorder/replay, X11 execution,
  window context, and i3-oriented runtime flows.
- Wayland work is real and valuable, but it currently fragments the story and
  competes with the main product loop.
- A narrow, honest flagship target is better than a vague universal promise.

## Consequences

### We actively optimize for

- i3/X11 runtime reliability
- recorder/cleanup/replay excellence
- event-driven waits and window guards
- session-bound service ownership
- fast warm-path invocation
- private-LLM-authored macros and script execution

### We demote

- portal-first activation as a primary activation story
- Hyprland/KWin-specific product shaping
- broad Wayland parity language in the main README/story
- app-native adapters as roadmap centerpieces

### We keep

- architectural seams that honestly model different capability/authority lanes
- ad hoc CLI execution
- enough research/history to revisit old lanes later if reality changes
