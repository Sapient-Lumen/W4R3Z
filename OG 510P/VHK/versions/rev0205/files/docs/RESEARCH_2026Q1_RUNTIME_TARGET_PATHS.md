# Research — target-path runtime embedding

## Why target-path bootstraps beat copied virtualenv trees

Python's stdlib `venv` documentation is unusually direct: environments are not
considered movable or copyable and should be recreated in the target location.
That makes exact-target bootstrap scripts the honest next step after VHK's
wheelhouse/runtime handoff.

## Why this fits VHK's package skeleton story

The AppImage/AppDir model already wants one stable entrypoint and predictable
inside-the-AppDir paths, which lines up with reserving `usr/lib/vhk-runtime/`
for a package-local Python runtime.

Flatpak remains more constrained: the official Python docs keep dependency
generation explicit and builder-facing, which reinforces VHK's choice to keep
embed helpers opt-in and reviewable instead of pretending every package lane is
automatically a self-contained automation runtime.
