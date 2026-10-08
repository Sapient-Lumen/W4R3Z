# Research notes — deployment lifecycle lessons (2026 Q1)

This note captures a simple product lesson from the current Linux automation
landscape: **deployment readiness is more than package installation**.

## Adjacent-tool lessons VHK should keep learning from

### Espanso

- The install story is split across packaging, service registration/start, and
  Wayland capability grants.
- That means a text surface should not be modeled as “binary present = done”.

### xremap

- The project is strong at app-specific remapping and Wayland reach, but the
  operator story still branches into:
  - `sudo` vs non-`sudo`
  - `input` / `uinput` policy
  - GNOME-specific app-context setup
- That reinforces VHK's choice to keep remappers as explicit helper seams.

### keyd / kanata / kmonad

- These tools win by owning a narrow low-latency edge.
- Their install stories still depend on service wiring, permission policy,
  config placement, and restart behavior.
- VHK should keep separating generated configs from lifecycle claims.

### ydotool

- The daemon/socket split is a real deployment seam, not a detail.
- A project can “have ydotool installed” while still being unusable because the
  socket is absent or `/dev/uinput` is not writable.

### XDG desktop portals

- Portal support is an interface matrix plus a backend-routing/config problem.
- `GlobalShortcuts` is also session-oriented by design, which fits stable action
  catalogs better than infinitely dynamic macro bindings.

## Product takeaway for VHK

The repo should keep a layered model:

- planner/design language for what the project wants
- host contract language for what the host must provide
- readiness proofs for what is actually live on this machine right now

That is a better Linux-native shape than pretending one export or one helper can
stand in for the whole runtime.
