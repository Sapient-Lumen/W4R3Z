# 52 — Gearbox TUI Spec (Ratatui) (v0.19)

The Gearbox is the human’s “control surface.”
It should be fast, low cognitive load, and resistant to operator mistakes.

## 1) Design goals
- One keystroke to switch modes (Gatekeeper/PatchOnly/Freeze/etc.).
- One keystroke to force compaction.
- One keystroke to re-render all agent views (“refresh”).
- Visible: H0, mode, selected patch, certified CE, integrator.
- Visible: parse success rates + time_to_ctrl per agent.
- Visible: queue depths / backpressure warnings.

## 2) Layout (suggested)
- Top bar: H0 + mode + strictness + CURSOR
- Left pane: HOT + mandatory events
- Middle pane: selected patch / integrator scope / leases
- Right pane: telemetry (per agent)
- Bottom: command palette + recent actions

## 3) Inputs
- keybinds for critical actions (mode, compact, snapshot, cap probe)
- command palette for everything else:
  - `mode PatchOnly`
  - `compact now`
  - `thread fork ...`
  - `weights set A1=2.5 A4=0.7`
  - `verifier run unit_fast`

## 4) Safety rails
- destructive actions require “double tap” or a confirm key (configurable)
- broadcast warnings: show a banner if operator toggled broadcast mode externally

## 5) Event handling model
Central event capture → message passing to state store.
The UI never mutates WS directly; it sends commands to the kernel.

## 6) Debug views
- “View diff inspector”: what was suppressed due to budgets?
- “Parse inspector”: why did CTRL parse fail (missing tag, bad JSON, truncation)?

Ratatui async patterns: use a tokio mpsc event stream and render in a tight loop; see Ratatui async tutorial for reference.
