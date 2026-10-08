# Research note: generic close/new polling and vanish truth

## Why this revision happened

AutoHotkey keeps a clear distinction between waiting for a window to exist and waiting for it to be gone again. `WinWaitClose` is explicitly framed as “wait until the specified window does not exist,” which makes disappearance a first-class automation truth rather than a side effect of sleeps or blind retries.

On Linux, the situation is split by backend. `xdotool` is still the canonical X11 command-line automation tool and can search/activate windows, while `wmctrl` remains a practical EWMH-style enumeration surface for titles, classes, PIDs, and geometries. KDE Wayland’s `kdotool` explicitly positions itself as an xdotool-like bridge for KWin window control, but it also documents missing pieces and the lack of universal `--sync` parity.

That combination suggests a disciplined VHK design:

- do not pretend generic desktops expose a rich universal event stream
- do not throw away truthful open/close semantics merely because the backend lacks native close hooks
- prefer best-effort snapshot diffs for `new` / `close` on generic X11/KWin over falling back to compositor-specific code paths or sleep-heavy folklore

## What VHK now does

Revision 0322 adds a generic polling lane that diffs `GetWindowList`-style snapshots to infer `new` and `close` transitions on X11/KWin-class desktops. Those events stay explicitly best-effort and are limited to what snapshot identity can prove.

The same revision also gives `WaitForWindowVanish` a true generic snapshot fallback. That matters because recorder output had already become much more explicit about window contracts, and the runtime vanish path could no longer honestly stay i3-shaped on generic desktops.

## Remaining honesty boundary

This does **not** mean generic desktops now have a universal compositor event stream. Workspace, urgent, and custom event lanes remain compositor-specific unless VHK is actually talking to i3/sway IPC, Hyprland socket2, or another backend with a real event contract.
