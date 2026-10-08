# Research — startup handoff ownership

Current Linux desktop/service guidance keeps pointing to the same lesson:
startup mechanisms are related, but not interchangeable.

## What current tooling/specs are teaching

- The XDG autostart spec says entries in autostart directories are launched by
  the desktop/session, and `OnlyShowIn`, `NotShowIn`, and `TryExec` all affect
  whether that startup actually happens.
- `graphical-session.target` is a distinct systemd user-session concept for
  graphical services rather than a synonym for “the user logged in somehow.”
- UWSM explicitly binds itself to `graphical-session-pre.target`,
  `graphical-session.target`, and `xdg-desktop-autostart.target`, and it treats
  XDG autostart entries as systemd-managed startup objects.

## Product lesson for VHK

If a VHK service pack emits both a graphical-session-bound unit and an XDG
autostart bridge, it should also say which one is the **default owner** and
which one is merely the **fallback owner**.

Otherwise the handoff risks recreating exactly the kind of Linux startup folklore
that VHK is trying to replace with reviewed artifacts.
