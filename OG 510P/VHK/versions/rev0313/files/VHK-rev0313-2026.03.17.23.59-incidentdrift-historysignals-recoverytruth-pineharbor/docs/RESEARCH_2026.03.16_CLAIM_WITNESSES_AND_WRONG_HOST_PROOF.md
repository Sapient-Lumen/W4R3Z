# Research — claim witnesses and wrong-host proof

## Why this matters

A Linux automation project can easily end up with two incompatible truths:

- a target lane that looks supportable in planner/release output
- a current workstation that is not actually the right evidence machine for that
  lane

That mismatch is especially dangerous on Wayland because desktop family and
portal backend reality both matter. A sway/Hyprland host can be perfectly valid
for its own remapper-first story while still being weak or misleading evidence
for a GNOME/KDE portal-first claim.

## Lessons from others

- AutoKey still keeps its core support story tied to Linux/X11 rather than
  pretending every Linux desktop is equivalent.
- Espanso keeps application/config precedence explicit instead of flattening all
  contexts into one active truth.
- xdg-desktop-portal explicitly separates frontend interfaces, backend routing,
  and backend implementations.
- libei/EIS documents that input transport and input-capture/session logic are
  separate layers.

Those are all product-shape lessons for VHK: keep evidence boundaries explicit
and do not let a local run silently become proof for the wrong lane.

## Product direction added in this revision

Claim-facing surfaces now distinguish between:

- the planner recommendation for a lane
- the current host as a witness for that lane

That witness review is intentionally compact:

- `aligned`
- `degraded`
- `drifted`
- `neutral`
- `unknown`

This is not meant to be perfect desktop emulation. It is a discipline layer that
prevents one common mistake: treating the wrong Linux host as verified evidence
for a stronger support claim.

## Immediate follow-through

- planner/promotion surfaces should learn the same witness posture
- publish/support snippets should eventually be able to quote witness status
- operator-selected evidence hosts/lanes should become first-class when VHK
  starts tracking reviewed flagship environments more formally
