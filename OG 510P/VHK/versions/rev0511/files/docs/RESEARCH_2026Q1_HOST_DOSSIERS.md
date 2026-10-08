# Research — installed host dossiers and Linux support packets

This note explains why VHK now has a dedicated host dossier pack instead of
stopping at install scripts and scattered status commands.

## One lane should produce one packet

Linux packaging and service composition are rarely debugged from a single
command. Real issues usually span:

- desktop/session identity
- launcher discoverability
- user-service state
- recent journal output
- whatever the installed app thinks its own state is

That makes copy/pasted terminal output a poor long-term support surface.
Collecting these facts under one XDG state root is a better match for how Linux
operators actually debug installed applications.

## logind is the session truth, not guesswork

`loginctl show-session` exposes concrete session properties for the active
session. That makes it a better input for support packets than trying to infer
session type from one environment variable or from screenshots alone.

## systemd needs both static and live views

`systemctl --user show` is good for the running manager's current view of unit
search paths and unit state, while `journalctl --user` captures recent behavior.
Those answer different questions, so the dossier pack collects both.

## Per-user journals are not universal

Per-user journal access is not guaranteed on every host. VHK treats that as an
explicit gap in the dossier instead of pretending the absence of logs means the
service lane is healthy.

## Why archive under XDG state first

The dossier is host-specific support state, not portable project data. Keeping
it under `XDG_STATE_HOME` first and only zipping it after review matches that
reality and makes privacy review easier.
