# 75 — Broadcast + Operator Synchronization Protocol (v0.19)

You plan to use Terminator broadcast and/or tmux sync panes.
Broadcast is powerful but fragile: mis-broadcast can look like model failure.

This doc defines an operator runbook and router-side mitigations.

## 1) Operator primitives
- Broadcast the “start slice” prompt to all agents.
- Avoid interactive sequences that diverge across terminals.
- Prefer scripts/aliases to reduce human error.

## 2) tmux alternative
tmux supports `synchronize-panes` to broadcast input across panes.
This can be used as a stable fallback when your terminal emulator is flaky.

## 3) Router mitigations
The router can’t reliably detect your terminal broadcast toggle, but it can detect symptoms:
- simultaneous identical agent inputs at near-identical timestamps
- sudden correlated parse failures
- repeated identical outputs across agents

If detected:
- enter Recovery mode suggestion
- warn the operator in gearbox: “broadcast anomaly suspected”
- recommend a snapshot before continuing

## 4) Safe broadcast patterns
- “start turn” command only
- “request view refresh” command only
- never broadcast destructive shell commands unless you intend it

## 5) Per-agent customization despite broadcast
If you must customize:
- keep the broadcast prompt identical
- then send a tiny per-agent override via REQ# or “ROLE: next focus” entries (bounded)

## 6) Postmortems
When something goes wrong:
- record: whether broadcast was on, and what was sent
- keep raw PTY logs per agent for correlation
