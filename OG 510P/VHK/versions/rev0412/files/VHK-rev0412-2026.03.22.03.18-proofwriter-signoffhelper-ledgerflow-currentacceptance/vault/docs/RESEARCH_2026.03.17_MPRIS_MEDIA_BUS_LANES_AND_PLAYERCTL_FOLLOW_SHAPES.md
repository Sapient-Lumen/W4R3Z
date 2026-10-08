# Research — MPRIS media bus lanes and playerctl follow shapes

## Takeaway

A Linux-native automation stack should treat media control as a bus contract before it treats it as a hotkey replay problem.

## What we learned

- MPRIS gives Linux media players a shared D-Bus contract for transport control, metadata, and state updates.
- `playerctl` proves the value of a thin adapter over that contract: one CLI for control, one `--follow` mode for state streams, and `playerctld` for recent-player selection.
- That means VHK should model media workflows as a reviewable service-bus lane whenever the project is already waiting on `org.mpris.MediaPlayer2*` signals.

## Product implication

`plan-project` should surface an explicit MPRIS lane instead of leaving the media story buried inside generic D-Bus/event-driven guidance. The right architecture is:

1. MPRIS / playerctl owns bus-level selection and state follow semantics
2. VHK owns macro orchestration, diagnostics, prompts, and artifacts
3. replay remains the fallback for players that do not expose the standard contract

## Honest gap

Planning is ahead of deployment here: VHK now recognizes the lane, but it still needs a thin export/generator story for concrete playerctl/MPRIS handoffs.
