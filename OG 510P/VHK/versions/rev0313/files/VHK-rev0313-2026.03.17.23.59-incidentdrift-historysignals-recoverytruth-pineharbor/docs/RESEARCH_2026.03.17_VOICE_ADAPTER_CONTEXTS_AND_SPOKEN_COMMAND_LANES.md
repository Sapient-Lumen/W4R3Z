# Research — voice adapter contexts and spoken-command lanes

## Current lesson

Linux voice automation is already split across at least two real layers:

- the speech tool owns recognition, grammar/context activation, and often some
  local action vocabulary
- the target automation tool owns the larger action catalog and execution
  semantics

That means VHK should not treat voice as “another generic trigger backend.” It
should keep voice adapter-shaped.

## Concrete lessons from current adjacent tools

### Talon

Talon's `.talon` files are already context-aware artifacts: they can match app
name/title criteria and declare voice commands and hotkeys.

Product lesson for VHK:

- keep exported spoken commands literal and reviewable
- keep app/title context visible in generated artifacts
- do not copy VHK macro semantics into Talon scripts when a stable command id
  handoff will do

### Dragonfly

Dragonfly already models grammars/contexts/actions as first-class Python-side
objects, but on Linux its input/window action story remains X11-leaning.

Product lesson for VHK:

- keep Dragonfly export explicit about X11/session fit
- keep voice support framed as an adapter lane rather than universal Linux voice
  parity
- preserve generated ledgers and lint warnings so phrase/context drift can be
  reviewed like any other deployment artifact

## Resulting VHK design rule

Planner output should surface a dedicated voice lane whenever a project already
contains deliberate spoken metadata (`voice_phrases`, `voice_when`) instead of
waiting until pack generation to reveal that design choice.

That is why revision 0277 adds:

- `voice-command-adapter`
- `voice-context-command-lane`
- `voice-tools-own-recognition-context`

## Remaining follow-up

- feed voice-lane prerequisites into doctor/readiness/setup surfaces
- add better pronunciation/homophone review guidance
- add Studio/inspector help for assigning/testing spoken phrases and contexts
