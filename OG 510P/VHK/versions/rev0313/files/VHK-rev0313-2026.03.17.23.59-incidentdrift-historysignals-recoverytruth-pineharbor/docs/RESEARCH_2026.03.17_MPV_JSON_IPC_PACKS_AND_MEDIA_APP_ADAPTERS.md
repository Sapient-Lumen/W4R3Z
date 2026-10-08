# Research — mpv JSON IPC packs and media app adapters

## Current lesson

mpv is a good example of why VHK needs concrete app-native adapter packs instead
of stopping at planner vocabulary.

Its official manual already points away from fake terminal/input simulation and
explicitly recommends JSON IPC for interactive control via
`--input-ipc-server` / `--input-ipc-client`.

That makes mpv a strong media-native adapter seam.

## What changed in VHK

This revision adds `vhk gen-mpv-pack` as the first concrete export for the
app-native media lane.

The pack intentionally stays narrow:

- it exports only mpv-targeted macros
- it only emits routes when names, descriptions, or binding keys imply a
  reviewable command such as pause, stop, next, previous, seek, volume, mute,
  or fullscreen
- it keeps socket ownership/operator review explicit instead of pretending VHK
  has already become an mpv session manager
