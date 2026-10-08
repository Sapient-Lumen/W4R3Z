# Research note — 2026-03-18

## Topic

How VHK should keep chasing AutoHotkey/Pulover-style usefulness on Linux
without pretending Linux desktop automation has one universal trigger or input
lane.

## What the external landscape reinforced

- Pulover's Macro Creator still represents the bar for recorder-driven authoring:
  record relative-to-window or screen coordinates, step through playback, keep
  hotkeys always reachable, and expose a large step catalog. VHK should keep
  matching that authoring clarity even when Linux backends vary.
- X11 still has a straightforward direct-input lane (`xdotool`-class) and those
  tools already model repeated clicks explicitly, which is a good fit for VHK
  recorder cleanup and `MouseClickAt(clicks=...)`.
- Wayland remains plural, not singular:
  - `wtype` is excellent for text and key-oriented virtual-keyboard sequences
  - `ydotool` is broader but helper-daemon shaped
  - portal GlobalShortcuts is a real session-owned trigger lane, but not a
    universal answer to every dynamic hotkey problem
  - libei/EIS is promising, but still belongs in an explicit compositor/session
    authority lane
- xremap-like remapper stacks reinforce the same lesson: they can be fast and
  app-aware, but they also depend on evdev/uinput ownership and sometimes
  desktop-specific app-context plumbing.
- AT-SPI remains a serious Linux-native semantic automation lane, not just an
  accessibility side topic. GTK/AT-SPI roles, states, and actions provide a more
  semantic control surface than blind replay whenever the target app cooperates.

## Spec pressure for VHK

1. Keep the authoring model unified, but keep runtime/export lanes explicit.
2. Preserve a thin hot path for the fastest trigger/replay surfaces.
3. Treat semantic UI control as a first-class lane beside vision and raw input.
4. Preserve repeated-click intent explicitly in the step model.
5. Keep install/planner docs honest about authority boundaries.

## Concrete repo follow-up in this revision

- added explicit multi-click `MouseClickAt` support
- taught the optimizer to collapse repeated click runs into one multi-click step
- documented the new step fields and optimizer flags
- added focused tests around coordinate translation and optimizer CLI behavior

## Follow-up issues to keep alive

- expose multi-click editing/inspection directly in future Studio surfaces
- keep AT-SPI inspectors and selectors on equal footing with vision selectors
- keep portal/helper/remapper/app-native lanes separate in planning and install
  guidance
- keep the hottest low-latency paths out of unnecessary Python/control-plane
  layers where a thinner native/exported lane can own the trigger
