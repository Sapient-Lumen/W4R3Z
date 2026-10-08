# Research 2026-03-18: event guards and polling truth

## What we learned from others

- AutoHotkey keeps a meaningful split between proving current window state (`WinWait`, `WinWaitActive`) and waiting for future workflow transitions.
- Window Spy remains part of that discipline: inspect title/class/process first, then wait against what is actually observable.
- Pulover's Macro Creator keeps leaning into recorder-assisted authoring by capturing window class/title and by supporting relative mouse recording, which argues for recorder output that preserves workflow boundaries instead of leaving everything encoded as blind delays.
- On X11, `xdotool behave` is the clearest prior-art reminder that focus changes can be treated as explicit event hooks instead of only as repeated polling/state proofs.

## Design consequence for VHK

Recorder segmentation should not always collapse every cross-window transition into `WaitForWindow`. The first segment of a macro is a current-state proof, but later recorded boundaries are often better represented as future transitions:

- focus transition -> `WaitForWindowEvent(event=focus, ...)`
- same-window title transition -> `WaitForWindowEvent(event=title, ...)`
- geometry-only refresh -> remain state-based for now

That keeps VHK honest about what was actually recorded:

- **state guards** prove "the desired window is already here"
- **event guards** prove "the expected transition happened next"

## Important correction

While implementing the recorder event lane, we found that the generic polling fallback for `WaitForWindowEvent` was behaving more like a snapshot than a future event: it yielded an immediate first focus sample. That contradicted the documented semantics of the step.

The fallback now primes its baseline first and only emits after an actual focus/title change.

## Remaining issue

Generic X11 still does not provide a universal compositor-agnostic geometry event surface. That means relative-coordinate segment refreshes continue to use `WaitForWindow` rather than pretending a portable geometry event exists.
