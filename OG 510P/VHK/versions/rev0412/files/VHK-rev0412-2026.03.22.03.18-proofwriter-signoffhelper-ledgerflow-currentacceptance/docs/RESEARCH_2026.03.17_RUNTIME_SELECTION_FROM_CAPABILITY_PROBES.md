# Research — runtime selection should consume the same truth surfaces as doctor

## What changed in understanding

The repo had already learned an important Linux-native lesson in the **doctor**
and **readiness** lanes:

- `dotoolc` is not the same thing as `dotool`
- `ydotool` is not the same thing as “a binary named `ydotool` is on PATH”
- `wtype` is not the same thing as “Wayland session detected”

What was still missing was the last mile: the live runtime chooser could still
pick helpers from PATH alone even after doctor had already proven that the lane
was not actually ready.

That mismatch is exactly the sort of thing that makes Linux automation feel
fragile: planning says one thing, runtime does another.

## What current prior art keeps teaching

A few repeated ecosystem patterns matter here:

- `wtype` is a **virtual-keyboard protocol** tool, and users still report the
  canonical failure mode on GNOME/Mutter: “Compositor does not support the
  virtual keyboard protocol.”
- `ydotool` upstream continues to describe `ydotoold` as mandatory because the
  virtual device must stay alive long enough for the graphical stack to accept
  it.
- `dotool` remains usable as a one-shot stdin helper, but multiple community
  references still point to `dotoold` + `dotoolc` as the faster repeated-playback
  lane because the virtual devices stay alive.

## Design implication for VHK

That means VHK should use **the same capability facts at runtime that it uses
in doctor/readiness/planning**:

- if `dotoold` is explicitly known inactive/failed, do not auto-pick `dotoolc`
- if `ydotool` is explicitly known to lack a reachable socket, do not auto-pick
  `ydotool`
- if Wayland protocol inspection explicitly says virtual keyboard support is
  absent, do not auto-pick `wtype`
- when probe state is genuinely unknown, remain pragmatic rather than treating
  uncertainty as a hard failure

That last point matters. Linux hosts are messy:

- some non-systemd setups can still run helper daemons manually
- some sessions do not have `wayland-info`
- some operators intentionally override auto-selection

So the right behavior is **truth when available, pragmatism when not**.

## Resulting product direction

This makes VHK more Linux-native in a meaningful way:

- route selection is no longer just a planner artifact
- runtime selection is no longer just PATH scanning
- helper/daemon/protocol truth becomes a shared contract across authoring,
  validation, and execution

That is closer to what AHK felt like on Windows: not merely featureful, but
predictably honest about what the system can actually do.
