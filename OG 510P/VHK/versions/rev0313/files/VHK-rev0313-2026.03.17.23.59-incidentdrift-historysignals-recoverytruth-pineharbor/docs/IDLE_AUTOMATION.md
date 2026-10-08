# Idle automation

VHK now ships two first-class idle primitives:

- `GetIdleMs`
- `WaitForIdle`
- `WaitForUserActivity`

These steps are intentionally capability-honest rather than pretending Linux
exposes one universal idle API everywhere.

## Current first-party support

- X11: `xprintidle`
- GNOME Wayland: `org.gnome.Mutter.IdleMonitor`

## Why this exists

Adjacent Linux tools keep proving that idle-aware automation is a real workflow:
lock timers, focus-mode helpers, break reminders, auto-pauses, and “wait until
I stop touching the machine” handoffs all rely on it.

VHK should support that lane, but without overselling Wayland portability.

## Recommended authoring patterns

### 1) Direct probe when the desktop makes it honest

```yaml
- type: WaitForIdle
  minimum_ms: 1500
  timeout_ms: 20000
  poll_ms: 100
- type: Notify
  summary: "Ready"
  body: "You have been idle long enough; continuing the macro."
```

### 1b) Wait for the human to come back

```yaml
- type: WaitForIdle
  minimum_ms: 300000
  timeout_ms: 3600000
- type: WaitForUserActivity
  maximum_ms: 1500
  armed_after_ms: 300000
  timeout_ms: 3600000
- type: Notify
  summary: "Welcome back"
  body: "Continuing after user activity resumed."
```

### 2) Bridge compositor-native idle events into the bus when no generic probe exists

For wlroots/sway-style sessions, prefer a helper such as `swayidle` that emits
bus events:

- timeout → `vhk emit idle.timeout`
- resume/activity → `vhk emit idle.resume`

Then macros can synchronize with `WaitForBusEvent`:

```yaml
- type: WaitForBusEvent
  event: idle.timeout
  timeout_ms: 600000
```

This keeps compositor-specific lifecycle logic outside the core runner while
still giving macros a clean, event-driven synchronization surface.


## Design note

`WaitForUserActivity` exists because Linux idle tooling consistently models
**timeout + resume** pairs instead of only one-way idle thresholds. VHK should
mirror that shape directly rather than forcing authors to improvise it with
manual loops and sleeps.
