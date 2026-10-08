# Research — workload-shaped input lanes and operator dossiers

## Why this pass

VHK already knew about lots of Linux input helpers, but helper lists are not the
same thing as a product strategy. Current upstream docs keep reinforcing that
Linux automation splits into **different lanes with different lifecycles**.

## What current upstream material keeps teaching

### 1) `wtype` is a narrow virtual-keyboard fast path

The upstream `wtype` README still frames it around the Wayland virtual-keyboard
protocol and notes that pressed modifiers are released when the process exits.
That is a useful fast path, but it is plainly not a universal Linux text lane.

### 2) `ydotool`/`dotool` keep repeating the daemon-lifecycle lesson

`ydotool` still documents daemon-backed operation, and the broader Linux helper
ecosystem still treats long-lived device/session state as the answer for
repeated playback. That means repeated pointer/key automation is really a
service/socket/uinput lane, not just a helper-binary checkbox.

### 3) portals and libei keep permission/control as first-class boundaries

The XDG GlobalShortcuts, RemoteDesktop, and InputCapture docs keep describing
session creation, registration, triggers, and asynchronous activation. `libei`
also still describes a client/server/portal split rather than one immediate
replacement for every old injection path.

## Product implication for VHK

Those sources argue for one practical design move: VHK should group input truth
by **workload lane** during planning/review.

The important questions are:

- does the project want clipboard/text-surface throughput?
- does it want narrow literal text bursts on a compositor-proven fast path?
- does it want repeated pointer/key playback that deserves a daemon-backed lane?
- does it want permissioned portal/libei-style control?
- or is it simply an X11-native replay case?

That is more useful to an operator than a flat list of helper names because it
connects Linux reality to deployment choices, support posture, and docs.

## Resulting repo direction

This research supports adding an explicit `input_lane_dossier` to planning and
capability-audit output so VHK can talk about Linux-native input as a set of
reviewable workload lanes instead of only as backend trivia.
