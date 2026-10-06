# RFC-0144: Camera + audio capture portals (AV devices)

Status: **Draft**  
Last updated: 2026-02-24

## Problem

Camera and microphone access are privacy-sensitive and frequently abused.
Traditional UNIX exposure (device nodes + group membership) is ambient authority.

The ecosystem also struggles with coherent microphone mediation: camera portals exist, audio portals are still evolving.

## Proposal

Add an optional AV capture lane:

- host broker mediates user consent and device choice
- apps receive leased grants:
  - camera capture (`ui.camera.grant`)
  - audio capture (`ui.audio.capture.grant`)
- optional receipts for high-assurance environments:
  - `ui.camera.receipt`
  - `ui.audio.capture.receipt`

Design constraints:
- foreground and purpose constraints are first-class policy inputs
- mandatory capture indicators
- transport is an opaque stream handle (PipeWire remote FD or DeriveBSD-native stream object)

## Spec objects

- `ui.camera.grant`, `ui.camera.receipt`
- `ui.audio.capture.grant`, `ui.audio.capture.receipt`

See: `docs/209-camera-and-audio-capture-portals.md`.

## Prior art

- XDG Desktop Portal Camera:
  https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Camera.html

- PipeWire security posture + container/sandbox emphasis:
  https://pipewire.org/

- Microphone portal request:
  https://github.com/flatpak/xdg-desktop-portal/issues/615

- Audio portal discussion:
  https://github.com/flatpak/xdg-desktop-portal/issues/1129

- Mozilla: no microphone portal yet:
  https://bugzilla.mozilla.org/show_bug.cgi?id=1726218

## Open questions

- whether to split “microphone” and “other audio capture” (e.g., loopback) into separate grants
- how to represent per-device selection and “default device” semantics stably
- whether capture receipts should be required for certain trust tiers
