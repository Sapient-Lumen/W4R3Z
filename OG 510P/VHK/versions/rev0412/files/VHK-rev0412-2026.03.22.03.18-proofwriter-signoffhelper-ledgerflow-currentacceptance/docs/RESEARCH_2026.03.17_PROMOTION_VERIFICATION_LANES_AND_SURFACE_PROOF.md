# Research — promotion verification lanes and surface proof

Date: 2026-03-17

## Question

If VHK wants to behave like a serious Linux-native automation system instead of a vague macro exporter, what should count as proof that a promoted surface is actually alive?

## What the outside tools keep teaching

### Espanso

Espanso keeps text automation tied to explicit service and inspection surfaces:

- `status`
- `log`
- `path`
- `match`
- `restart`
- `service status/start/stop/restart/register/check`

That is a strong signal that text-package proof should not stop at “the files exported.” The real proof loop is service health plus one representative expansion path.

### keyd

keyd keeps remapper truth close to live input and journald:

- start via systemd
- reload the config set
- inspect logs via `journalctl`
- inspect emitted key names via `keyd monitor`
- keep an emergency termination path when a bad config makes the machine hard to use

That implies remapper proof should be input-event smoke plus log truth, not only generator success.

### xremap

xremap continues to emphasize `evdev`/`uinput`, app-specific remapping, and `--watch` for newly connected devices. That reinforces the idea that some Linux-native surfaces are only real when a live device/event path has been observed.

### GlobalShortcuts portal

GlobalShortcuts remains session-based and emits `Activated` / `Deactivated` signals. That means portal-backed trigger proof is about session and signal behavior, not just static registration.

### InputCapture portal

InputCapture still distinguishes `enabled` from `active`, and activation remains compositor-controlled and asynchronous. That is a very strong reason to separate “planner says this route exists” from “the target desktop has actually demonstrated the proof state we need.”

### Background portal

The Background portal explicitly separates background permission/autostart requests from status reporting via `SetStatus`. That continues the same Linux lesson: lifecycle and proof are first-class surfaces, not implementation details.

## Product lesson for VHK

Planner output needed one more explicit truth surface:

- not only how a promotion ships
- not only how it starts
- not only how operators control it
- not only how they recover it
- but how they prove it is alive on the target desktop right now

That is the role of `promotion_verification_plan`.

## Practical shape

Per promoted surface, VHK should name:

- verification posture
- primary verification lane
- related capability gates
- smoke loop
- live probe
- acceptance boundary
- proof surfaces

This keeps release language anchored to observed Linux behavior instead of to generated files and optimistic assumptions.
