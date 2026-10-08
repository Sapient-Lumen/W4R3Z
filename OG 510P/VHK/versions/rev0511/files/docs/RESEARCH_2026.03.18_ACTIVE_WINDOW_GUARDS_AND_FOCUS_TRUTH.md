# Research note — active-window guards and focus truth

## What we learned from adjacent tools

AutoHotkey keeps a sharp distinction between a window that merely exists and a
window that is *active*. `WinWaitActive` exists because real GUI flows often
need to wait for foreground ownership before typing or clicking.

The X11 toolchain shows the same pattern. `xdotool search --sync` waits for a
window to appear, while `windowactivate --sync` and `windowfocus --sync` wait
for foreground/focus state. Those are not the same proof surfaces.

Pulover's Macro Creator also points in the same direction: relative recording
and window class/title capture matter because recorder output is only useful
when it preserves enough workflow context to replay honestly.

## Implication for VHK

VHK's segmented X11 recorder is built from *active-window* samples. That means
its inserted segment guards should default to the same truth the recorder
actually observed:

- `active` scope: wait for the matching window to be focused/foreground
- `present` scope: only wait for a matching window to exist somewhere

Defaulting to `present` would be too weak for many recorded flows. If a browser
and terminal are both already open, a guard that only proves class/title
existence can pass before the user has actually returned to the recorded target.
That invites mis-typed keys and misplaced clicks.

## Product decision

The recorder should therefore:

- default segment guards to `active`
- encode that as `focused: true` on the inserted `WaitForWindow` selector
- keep `present` as an explicit opt-out for authors who intentionally want a
  broader, less strict guard
- preserve the chosen guard scope in the review sidecar so Studio/editor flows
  can surface it later instead of hiding the tradeoff in generated YAML

## Why this stays Linux-native

This is not Windows nostalgia. It is the same operational distinction Linux
users already face today across X11, WM IPC, and compositor tools:

- existence is one proof surface
- foreground ownership is another
- recorder output should say which one it is using

That keeps VHK honest, reviewable, and closer to how strong desktop automation
actually survives outside toy demos.
