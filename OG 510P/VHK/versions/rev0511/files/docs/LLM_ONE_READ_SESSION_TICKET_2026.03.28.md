# LLM one-read session ticket — 2026-03-28

## Why this exists

The flagship VHK lane is not “generic Linux automation.” It is:

- i3 on X11
- a session-bound warm user service
- thin emit/dispatch from hotkeys
- recorder -> cleanup -> replay -> proof
- a private LLM that can safely edit macro YAML and operate the live stack

The repo already had the right ingredients, but the LLM lane still had to reopen too
many helpers to reconstruct the same answer:

- is the resident runtime actually ready on the live X11/i3 session?
- which macro is currently selected?
- where is the canonical editable source?
- what is inspect-only evidence?
- what is the bounded next command?

That re-join cost was too high for the flagship lane.

## Product decision

The generated i3/X11 stack should expose one compact session surface for the private
LLM:

- `bin/llm_session_ticket_json.sh`
- `bin/llm_session_ticket.sh`

This surface is not a new source of truth. It is a bounded projection over the
existing resident control plane.

## What the ticket must contain

A valid one-read session ticket names:

- the selected macro
- the warm runtime lane
- the selected-macro work lane
- the primary LLM workbench
- the authoring boundary
- the selected handoff
- the bounded next action
- a recommended open sequence

The ticket must also state the edit contract explicitly:

- edit authority: macro YAML only
- inspect-only classes: generated review surfaces, runtime snapshots, runtime observability
- actuation class: runtime actuation

## What this sharpens

This keeps the flagship loop cheap and explicit:

1. read one session ticket
2. open canonical macro source if mutation is needed
3. inspect receipt / replay / cleanup evidence only when the ticket points there
4. execute only through bounded generated wrappers
5. re-read the session ticket after state changes

## What this does *not* change

This does not widen VHK toward a broader Linux-native story.

It does not make Wayland, portals, or app-native adapters first-class. Those remain
secondary unless they materially improve the i3/X11 lane.

It also does not replace the fused stack snapshot. `stack_state_json.sh` remains the
full resident datacube; the session ticket is the compact operator/LLM fast path.
