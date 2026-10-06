# RFC-0146: Location portal (geolocation)

Status: **Draft**  
Last updated: 2026-02-24

## Problem

Location APIs are high-signal privacy surfaces. Ambient access breaks containment and makes “deny by default” unrealistic.

## Proposal

Add an optional **Location portal** lane:

- requests specify desired accuracy class and cadence
- broker mediates consent and downgrades accuracy if needed
- outputs are receipted for auditability

Evidence objects:
- `ui.location.grant`
- `ui.location.receipt`

## Policy

- deny by default
- “precise” requires explicit prompt even if coarse is remembered
- hardened profiles can disable the portal family (lockdown)

## References

- XDG Location portal: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Location.html
