# Research — WezTerm CLI packs and pane identity boundaries

## Core lesson

WezTerm already exposes a pane-aware CLI for sending and retrieving text. That makes it a better fit for a thin app-native adapter pack than for generic desktop typing replay.

## What VHK should learn

- `wezterm cli send-text` is a pane operation, not a generic window-text operation
- `wezterm cli get-text` is a real capture surface and should remain on the WezTerm side of the seam
- `wezterm cli list --format json` is good enough for a reviewable pane-discovery fallback when VHK only has title evidence
- ambiguous pane discovery should fail loudly instead of guessing

## Product implication

VHK should export thin WezTerm helper wrappers rather than embedding terminal-control logic into the core runner. The runner should keep owning macro semantics, while the generated pack keeps pane targeting and capture reviewable.
