# Research note — relative recording and CoordMode patterns

Date: 2026-03-18

## Why this note exists

VHK already had a runtime `CoordMode` implementation plus window-geometry probes,
but the recorder still emitted absolute screen coordinates. That kept recorded
macros closer to xmacrorec-style playback than to the practical Window Spy /
Pulover workflow that many AutoHotkey users rely on.

## Product lesson

The lesson from AHK and Pulover is not merely "show some coordinates". It is:

1. help the author see which coordinate space they are using
2. keep window scope adjacent to pointer capture
3. make relocatable coordinates easier than raw screen math when the target
   workflow naturally lives inside one stable window

## What changed in VHK

Revision 0316 threads that lesson into `vhk record-x11` itself:

- active-window capture can now carry geometry snapshots, not only selector-ish
  identity fields
- recorder output can be rewritten into `CoordMode(target=mouse, mode=window)`
  or `CoordMode(target=mouse, mode=client)` form
- the same sidecar payload that already held selector suggestions can now also
  preserve the chosen relative mouse anchor
- `client` mode stays honest and falls back to the outer window rect when Linux
  tooling cannot expose a distinct client rectangle

## Why this is the Linux-native move

Linux automation is fractured across X11, Wayland, accessibility stacks, and
app-native protocols. That makes it especially important to distinguish:

- absolute screen replay
- active-window-relative replay
- semantic UI control

VHK should not flatten those together. Relative recording is valuable because it
reduces fragility for window-local tasks, but it does not replace semantic UI
controls or route-native adapters.

## Remaining gaps

- no Studio-side visual review for the chosen coordinate anchor yet
- no per-step mixed coordinate-space editing yet
- no live "this window moved during recording" review UI beyond the captured
  geometry consistency flag
- no Wayland-native lexical recorder equivalent yet
