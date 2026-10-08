# Research notes: learning from adjacent Linux automation tools

These notes capture a few current ecosystem lessons that should keep VHK honest
as it moves from planning prose toward a Linux-native runtime.

## Product-shape lessons

### 1) AutoKey still marks the X11 boundary clearly

AutoKey continues to describe itself as a desktop automation utility for Linux
and X11, with an explicit warning that it will not function 100% on Wayland.
That is a useful product-shape lesson for VHK: desktop scope and session scope
must be named explicitly in public support language instead of being flattened
into a generic "Linux support" claim.

Reference:
- https://pypi.org/project/autokey/

### 2) Espanso keeps text expansion first-class, but Wayland app scoping remains limited

Espanso still treats text expansion, forms, and shareable packages as first-
class surfaces, but its docs still say app-specific configurations are not yet
supported on Wayland. VHK should keep hotstrings/text-entry as a first-class
lane without assuming full app-targeting parity across every desktop.

References:
- https://espanso.org/docs/configuration/app-specific-configurations/
- https://espanso.org/docs/install/linux/

### 3) keyd and kanata prove the value of a low-latency remapper tier

keyd still frames itself as a system-wide daemon built on evdev/uinput with
speed, consistency, and display-server-agnostic app remapping as core goals.
kanata continues to focus on layers, tap-hold behavior, macros, and advanced
keyboard behavior.

VHK should learn from that split instead of competing with it directly:
- keep a clear export/offload story to remapper layers
- treat low-latency trigger ownership as a separate problem from high-level
  macro orchestration
- preserve a good command/event boundary instead of forcing everything into one
  runtime loop

References:
- https://github.com/rvaiya/keyd
- https://github.com/jtroo/kanata

### 4) xremap shows that Wayland power often arrives with desktop-specific seams

xremap still advertises Wayland support and app-specific remapping, but its own
GNOME Wayland guidance still depends on a GNOME Shell extension plus additional
DBus/root environment setup. That reinforces VHK's current strategy: Wayland
support needs explicit route selection and operator-facing deployment guidance,
not one magical backend claim.

Reference:
- https://github.com/xremap/xremap/blob/master/doc/running_with_sudo.md

## Portal lessons

### 5) GlobalShortcuts is session/app scoped, not a generic daemon substrate

The GlobalShortcuts portal is built around application-created sessions and
shortcuts bound to those sessions. That makes it a strong fit for stable,
reviewed action catalogs, but a weaker fit for endlessly dynamic daemon-style
macro inventories.

Reference:
- https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.GlobalShortcuts.html

### 6) InputCapture is still trigger-driven, not immediate-grab automation

The InputCapture portal still distinguishes between "enabled" and "active"
capture, leaves activation to the compositor, and explicitly says there is no
way for an application to activate immediate input capture. That keeps it in the
"carefully permissioned capture lane" bucket, not the "drop-in AHK hook"
bucket.

Reference:
- https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.InputCapture.html

### 7) Portal usability still depends on backend routing and activation environment

The portal docs still make it clear that backend routing is selected through
`portals.conf`, and that backend processes inherit their environment from the
activation environment maintained by `systemd --user` or `dbus-daemon`. VHK
should therefore keep probing backend routing and keep deployment/setup docs
explicit about portal environment seams.

References:
- https://flatpak.github.io/xdg-desktop-portal/docs/portals.conf.html
- https://flatpak.github.io/xdg-desktop-portal/docs/system-integration.html


### 8) X11 power-user tools still teach the same lesson: observe events, do not just sleep

Current X11 tooling still exposes an event-first style that VHK should keep
learning from:

- `xdotool behave` binds actions to window events such as focus, blur,
  mouse-enter, and mouse-leave.
- `wmutils/opt` still ships `wew`, explicitly described as a tool that prints
  window events.
- `xprop -spy` still exists as a forever-running property-change watcher.

The product lesson is bigger than any one backend: Linux automation gets more
reliable when runtime glue can *wait on emitted state changes* instead of piling
more polling loops and fixed sleeps onto every workflow. VHK should therefore
keep event-driven synchronization first-class even when the actual event source
changes across X11, i3/sway IPC, Hyprland socket2, clipboard helpers, or a
project-local IPC bus.

References:
- https://manpages.ubuntu.com/manpages/trusty/man1/xdotool.1.html
- https://github.com/wmutils/opt
- https://manpages.ubuntu.com/manpages/jammy/man1/xprop.1.html


