# Stack profiles for Linux-native automation

VHK is trying to solve a bigger problem than “replay this key sequence”.
A Linux-native automation stack is usually split across **multiple layers**:

- a thin trigger layer
- a macro/runtime layer
- optional visual selector assets
- optional event/watcher services
- optional text-export surfaces
- optional low-level remappers

`vhk plan-project` now exposes this more directly through **architecture maps**, **deployment profiles / stack profiles**, **runtime seams**, and **ecosystem lessons**.

## Why the split matters

The surrounding Linux ecosystem keeps teaching the same lesson:

- text tools like Espanso treat forms, variables, and app scoping as a real
  product surface
- low-level remappers like keyd, kanata, kmonad, and xremap win by staying
  close to evdev/compositor layers instead of acting like a full macro engine
- portal/libei/EIS work on Wayland is valuable, but still capability- and
  backend-dependent enough that projects need explicit adapter seams

That means VHK should not force every workflow into one always-on Python
process. In many cases, the right architecture is:

- **thin dispatch** outside the runner
- **strong sequencing/diagnostics** inside the runner
- **exports/helpers** for the surfaces that want lower latency or tighter
  desktop integration

## Current profile shapes

`plan-project` now emits a set of scored profiles.

### Text-first export profile

Best fit when the project’s visible product is:

- snippets
- hotstrings
- forms
- structured replies
- app-scoped text automation

Typical stack:

- trigger surface: hotstrings or a small launcher/hotkey layer
- execution surface: prompt-aware text macros
- export surface: espanso-style package generation and include/exclude rules

### Selector-driven runner profile

Best fit when the project is mostly:

- image matching
- OCR waits
- bounded click-through flows
- “recorded draft cleaned into selector assets”

Typical stack:

- trigger surface: one-shot launch into the runner
- execution surface: selector assets + diagnostics
- export surface: preview data, named regions, run reports

### Watcher-daemon profile

Best fit when the project wakes up because:

- DBus signals
- clipboard changes
- window changes
- socket or service events

Typical stack:

- trigger surface: user services / emitters
- execution surface: VHK bus + runner
- export surface: generated systemd user units

### Remap-integrated profile

Best fit when the project needs:

- tap-hold
- layers
- ergonomic remapping
- ultra-fast always-on key interception

Typical stack:

- trigger surface: remapper/compositor bind
- execution surface: short launch into VHK
- export surface: keyd / kanata / kmonad / xremap-class configs

### Wayland helper-boundary profile

Best fit when a Wayland-facing project also needs:

- pointer control
- global hotkeys
- capability-aware deployment
- session-specific helper fallback paths

Typical stack:

- trigger surface: compositor binds or portal shortcuts when genuinely present
- execution surface: VHK behind helper / portal / uinput / future-libei seams
- export surface: deployment-profile manifests and doctor/validate reports

## The design principle behind these profiles

The profiles are **not** meant to pigeonhole a project into one bucket.
They exist to make a mixed stack explicit:

- what should be always-on?
- what should be exported?
- what should be packaged as a service?
- what should stay in the VHK runtime because that is where sequencing,
  retries, logging, and diagnostics are strongest?

That is the path toward a Linux-native AHK-like product without pretending the
Linux desktop has one universal automation API.


## Desktop target matrix

`plan-project` now also emits a **desktop target matrix**.

This is deliberately more opinionated than the stack profiles: it tries to say
which *desktop landing zones* are realistic for the current project, and which
ones should be treated conservatively.

Current targets include:

- **Portable text/export**: lean on hotstrings, forms, prompt profiles, and
  exported text packages.
- **X11 tiling-native**: explicit i3/X11-style target for projects chasing the
  least constrained classic desktop automation feel.
- **Portal-centric Wayland**: treat portals as a capability matrix and keep the
  runner above explicit permission/session flows.
- **Helper-boundary Wayland**: isolate injection/interception behind helpers so
  backend churn does not leak into macro logic.
- **wlroots/Hyprland conservative**: bias toward compositor binds, watchers,
  text surfaces, and explicit capability checks instead of claiming generic
  RemoteDesktop/InputCapture parity.

The point is not to lock the project into one desktop forever. The point is to
force VHK to make honest product promises.


`vhk gen-design-pack` packages those same outputs into a checked-in design brief and runtime contract so project teams can review the layer split without scraping terminal tables.
