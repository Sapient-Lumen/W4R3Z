# Research notes: activation lanes (2026 Q1)

This note captures the planner-level product lesson behind the activation-pack
work.

## Main lesson

Linux automation stacks do not only differ by capability. They also differ by
**activation ownership**:

- launchers wake work on demand
- text expanders stay alive as user services
- remappers own low-latency key interception
- helper daemons own sockets and device access
- portals own session-bound consent/configure flows

That means a Linux-native VHK cannot stop at "recommended helper" or "package
group". It also needs to say:

- who starts this lane?
- what keeps it alive?
- what host contracts gate it?
- what is the fallback route?

## Ecosystem pattern carried into VHK

- AHK/Pulover still point toward a strong stateful runtime core.
- Espanso shows that text automation is a packaging + lifecycle surface, not
  only a string-replacement trick.
- keyd / kanata / xremap reinforce that hotkey ownership and interception often
  belong in dedicated low-latency lanes.
- portals reinforce that some Wayland-era integrations are session-bound and
  need explicit bind/configure flows instead of silent background hooks.
- ydotool reinforces that helper socket lifecycle is part of the deploy story.

## What changed in VHK

`plan-project` now emits `activation_routes`, and `vhk gen-activation-pack`
turns those routes into operator-facing docs, a machine-readable plan, and a
refresh script.

That keeps the next design question honest:

- which route is the reference lane for this project?
- which routes are backup lanes?
- which routes are blocked by host contracts today?
