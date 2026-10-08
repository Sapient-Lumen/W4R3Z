# Research — recovery lanes and first-response ownership

Recent Linux automation tools keep reinforcing the same lesson: shipping posture and startup posture are not enough. Operators also need an explicit first-response and rollback lane when a surface drifts.

- Espanso documents a real Linux service lifecycle with `service register/start/stop/status`, `restart`, and `log`, so a text-package surface naturally becomes a service-restart recovery lane.
- keyd documents `systemctl enable ... --now`, `keyd reload`, `journalctl -eu keyd`, and a special `backspace+escape+enter` sequence that terminates keyd if a bad config makes the machine hard to use. That is the shape of a rollback-first recovery lane.
- xremap keeps presenting itself as a fast remapper built around `evdev`/`uinput`, with app-specific remapping and `--watch` for newly connected devices. That reinforces that repeated low-latency input layers need explicit restart/reload/device-drift recovery, not only a shipping recommendation.
- XDG desktop portals remain session-shaped. GlobalShortcuts, RemoteDesktop, and InputCapture all describe session creation/binding and lifecycle; InputCapture explicitly says sessions can be closed and that actual transport is delegated to libei. That is a session-recreate recovery lane, not a generic restart story.
- ydotool still presents `ydotoold` as mandatory for the modern tool, so daemon/socket truth remains central to recovery.

Product implication: `plan-project` should expose a `promotion_recovery_plan`, with per-surface recovery posture, first response, rollback surface, re-entry check, related host requirements, and review commands.
