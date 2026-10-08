# Window contracts

VHK now treats Linux window usage as a **contract**, not just a boolean
"window introspection" checkbox.

That contract answers questions such as:

- does this project only need title/class/app matching?
- does it depend on stateful selectors like `sticky`, `floating`, or
  `fullscreen_mode`?
- does it require window geometry, or only sample it when available?
- does it depend on the "window under the pointer" lane?
- does it scope windows by PID?

## Why this exists

Linux window tooling is real but uneven:

- sway/i3 can expose rich state directly through their tree/IPC
- X11 can derive some state through EWMH helpers
- Hyprland can expose useful state, but `hyprctl` is still synchronous and not a
  thing to spam in tight loops
- KDE Wayland via `kdotool` can expose some `windowstate` properties, but not
  all of them

So a project that says "I need window introspection" is often underspecified.
A project that says "I need sticky/fullscreen matching plus geometry plus
pointer-window sampling" is much easier to route, validate, and support.

## Current surfaces

- `vhk plan-project --json` now includes `window_contract`
- `vhk validate` now emits extra `session_window_contract` warnings when the
  current desktop can see windows in general, but cannot honestly guarantee the
  specific state/geometry/pointer-window semantics the project asks for
- `vhk doctor --json` now includes
  `session_capabilities.window_introspection.window_contract_support`

## Shape

The current contract summary tracks:

- selector sites and examples
- state fields used (`visible`, `fullscreen`, `floating`, `sticky`, etc.)
- identity fields used (`workspace`, `wm_class`, `app_id`, etc.)
- PID-scoped selectors
- geometry requested vs geometry required
- pointer-window steps and strict pointer-window requirements

This is intentionally conservative. VHK is trying to say what a project *really
needs from the host*, not inflate backend claims.
