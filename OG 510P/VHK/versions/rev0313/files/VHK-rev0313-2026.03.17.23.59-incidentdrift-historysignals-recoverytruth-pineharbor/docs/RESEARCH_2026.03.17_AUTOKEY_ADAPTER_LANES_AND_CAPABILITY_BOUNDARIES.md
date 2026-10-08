# Research — AutoKey adapter lanes and capability-boundary lessons

Date: 2026-03-17

## Why this note exists

VHK already had an AutoKey exporter, but the planner still mostly described
text automation through Espanso-style exports and generic launcher/remapper
surfaces. That left one useful Linux-native lesson under-modeled:

- X11 still benefits from a **reviewable adapter lane** for text + trigger
  workflows
- Wayland capability work still wants **explicit boundaries** rather than a
  fake generic backend story

## Online lessons worth preserving

### 1) AutoKey is still explicitly Linux/X11

Official AutoKey docs still describe the product as an automation utility for
**Linux and X11**, and they explain that its core works by sending/receiving
keyboard events via the X server.

Useful product lesson for VHK:

- keep AutoKey as an **honest X11 lane**, not a generic Linux promise
- preserve VHK as the runtime/authoring model while exporting a reviewable
  adapter pack when X11 projects want that shell

Source links:

- https://autokey.github.io/intro.html
- https://github.com/autokey/autokey/issues/865
- https://github.com/autokey/autokey/issues/1042

### 2) AutoKey's window model stays coarser than VHK's selector model

AutoKey's Window API is still oriented around title matching plus an optional
`matchClass=True` switch, which reinforces the existing VHK export-honesty
rule: do not silently pretend a multi-field VHK selector survives intact once
it crosses into AutoKey.

Useful product lesson for VHK:

- keep selector-loss warnings visible in lint/planner/export docs
- keep scoped AutoKey export conservative and reviewable

Source links:

- https://autokey.github.io/api/window.html

### 3) xremap remains a strong Linux-native remap reference, but it is a different lane

xremap still positions itself as a Linux key remapper for X11 and Wayland with
app-specific remapping, key sequences, and desktop/backend-specific feature
builds.

Useful product lesson for VHK:

- keep xremap/remapper planning separate from AutoKey adapter planning
- do not collapse "reviewable X11 adapter" and "low-latency remap owner" into
  one generic trigger story

Source links:

- https://github.com/xremap/xremap

### 4) libei/EIS still argues for helper-boundary modeling

The libei documentation still frames emulated input as a client/server contract
between an EI client and an EIS implementation, typically inside the Wayland
compositor stack, with `liboeffis` as a helper library for DBus communication
with the XDG RemoteDesktop portal.

Useful product lesson for VHK:

- keep helper/session seams explicit for Wayland-class pointer/input work
- avoid claiming the Python runner itself is the transport layer

Source links:

- https://libinput.pages.freedesktop.org/libei/

### 5) GNOME 48 reinforces portal-first shortcut lanes, not universal parity

GNOME 48's developer notes say global shortcuts are now supported and fully
available through the portal stack. That is important, but it is still a
**desktop-specific lane** rather than proof that every Wayland desktop now has
uniform trigger semantics.

Useful product lesson for VHK:

- keep portal-global-shortcuts as a scored candidate
- continue showing alternative lanes and capability audits for desktops where
  portal coverage differs

Source links:

- https://release.gnome.org/48/developers/

## Repo consequence in REV0269

Planner/output consequences that follow from the research above:

- add an explicit `autokey-x11-adapter` candidate integration surface
- add an `autokey-reviewable-adapter` planner pattern
- thread `vhk gen-autokey-pack ...` into text-tier macro route guidance for
  X11-class projects
- keep Wayland capability-boundary language intact instead of letting the new
  X11 adapter work blur Linux-wide claims
