# Research — authority envelopes and layered Linux ownership

Recent review of prior art kept reinforcing the same point: Linux automation
surfaces differ not only by speed or features, but by who actually holds
authority on the machine.

## Repeated lessons

1. Text expansion is usually a user-session service/config problem.
   Espanso continues to expose start/status/restart/service management as a
   first-class Linux surface.

2. X11 shell automation remains meaningfully distinct from Wayland/session
   automation.
   AutoKey still frames itself as an X11 utility, which is a useful reminder not
   to collapse X11 shell authority into generic Linux authority.

3. Portal shortcuts and portal sessions are desktop-mediated, not process-local.
   XDG GlobalShortcuts and related session APIs keep emphasizing session objects,
   binding flows, and backend mediation.

4. Remappers and helper daemons keep pushing authority toward evdev/uinput,
   service lifecycle, socket policy, and `/dev/uinput` access.
   keyd, ydotoold, and similar tools keep making that boundary explicit.

## Product implication for VHK

Planner and promotion review should say which layer owns authority per promoted
surface, not only which surface is warm or which one starts first.

That is the role of `promotion_authority_envelope_plan`.