### 9) Idle automation is a probe/event split, not one universal API

Current Linux idle tooling still teaches an important product-shape lesson:
there is no single universally portable idle probe that deserves a giant “Linux
idle API” claim.

- `xprintidle` remains the straightforward X11 probe that returns idle time in
  milliseconds.
- `xidlehook` continues to model idle automation as a command runner with
  thresholds and resume hooks rather than as a general macro runtime.
- `swayidle` keeps the wlroots/Wayland story event-oriented through timeout /
  resume / before-sleep / after-resume hooks tied to compositor protocols.
- GNOME continues to expose a compositor-specific `org.gnome.Mutter.IdleMonitor`
  DBus surface used by surrounding software.

VHK should learn from that split instead of papering over it:
- direct idle probes are a capability surface
- compositor-specific idle daemons are an event bridge surface
- `WaitForBusEvent` should remain part of the idle story, not just WM glue


### 10) Idle tooling is usually a *pair* of states: timeout and resume

Current idle tooling keeps reinforcing that useful automation is often about two
transitions, not one:

- `swayidle` documents `timeout <seconds> <cmd> [resume <cmd>]` and also names
  lock/unlock and before-sleep/after-resume hooks.
- `hypridle` exposes listener pairs with `on-timeout` and `on-resume`.
- `xprintidle` remains a simple X11 probe that reports idle milliseconds, which
  is useful precisely because higher-level tools can turn that counter into both
  “became idle” and “became active again” decisions.

VHK should learn from that shape instead of only implementing one-way idle
thresholds. A Linux-native macro runtime needs both the idle-side wait and the
resume-side wait, while still keeping compositor-specific lifecycle daemons as
optional event bridges rather than pretending one universal API exists.

### 11) Window introspection is useful precisely because Linux does **not** flatten it into one API

Current Linux window tooling still reinforces the same product lesson:
window-aware automation depends on several backend-specific metadata surfaces,
not one universal “get active app” contract.

- `xdotool` still exposes `getactivewindow`, `getwindowname`, and
  `getwindowpid`, which keeps X11 active-window scripting practical.
- `wmutils/opt` still ships `wew` as an explicit window-event printer.
- sway docs and user-facing guidance still lean on `app_id` for native Wayland
  windows rather than pretending `WM_CLASS` remains the universal key.
- Hyprland continues to expose `hyprctl activewindow` as its focused-window
  metadata lane.
- KDE Wayland still needs a compositor-specific bridge such as `kdotool`, which
  shells into KWin scripting rather than using a generic cross-desktop API.

The lesson for VHK is not “hide all this.” The lesson is:
- expose one stable authoring shape (`window`, `wm`, selector-friendly fields)
- keep backend-specific acquisition honest
- make runtime introspection available inside macros, not only in CLI debuggers

That is why `GetActiveWindow` belongs in the runtime: it lets one-shot macros,
watcher-triggered macros, and `window-spy` all speak the same vocabulary while
still respecting Linux’s real backend seams.


### 21) Window enumeration deserves to be first-class, but it is still backend-shaped

AHK did not only make the *active* window inspectable; it also made listing and
filtering windows part of normal automation authoring (`WinGet` / `WinGetList`).
Linux still supports that workflow, but by composing several backend-specific
lanes instead of one cross-desktop API:

- X11 still has explicit window search/list helpers such as `xdotool search`
  and `wmctrl -l -p -G -x`.
- i3/sway still expose the full layout tree over IPC, which is a stronger and
  more structured window-enumeration surface than title scraping.
- Hyprland still exposes `hyprctl clients`, but its docs also warn that
  `hyprctl` info calls are synchronous and should not be spammed; higher-rate
  live flows belong on socket2 instead.
- KDE Wayland can now participate via `kdotool search`, but it still uses KWin
  internal UUID-like window ids and intentionally does not match `xdotool`
  feature-for-feature.

That leads to a useful product rule for VHK: **enumeration should be first-class
in the runtime, but the docs must keep teaching authors which backend seam is
actually answering the question.** `GetWindowList` follows that rule.


### 8) MouseGetPos / window-under-pointer workflows deserve a first-class lane

