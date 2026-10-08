# Research note: incident drift and journal history

A single `journalctl --user -n ...` excerpt is useful, but it is not the whole
story of a Linux user-service incident.

Systemd exposes explicit current-state and recent-log tools, but it also keeps
separate concepts for boots, invocations, and journal retention. That means one
live status capture can under-describe whether the current incident class is a
one-off, chronic, or already recovered condition.

VHK should therefore keep a short **local installed-lane incident history** in
addition to the current systemd/journal snapshot. This is not meant to replace
raw logs; it is meant to make day-to-day support more truthful before a heavier
host dossier is requested.
