# Research note: macro route ownership and Linux tool lessons (2026-03-16)

This pass focused on one design question that matters if VHK wants to feel as
useful on Linux as AHK has been on Windows:

> which lane should own each macro?

Project-level plans were already strong, but the repo still needed a more
explicit answer per macro.

## What other Linux tools keep teaching

### 1) Text automation wants its own lane

Espanso keeps reinforcing that snippet automation is not just “type this text”; it
is package/config/app-filter/form logic with a distinct product surface.

VHK implication:

- hotstring- or text-expander-shaped macros should be visible as **text-tier**
  routes
- structured or long typed text should stay eligible for clipboard/hybrid lanes
  instead of being trapped as per-character replay

### 2) Low-latency remapping is a different product than macro replay

keyd, xremap, kanata, KMonad, and related remapper ecosystems keep proving the
same point: ergonomic key transforms, app-specific remaps, and tap-hold logic
want to live near evdev/compositor boundaries.

VHK implication:

- remap-like macros should be called out explicitly as **remapper-tier**
  candidates
- the runner should stay the fallback / orchestration engine, not the thing that
  impersonates a remapper everywhere

### 3) Event-driven workflows want a service owner

Linux-native automation often gets better when DBus, file, clipboard, or WM
signals enter through watchers or user services and only hand off to the runner
for real work.

VHK implication:

- watcher-triggered macros should surface as **watcher-service** routes
- route ownership should name the service/watcher lane directly instead of
  flattening everything into “macro execution”

### 4) Wayland pointer/capture flows still need an honesty boundary

Portal and helper progress matters, but pointer injection and capture on Wayland
still vary by desktop, backend, helper, and session wiring.

VHK implication:

- helper-sensitive macros should surface as **helper-boundary runner** routes
- the macro plan should say out loud that these flows depend on helper seams and
  route selection, instead of pretending the macro language itself guarantees
  portability

### 5) Launch surfaces are a real product tier

Tools like launcher/palette/radial-menu systems keep showing that many workflows
are better launched deliberately than hidden behind another resident hotkey.

VHK implication:

- palette-only or manually launched workflows should surface as **launcher-entry**
  routes
- shipping artifacts should keep desktop-entry / launcher-script / palette
  surfaces first-class

## What was implemented from this lesson

`vhk plan-project --json` now emits `macro_route_profiles`, which make route
ownership explicit per macro.

Each profile now states:

- the route id and title
- the owning layer
- the execution surface
- the primary activation route chosen from the project's route matrix
- fit / evidence / risks
- tools VHK should learn from for that macro shape
- concrete next commands

This does not replace stack profiles or activation routes. It connects them to
the part authors actually edit every day: the macro list.

## Why this matters for VHK's AHK ambition

AHK on Windows feels powerful partly because one environment can own a huge
range of automation affordances directly.

Linux is different.

A serious Linux-native AHK-like system needs to win by **composition**:

- text lane where text tools are strongest
- remap lane where remappers are strongest
- watcher/service lane where Linux events are strongest
- helper seam where Wayland remains conditional
- runner core where sequencing/orchestration/diagnostics are strongest

The new route-profile surface is a small but important step toward that product
shape.
