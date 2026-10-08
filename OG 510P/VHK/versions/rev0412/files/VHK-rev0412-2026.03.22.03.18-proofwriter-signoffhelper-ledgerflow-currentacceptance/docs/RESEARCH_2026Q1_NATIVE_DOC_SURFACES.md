# Research 2026Q1: native packaged doc surfaces

This pass focused on a small but important product-shape question: once a VHK
project is installed as a conservative XDG-local app, what does the non-palette
surface look like?

## Borrowed patterns

- Desktop-entry additional actions are a good fit for “open app home”, “open
  support guide”, and “inspect bundle” shortcuts because they are explicitly
  meant for quicklists/jumplists attached to one installed app.
- `gio open` and `xdg-open` are the right conservative openers for packaged doc
  files because they delegate to the user's preferred desktop handler instead
  of forcing VHK to guess which editor/viewer should be used.
- Keep packaged docs inside the app tree under `share/doc/vhk/` so the installed
  lane remains reviewable and relocatable as one app-root story.

## Resulting design

- native app trees now ship `VHK_APP_HOME.md` + `VHK_APP_HOME.json`
- launchers can print/open/list packaged docs directly
- desktop actions can surface home/support docs without dropping users into a
  raw shell command or requiring a terminal window

## Remaining caution

This is still a conservative documentation/status surface, not a promise of a
full interactive GUI shell or tray app. Richer UI should grow only after the
reviewed-bundle/native/service lanes stay stable.