AutoHotkey still treats `MouseGetPos` as a normal automation primitive: it can
return not just cursor coordinates, but also the window being hovered. Linux can
approximate that too, but the path is backend-shaped rather than universal.
`xdotool getmouselocation --shell` still reports a `WINDOW` value on X11, and
kdotool documents that `getmouselocation` seeds the window stack with the
topmost window under the pointer. By contrast, sway exposes absolute window
rectangles via `GET_TREE`, and Hyprland exposes client geometry via
`hyprctl clients`, which pushes VHK toward geometry-based best-effort matching
on those compositors.

References:
- https://www.autohotkey.com/docs/v2/lib/MouseGetPos.htm
- https://manpages.ubuntu.com/manpages/trusty/man1/xdotool.1.html
- https://github.com/jinliu/kdotool
- https://man.archlinux.org/man/sway-ipc.7.en
- https://wiki.hypr.land/Configuring/Window-Rules/


### 22) PID/process-aware window workflows still matter on Linux too

AHK did not only normalize class/title matching; it also made PID and process
name first-class through `WinGet`/`WinGetPID`/`WinGetProcessName`. Linux still
supports the same *kind* of workflow, but through backend-specific seams:

- X11 still exposes window PID lookup through `xdotool getwindowpid`, while also
  warning that `_NET_WM_PID` depends on cooperation from the target
  application/window.
- sway still documents `pid` as a numeric window criterion.
- Hyprland still exposes `clients`/`activewindow`, which makes PID-bearing
  client metadata available, but its docs also warn that `hyprctl` info calls
  are synchronous and should not be spammed.
- KDE Wayland can participate through `kdotool`, but it still uses KWin
  internal window ids and should be treated as a compositor-specific bridge.

The design lesson for VHK is to make process-aware window context first-class in
the runtime (`pid`, `process_name`, selector `pid`) while keeping exporter and
polling behavior honest per backend.


### 23) Window state is part of the automation surface, not just an implementation detail

A lot of Linux tooling does not just identify windows; it exposes **state**.
That matters because AHK-style authoring often branches on questions like:

- is this window actually visible?
- is it fullscreen?
- is it floating like a popup?
- is it minimized / hidden rather than on-screen?

Current ecosystem signals line up on that:

- sway IPC documents `visible`, `sticky`, `floating`, and `fullscreen_mode` on
  window/container nodes.
- EWMH documents `_NET_WM_STATE_HIDDEN` as the canonical “minimized / not
  represented onscreen” state, and also standardizes `_NET_WM_STATE_FULLSCREEN`
  and `_NET_WM_STATE_STICKY`.
- kdotool documents a `windowstate` lane with support for `fullscreen` and
  `minimized`, but it also explicitly lists `sticky` and `hidden` as missing.
- Hyprland still warns that `hyprctl` info calls are synchronous and should not
  be spammed, which means stateful introspection belongs in one-shot routing and
  diagnostics far more than in tight polling loops.

The design lesson for VHK is to keep one stable state vocabulary across window
lanes (`visible`, `fullscreen`, `floating`, `sticky`, `minimized`, and backend
extras such as `mapped`/`hidden`/`pinned`) while remaining explicit that some
fields are stronger on sway/X11 than they are on KWin/Hyprland.


## Window-state selectors are worth first-class authoring support

AHK treats window state as ordinary authoring material, not debugger trivia:
`WinGetMinMax` exposes minimized/maximized state directly, and the broader Win
function family makes PID/title/class oriented matching normal script authoring.
Linux exposes the same idea, but through backend-shaped surfaces rather than one
universal API:

- sway IPC exposes `visible`, `sticky`, `fullscreen_mode`, and `floating`
- X11 tools like `xdotool search --onlyvisible` and EWMH `_NET_WM_STATE_*`
  expose partial visibility/minimize/fullscreen semantics
- KDE Wayland via `kdotool windowstate` currently supports `fullscreen` and
  `minimized` but still lacks `sticky` and `hidden`
- Hyprland `hyprctl` exposes rich client state, but the compositor warns that
  `hyprctl` calls are synchronous and should not be spammed

That argues for a VHK design where window-state *matching* is first-class at
runtime, while exported WM config remains conservative and backend-specific.

The next lesson is operational: Linux projects also need a way to say *which*
window truth they depend on. There is a real difference between “I match by
class/title” and “I need `sticky` + `fullscreen_mode` + geometry + the window
under the pointer.” VHK now treats that as a project/session **window
contract**, so planning and validation can warn about backend-specific gaps
without pretending every compositor exposes the same surface.


