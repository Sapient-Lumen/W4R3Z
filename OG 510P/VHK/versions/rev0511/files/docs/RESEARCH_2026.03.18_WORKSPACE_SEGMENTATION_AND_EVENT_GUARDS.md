# Research note: workspace segmentation and event guards

## Why this revision happened

Revision 0323 made geometry boundaries first-class, but another recorder honesty seam remained: workspace was already part of the sampled active-window context, so the recorder could split one flow when the same window identity showed up on another workspace/desktop — yet it still labeled that split as a generic `focus` transition.

That was not a satisfying contract after looking at the surrounding Linux landscape:

- AutoHotkey distinguishes window existence, activation, and waiting surfaces instead of flattening them into one generic notion of “the app changed.”
- i3/sway expose workspace changes as first-class IPC events, separate from window focus/title changes.
- Hyprland’s IPC event stream also exposes workspace/focused-monitor changes as distinct signals.
- generic X11 tooling still treats desktops/workspaces as a real control surface through EWMH-style helpers such as `xdotool get_desktop` / `set_desktop` and `wmctrl` desktop enumeration, even though the event story is weaker and more WM-dependent.

That combination suggests the right VHK rule: workspace transitions are real, but they should be **explicit and opt-in** for recorder output, not an accidental side effect of whatever happened to be in the sampled identity tuple.

## What VHK now does

Revision 0324 follows that rule.

- same-window workspace changes stay flat by default during recorder segmentation
- authors can opt into preserving those boundaries with `--segment-on-workspace-change`
- when event guard mode is active, those boundaries can now become `WaitForWindowEvent(event=workspace, ...)`
- sidecars preserve `segment_on_workspace_change` so downstream tools know whether workspace boundaries were intentionally part of the recording contract

## Remaining honesty boundary

This still does **not** mean VHK has solved a universal Linux workspace event lane.

- i3/sway and Hyprland have stronger, explicit workspace events
- generic X11 still relies more on snapshots/current-desktop truth than on one portable event stream
- recorder-generated workspace guards therefore remain most trustworthy on the stronger WM-specific event lanes and best-effort elsewhere

That is acceptable because it keeps the main truth intact: workspace is now a first-class recorder concept, but only when the author asks for it and only as strongly as the backend can honestly support it.
