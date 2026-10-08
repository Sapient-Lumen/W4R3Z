# Scheduling macros

VHK aims for a Linux-native scheduling story.

For v1, the recommended path is **systemd user timers** (with cron as a later
fallback).

## Generate a .service + .timer

```bash
vhk gen-systemd ./my_project my_macro --on-active-sec 10m
```

or:

```bash
vhk gen-systemd ./my_project my_macro --on-calendar "Mon..Fri 09:00"
```

By default this writes unit files to:

```text
~/.config/systemd/user/
```

## Enable

After generating unit files:

```bash
systemctl --user daemon-reload
systemctl --user enable --now <unit>.timer
```

## Logs

```bash
journalctl --user -u <unit>.service
```

## Tips

- Prefer `Persistent=true` in the timer so missed runs can catch up.
- Keep macros wait-driven (wait for windows/images/text) rather than sleep-driven.

## Long-running watchers (.service)

Clipboard and window watchers are intended to run as background services.

Generate a user service:

```bash
vhk gen-systemd-watcher ./my_project --window focus_firefox
```

Enable it:

```bash
systemctl --user daemon-reload
systemctl --user enable --now vhk-<project>-window-<watcher>.service
```

### graphical-session.target caveat

Some tiling-WM sessions (notably i3/sway when started outside systemd) do not
reliably reach `graphical-session.target`. If your service refuses to start due
to dependencies, generate the unit without `--graphical` (default: installs
under `default.target`).
