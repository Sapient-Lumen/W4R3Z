# Research — promotion startup routes and lifecycle ownership

## Why this note exists

VHK already had an input-lane dossier and promotion shipping-lane map. The next
question was whether Linux prior art also implies a separate startup/lifecycle
map.

The answer is yes.

## Outside lessons

### Espanso keeps text automation in an explicit service/autostart lifecycle

Espanso documents a dedicated Linux service surface with commands for checking,
registering, starting, stopping, and restarting the service, including service
registration for auto-start on boot/login. That is a strong hint that text
shipping surfaces should not be modeled only as “text injection exists”; they
also need a startup owner.

### Xremap keeps remapping in a low-latency resident/remapper lifecycle

Xremap still presents itself as an `evdev`/`uinput`-based remapper for X11 and
Wayland, with app-specific remapping, device watching, and key-triggered
commands. That is closer to a resident remapper lane than to an ordinary
one-shot macro launcher.

### Portal shortcut/input flows are session-bound, not generic hotkey daemons

The GlobalShortcuts portal requires applications to create a session, bind
shortcuts under that session, and then receive Activated/Deactivated signals.
InputCapture is even more explicit: it distinguishes “enabled” from “active”,
uses triggers, and delegates transport to libei. Both reinforce that portal
activation is a lifecycle contract, not just a capability checkbox.

### Background/autostart is its own portal truth surface

The Background portal explicitly lets sandboxed apps request background activity
or autostart at login. That supports VHK keeping startup/service ownership as a
first-class review surface instead of assuming the same activation story works
for launcher, service, and portal/session deployments.

## Product implication for VHK

Promotion review should not stop at:

- which export surface exists
- which input lane owns shipping

It should also answer:

- which activation route owns startup?
- is the surface resident, session-bound, launcher-first, or review-led?
- which requirements belong to startup ownership versus input ownership?

That is the reason for `promotion_activation_route_plan`.