## Event-driven waits are a real authoring primitive

- `xdotool` still documents `behave` as an event-driven interface for window
  hooks such as focus/blur/mouse-enter workflows, which keeps X11 automation
  from degenerating into sleep-heavy polling loops.
- sway/i3 still expose window/workspace events over IPC, so waiting for `new`,
  `focus`, `title`, or `urgent` is part of the normal scripting surface rather
  than a hidden implementation detail.
- Hyprland’s current IPC docs still list `openwindow`, `closewindow`,
  `activewindow*`, `windowtitle*`, `workspace*`, and `custom`, which makes
  event-driven synchronization a first-class compositor seam.

That combination argues for giving VHK a dedicated **WaitForWindowEvent** step
instead of forcing users to approximate every live transition with
`WaitForWindow` + polling or with a permanently running watcher service.

## 2026-03-08: filesystem-triggered automation should keep a small high-level event vocabulary

`inotifywait`, `incrond`, and `systemd.path` all reinforce the same Linux-native lesson: filesystem automation is valuable, but the product surface should stay smaller than raw kernel event masks. VHK therefore keeps `file_watchers` on a compact authoring vocabulary (`new`, `changed`, `deleted`, `any`) and lets helpers map lower-level events into that shape.

Another important lesson is honesty: inotify queues can overflow, and some mounts/filesystems behave poorly with native event streams. VHK should keep a polling fallback and should not oversell file watchers as perfect truth on every host.


## File-event waits: learn from inotifywait / systemd.path / entr / watchexec

Linux already has strong prior art for event-driven file automation.
`inotifywait` is explicitly shaped around waiting for changes from scripts;
`systemd.path` layers service activation on top of inotify while inheriting the
same limitations; `entr` shows the practical value of waiting for the watched
command to finish before reacting again; and `watchexec` keeps debouncing and
filtering as first-class concerns rather than an afterthought.

VHK should learn the same lesson at the macro-authoring layer: expose a small,
honest file-event vocabulary (`new` / `changed` / `deleted` / `any`), support
producer-friendly settling knobs (`min_size`, `stable_ms`), and keep long-lived
watcher policy separate from one-shot in-macro waits. That is what
`WaitForFileEvent` + `file_watchers:` now do.


## File burst coalescing lesson

Adjacent Linux-native file tools do not pretend every low-level edge deserves its own automation run. `entr` explicitly warns that OS event consolidation means its `/_` shortcut is only appropriate for the single-file case, and `systemd.path` documents that `PathChanged=` is not activated on every write. That argues for keeping VHK file automation small, high-level, and quiesce-aware rather than exposing raw helper events as the primary authoring contract.


### 9) D-Bus signals deserve to be a first-class runtime lane, not only a bridge trick

Linux desktop automation keeps running into software that already exposes a good
event boundary over D-Bus instead of through files or shell hooks:

- `dbus-monitor` still exists specifically to monitor messages on the bus.
- `gdbus monitor` is a lighter-weight fallback, but it scopes monitoring around
  one bus owner/object rather than arbitrary match-rule support.
- systemd's D-Bus docs still say clients must call `Subscribe()` before most
  manager signals are sent.
- the MPRIS spec still explicitly tells clients to listen for
  `org.freedesktop.DBus.Properties.PropertiesChanged` when player state changes.

That argues for a VHK shape where DBus can be consumed directly inside a macro
(`WaitForDbusSignal`) while the older `bridge-dbus-signal` CLI remains useful
when authors want to normalize many upstream producers into one local project
bus. The docs should also stay honest that the `gdbus` fallback is narrower than
`dbus-monitor`: for best results it needs a sender/bus-name scope.

## systemd unit state is usually a *state probe* problem, not a raw signal problem

Systemd's docs still make two separate truths clear: `systemctl show` maps
directly onto manager/unit properties, and the D-Bus API still expects clients
to call `Subscribe()` before most manager signals are sent. That combination is
a strong design hint for VHK. Many automation stories only need a *named
unit-state wait* (`ActiveState` / `SubState` / `LoadState`) rather than a raw
D-Bus monitor, so VHK should expose a direct systemd-unit-state lane instead of
forcing every author through custom `systemctl show` parsing or manual signal
subscription setup.
