# RFC-0143: ScreenCast + RemoteDesktop portals (screen sharing + remote control)

Status: **Draft**  
Last updated: 2026-02-24

## Problem

Screen sharing and remote control are common workflows, but they are also:
- high-power exfil channels (screen capture)
- high-power integrity channels (input injection)

If they are ambient, sandbox boundaries become decorative.

## Proposal

Add an optional “UI capture/control as authority” lane:

- a host broker mediates user selection and consent
- apps receive **leased** grants for:
  - screencast sessions (`ui.screencast.grant`)
  - remote desktop control sessions (`ui.remotedesktop.grant`)
- receipts are available as a policy knob:
  - `ui.screencast.receipt`
  - `ui.remotedesktop.receipt`

Design constraints:
- always-on non-spoofable indicator for active capture/control
- remote input injection must integrate with secure attention (SAK) and be focus-scoped

## Spec objects

- `ui.screencast.grant`, `ui.screencast.receipt`
- `ui.remotedesktop.grant`, `ui.remotedesktop.receipt`

See: `docs/208-screencast-and-remote-desktop-portals.md`.

## Prior art

- XDG Desktop Portal ScreenCast interface:
  https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.ScreenCast.html

- XDG Desktop Portal RemoteDesktop interface:
  https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.RemoteDesktop.html

- libportal screencast overview (PipeWire stream transport):
  https://libportal.org/libportal.html

- PipeWire portal access control notes:
  https://docs.pipewire.org/page_portal.html

## Open questions

- whether to standardize “virtual monitor” creation as a separate capability
- how to make indicator overlays non-spoofable across compositors and remote consoles
- whether receipts should include a stable session id usable for incident triage
