# VHK vault

This directory holds work that is intentionally **preserved but demoted**.

The current active repo story is:

- i3/X11 first
- session-bound long-lived user service
- recorder/cleanup/replay as the center of gravity
- ad hoc CLI launches still supported
- private-LLM-authored VHK scripts as a first-class use case

## Contents

### `vault/docs/`
Historical or experimental documents that are no longer part of the active
headline story.

Current categories:

- Wayland / portal / compositor-specific notes
- app-native adapter research

## Code status

The live CLI still contains imports and commands for some of these lanes.
That code has **not** been removed in revision 0325, because the current pass is a
safe datacube reshape rather than a risky code-pruning pass.

A later revision can move or delete code once import boundaries and command
surfaces are trimmed deliberately.
