# Research notes — promotion evidence and checked-in proof

## What changed my mind this pass

The previous planner work already did a good job of answering:

- what Linux-native lane a macro wants
- what export surfaces a project wants
- which of those surfaces are ready, review, or blocked
- what gates and backlog tasks should happen next

But strong Linux-native tools are not judged only by route choice. They are judged by whether the project can **show its work**.

That matters on Linux because:

- input and trigger behavior still diverge heavily by X11, Wayland, compositor, and helper stack
- portal behavior still depends on backend routing and session objects
- text, remap, watcher/service, and helper-boundary ownership are still different product lanes

So the planner needed one more layer: **which checked-in artifacts should exist before a surface/gate counts as release-proof?**

## What current upstream tools reinforce

Espanso still documents Wayland support as experimental on Linux and says app-specific configurations are not yet supported on Wayland. That means text-surface posture cannot be treated as generic parity; setup and verification proof should remain explicit.

keyd still frames itself as a system-wide daemon using `evdev`/`uinput`, and xremap still frames itself as app-specific remapping for X11 and Wayland. That reinforces the idea that remapper lanes are their own product surface and need their own review/setup proof instead of piggybacking on runner claims.

The portal docs still emphasize backend/session routing and configuration (`portals.conf`). That means helper-sensitive lanes need checked-in host/route/claim artifacts, not just planner prose.

## Resulting VHK rule

Promotion work should not stop at:

- route ownership
- surface readiness
- gates
- backlog

It should also emit:

- the proof artifacts the repo should contain
- whether that proof is complete, partial, or missing
- lint signals when release posture outruns checked-in evidence

## Practical implication

This revision treats generated docs/plans/manifests as part of the product surface itself. For VHK, a Linux-native release is not only code plus macros; it is also a reviewed proof bundle that makes support claims auditable.
