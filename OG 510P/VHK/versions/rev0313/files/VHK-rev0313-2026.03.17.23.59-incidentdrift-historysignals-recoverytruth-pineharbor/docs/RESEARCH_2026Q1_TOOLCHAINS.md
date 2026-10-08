# Research notes: Linux automation toolchains (March 2026)

This note captures the practical product lessons behind the `toolchain_choices`
planner surface.

## Key observations

### 1) X11 still rewards direct desktop automation tooling

For X11-shaped targets, it still makes sense to think in terms of tools like:

- `xdotool` for keyboard/pointer automation
- `wmctrl` / `xprop` / `xwininfo` for window metadata
- WM binds / `sxhkd` for dispatch

These are still the closest match to the broad “AHK-like” desktop-ownership
model on Linux.

### 2) Wayland text injection and pointer injection are different problems

A recurring Linux desktop mistake is to talk about “Wayland input” as though it
were one thing.

In practice, the useful split is:

- text injection: virtual-keyboard / clipboard-first paths (`wtype`, exports,
  snippet tiers)
- pointer injection: helper/uinput/portal-boundary work (`ydotool`, `dotool`,
  helper processes, portal/session flows)

That split is exactly why VHK should keep text-tier and helper-boundary stories
separate.

### 3) Portals remain capability routing, not just API presence

Current portal documentation still treats routing as per-interface and desktop-
specific. A session may have a functioning portal stack while still differing by
interface or backend choice.

That means VHK should keep modeling:

- screen capture
- global shortcuts
- remote desktop / pointer paths
- input capture

as distinct capabilities.

### 4) Remappers are still their own product class

Tools like keyd, Kanata, KMonad, and xremap keep validating the same lesson:
low-latency remapping, tap-hold behavior, layers, and app-specific key behavior
should usually live in dedicated remap layers or generated configs, not be
forced into the macro runner.

## Product implication for VHK

VHK should keep growing as:

- a strong runner / macro language
- a Linux-native dispatch/export/generation toolchain
- a planner that helps choose the right external surfaces instead of pretending
  every project should use the same backend everywhere
