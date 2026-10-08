# Research — promotion lanes and shipping ownership

## Question

How should VHK connect project-level promotion surfaces to the Linux-native
runtime lanes they actually depend on?

## What current Linux tools keep teaching

### 1. Text packaging and app scoping are their own product surface

Espanso continues to treat app-specific behavior as explicit configuration,
including inherited app-specific configs plus include/exclude rules. That means
“ship this as text automation” is not the same design problem as “ship this as
generic key replay”.

Design implication for VHK:

- `text-package-export` should be able to lead with a clipboard/text-surface
  lane instead of silently inheriting whatever general input backend happens to
  look strongest.

## 2. Wayland remapping is still lane-shaped, not universal

xremap still describes itself as a Linux key remapper for X11 and Wayland,
explicitly built around `evdev`/`uinput`, with compositor-specific build
features and app-specific remapping support.

Design implication for VHK:

- remapper-style promotion belongs near a specialist low-latency input lane,
  not inside a generic “send keys” abstraction
- on Wayland, that usually means keeping daemon/helper-backed repeated playback
  and session-specific review visible

## 3. Portal input remains permissioned and session-owned

The InputCapture portal still distinguishes between an **enabled** state and an
**active** state, with the compositor deciding when activation actually happens.
The RemoteDesktop portal still exposes explicit keyboard/pointer notification
methods that are only available when the corresponding access was granted to the
session.

Design implication for VHK:

- helper-boundary shipping surfaces should stay explicitly review-led around
  permissioned portal lanes instead of being flattened into a generic “Wayland
  input works” story

## 4. libei is still a client/server stack, not a magic checkbox

The current libei docs continue to frame emulated input as a client/server model
with UNIX-socket transport, plus `liboeffis` as a helper for the XDG
RemoteDesktop portal.

Design implication for VHK:

- Linux-native shipping decisions should be able to say “this surface is owned
  by a portal/session/helper lane” rather than implying that all future Wayland
  input eventually collapses into one interchangeable backend

## Resulting product lesson

VHK should not stop its planner at export surfaces alone.

It should also emit a project-level map that says which input lane should own
those exports:

- text packages → clipboard/text-surface flagship lane
- remapper exports → specialist low-latency replay/remap lane
- helper dossiers → reviewed portal/helper lane
- watcher/launcher surfaces → orthogonal to primary input ownership

That is what `promotion_input_lane_plan` is for.
