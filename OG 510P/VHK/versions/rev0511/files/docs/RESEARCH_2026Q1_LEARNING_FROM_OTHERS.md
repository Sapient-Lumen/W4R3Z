Once VHK started layering project-shared and operator-local portal review presets, another lesson from adjacent tools became unavoidable: merged config without source provenance is not enough. Git keeps surfacing where layered config came from through its local/global/worktree model and include mechanisms, and editor tooling like VS Code keeps making override order legible to operators. That maps directly onto VHK's portal audit lane, so the project now treats preset provenance as review data rather than as shell trivia.

Layered review presets are another repeated lesson from adjacent tools. VS Code keeps showing the value of workspace settings overriding user settings, Git keeps showing local/global/worktree layering plus conditional includes, and Kibana keeps showing that saved queries become more useful once teams can reuse them without flattening all preferences into one file. That combination maps neatly onto VHK's portal audit lane: shared review presets belong with the project, operator-local overrides belong under config, and later layers should win by name instead of forcing one forked preset bundle per host.

### -3) Shared review presets should not crowd out operator-local overrides

Saved filter bundles are a repeated lesson in adjacent tooling too. Kibana's saved queries explicitly preserve query text, filters, and time range for reuse, while Allure keeps showing that persistent history data becomes much more valuable when teams can carry the same review lens across consecutive reports. That maps cleanly onto VHK's GlobalShortcuts audit lane: once the project had catalog -> bind -> ledger -> diff -> XDG history -> Markdown/HTML export, the next honest operator surface was a generated preset file that history/export/prune commands can all reuse.

### -2) Shareable audit history wants a portable HTML handoff

Allure keeps validating a practical workflow lesson that applies outside test suites too: historical state is more useful when teams can generate a portable HTML handoff, archive it, and compare runs over time rather than asking reviewers to inspect raw result files. After VHK already had portal catalogs, assignment ledgers, diff reports, and XDG-state history, the next honest step was to add a single-file HTML export on top of that same state lane instead of inventing a second reporting store.

### -2) XDG state only pays off if operators can browse and prune it

The XDG Base Directory spec is clear that `XDG_STATE_HOME` is for persistent state such as history/logs, but Linux apps that treat that as only an implementation detail still leave users doing archaeology in hidden directories. Once VHK moved portal assignment ledgers into XDG state, the next honest step was to add a review surface and a retention lane, not just a better storage root. The follow-up lesson is equally Linux-native: history lanes need operators to filter and expire state intentionally, not only accumulate it.

### -1) GlobalShortcuts audit history belongs in XDG state

The XDG Base Directory spec explicitly reserves `XDG_STATE_HOME` for restart-persistent user-specific state such as logs/history, and the GlobalShortcuts portal docs explicitly expose session-bound shortcut sets plus returned trigger descriptions. Put together, that means VHK should treat portal assignment ledgers as stateful history under XDG state rather than as ad-hoc build files.

## 2026-03-08 remapper-lane follow-up

One more lesson from current Linux remappers is now explicit in VHK itself: `keyd`, `kanata`, `KMonad`, and `xremap` are not just feature inspirations, they are **competing deployment lanes** with different ownership stories. `keyd` keeps validating the tiny system-daemon model, `kanata` and `KMonad` keep validating richer keyboard-first programmable layers, and `xremap` keeps validating app-aware remapping on modern Linux desktops. VHK should therefore keep modeling them as choose-one route members instead of flattening them into a generic “remapper present” checkbox.

# Research notes: learning from adjacent Linux automation tools

These notes capture a few current ecosystem lessons that should keep VHK honest
as it moves from planning prose toward a Linux-native runtime.

## Product-shape lessons

### -1) XDG-state audit trails still need share-safe summaries

The portal/XDG lesson is not complete once state lands in the right directory. Linux-native operator workflows also need a small handoff surface, which is why VHK now renders portal assignment history as Markdown instead of assuming reviewers will read raw YAML under `~/.local/state`.

### 0) GlobalShortcuts should be audited as a session ledger

The current GlobalShortcuts portal docs are explicit that apps bind shortcuts
under a session, `BindShortcuts` returns the subset that was actually bound with
user-facing `trigger_description` values, and `ListShortcuts` exposes the active
shortcut set for the session/application lane. That means VHK should treat the
portal route as a reviewable sequence of artifacts — requested catalog, live
bind/listen flow, and assignment ledger/diff — instead of as one opaque runtime
step.

Reference:
- https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.GlobalShortcuts.html


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
supported on Wayland. Its current app-specific-config docs also state that only
one app-specific configuration can apply at a time, with filename order deciding
which one wins when multiple filters match. VHK should keep hotstrings/text-
entry as a first-class lane without assuming full app-targeting parity across
all desktops, and its package-dir exporter should model that one-active-config
rule explicitly instead of pretending independent scoped files will all stack.

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

### 4.5) daemon-backed uinput clients keep teaching the same lifecycle lesson

Current Wayland input helpers keep reinforcing that the interesting design work
is not only "which injector exists?" but also "what has to stay alive for it
to be fast and predictable?"

- `ydotool` documents why a background daemon is needed: uinput device creation
  takes time and the desktop may not recognize a fresh virtual device
  immediately.
- surrounding Linux docs for `dotool` keep reinforcing the sibling pattern:
  `dotoold` + `dotoolc` is the healthier repeated-playback lane when you care
  about latency and reliability rather than one-shot demos.
- `wtype` remains valuable, but it also reminds us that virtual-keyboard lanes
  are compositor-shaped rather than universal.

The VHK lesson is straightforward: planner output and host-contract docs should
name daemon-backed helper lifecycle explicitly instead of talking about one
generic "Wayland typing" capability.


### 4.7) Good text tools keep a middle ground between pure typing and pure pasting

Keyboard Maestro's docs still draw a clean line between typing and pasting: typing is best for short text and for `Return` / `Tab` actions, while pasting is best for long text or arbitrary characters. Espanso keeps structured forms and app-specific configuration as first-class surfaces, and its Linux install docs still warn that Wayland support is experimental and lacks app-specific configurations there. Taken together, those lessons suggest a VHK middle lane: keep navigation boundaries visible, but let long literal field bodies graduate into an explicit clipboard-paste route when the macro is obviously filling structured forms instead of trying to simulate every printable character forever.

### 4.6) Text-first tools keep reinforcing “final intended text” over raw keystroke noise

Espanso keeps making forms and reusable text packages first-class, Keyboard
Maestro still draws a clear line between inserting text by typing and by
pasting, and Macro-Tool's own README still calls out that recording should get
smoother and “save only needed actions.” Put together, the lesson for VHK is
that recorder cleanup should keep graduating low-level key chatter toward the
final literal text the user meant to insert, not preserve every typo as if it
were sacred.

That does **not** mean pretending all editing is equivalent to text insertion.
Backspace/Delete plus short Left/Right/Home/End corrections, whole-word cleanup
keys such as `Ctrl+Backspace` / `Ctrl+Delete`, boundary selections such as
`Shift+Home` / `Shift+End`, and tiny shift-selection replacements (for example
`hellp` + `Shift+Left` + `o`) are a good low-risk next step because they still
stay within one short local run and can be validated against the final caret
position / selection state; dead-key, IME, and richer editor-semantic flows
still need stricter rules.

References:
- https://espanso.org/docs/matches/forms/
- https://wiki.keyboardmaestro.com/action/Insert_Text
- https://wiki.keyboardmaestro.com/action/Insert_Text_by_Typing
- https://wiki.keyboardmaestro.com/action/Insert_Text_by_Pasting
- https://github.com/YatoVoid/Macro-Tool/blob/main/README.md

### 4.75) Kando and Fly-Pie keep validating discoverable launcher hubs

Current menu / launcher tools keep teaching a complementary lesson: not every
growing macro catalog should be expressed as more invisible hotkeys.

- `Kando` centers pie-menu style launchers with stable item ids and multiple
  trigger paths.
- `Fly-Pie` keeps showing that marking menus can launch apps, URLs, and hotkey
  actions while staying user-discoverable.

VHK should learn from that shape without pretending it already ships a radial
menu runtime:
- keep one stable action catalog across palette entries, rofi rows, and WM
  launcher modes
- treat launcher/menu surfaces as a usability layer over the same runner
- keep low-latency remap ownership separate from discoverable action hubs

### 4.6) choose-one backend families should stay visible without counting as double-failures

One more ecosystem lesson fell out of the current helper mix:

- `wtype` keeps reminding us that a compositor-supported virtual-keyboard lane
  is its own shape, not a universal typing backend.
- `ydotool` explicitly makes the daemon/uinput lifecycle part of the design.
- surrounding `dotool` docs/packages keep showing the sibling `dotoold` +
  `dotoolc` pattern for repeated playback.
- portal APIs such as GlobalShortcuts and RemoteDesktop still expose session /
  consent lanes rather than a timeless always-on daemon substrate.

The VHK lesson is not only "document all of them." It is "model them as
alternative satisfaction paths." A host with one healthy lane should still
show the missing siblings for review, but it should not be scored as fully
blocked when the chosen route is already working.

### 4.7) adjacent tools keep forcing an explicit “which injector?” decision

A recurring lesson from current Linux automation tools is that operators usually
need one *chosen* typing/injection path, not a vague list of everything that
might work:

- projects such as `nerd-dictation` document multiple backends (`xdotool`,
  `dotool`, `dotoolc`, `ydotool`, `wtype`) but still make the backend choice a
  concrete configuration decision
- launcher/app tools such as `rofi-rbw` also expose the same real-world shape:
  “pick the injector that matches your display server”

The VHK lesson is that alternative helper families should not stop at planner
math. Host/readiness/session docs also need to point to one reviewed lane and
its exact bootstrap filter so the operator can act on the preferred path first.

## Portal lessons

### 4.5) Session-bound portals still want shipped action catalogs

The GlobalShortcuts portal is session-managed and interactive, but it is also explicitly about applications registering shortcut/action sets under a session. That means VHK should not leave the portal route as invisible runtime glue; it should emit a reviewable catalog artifact even though the final bind step still lives in the portal UI, and the live listener should be able to consume that exact artifact instead of silently regenerating a parallel action list.

Reference:
- https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.GlobalShortcuts.html

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

### 22) Route selection has to name a deployable lane, not just a healthy family

The current Linux ecosystem keeps repeating the same operational lesson:

- helper-backed input tools are often interchangeable only at a high level
- remappers overlap in purpose but differ in lifecycle, config language, and desktop affordances
- launcher/menu tools solve discoverability, not privileged input ownership

So a Linux-native planner should not stop at “one of these families is healthy.” It should surface the chosen lane and the matching install/review filter. Otherwise route selection stays informative for designers but ambiguous for operators.

## xremap export lesson (2026-03-08)

The most useful thing to learn from xremap was not just that it exists, but **how** it structures Linux-native remapping: app-aware `keymap` entries, explicit `launch:` handoff, and first-match ordering for scoped overrides. xremap’s current README still documents app-specific remapping, command launch from keymap actions, and compositor-specific installation/features for GNOME/KDE/wlroots/Hypr/Niri/COSMIC, which makes it a strong reference lane for VHK’s Wayland-era trigger story. The correct product response is not to clone all of xremap, but to let VHK generate a narrow, reviewable xremap handoff surface for launch-style bindings and app/window scoping.

### 4.8) recorder cleanup should aggressively rediscover text, not just compress keys

A recurring lesson from adjacent automation tools is that users think in terms of
"insert this text" much more often than they think in terms of "press Shift,
press H, release H, release Shift".

- Espanso keeps making structured text/forms a first-class product surface.
- Pulover's Macro Creator still presents recording as a bootstrap into broader
  automation, not as the final form of the macro.
- AutoKey keeps validating the same split between text-centric automation and
  deeper scripting.
- Even small Linux recorder projects like Macro-Tool keep listing "record should
  be smoother" as a follow-up instead of treating raw event streams as the end
  product.

The VHK lesson is practical: recorder cleanup should keep collapsing printable
key chatter back into text spans wherever the intent is obvious, including
shifted uppercase and punctuation, short backspace/delete repairs, and tiny
selection-based replacements, while still preserving real semantic shortcuts
like `ctrl+shift+p` as key actions.



### 4.8) typing-vs-pasting should be an explicit authoring choice, not only a runtime heuristic

Current Keyboard Maestro docs still keep the distinction crisp: typing is closer
  to literal keystrokes and especially useful for Return/Tab-sensitive text
  insertion, while pasting is faster for large text and can carry arbitrary
  characters, but at the cost of clipboard side effects and sometimes different
  styling/widget behavior. Espanso keeps structured text/forms first-class,
  which reinforces the same VHK lesson: large boilerplate text and form-style
  field entry are related but not identical product surfaces.

The VHK lesson is to keep both lanes explicit:
- reconstruct final intended text from recorder noise when the proof is honest
- optionally promote long literal single-line text into explicit clipboard-paste
  mode for throughput
- keep `Tab` / `Enter` rich snippets in the typed lane by default so automation
  authors do not silently lose navigation semantics

References:
- https://wiki.keyboardmaestro.com/Frequently_Asked_Questions
- https://wiki.keyboardmaestro.com/action/Insert_Text
- https://espanso.org/docs/matches/forms/


## Dragonfly keeps the right architectural lesson for VHK voice support

Dragonfly is still a speech-recognition framework with grammar/action objects, and its Linux automation actions still target X11 rather than Wayland. Its command-module story also remains loader-oriented: grammar files are normal Python modules, and non-Natlink loaders such as the Kaldi/Sphinx examples scan underscore-prefixed Python files in a module-loader directory. That combination strongly suggests VHK should **export** a Dragonfly adapter instead of embedding speech recognition into the VHK runner itself.

That led directly to `vhk gen-dragonfly-pack`: VHK now generates a reviewable Dragonfly command module plus a JSON spoken-form ledger, and the generated module calls back into `vhk run ...` instead of duplicating automation semantics in a second runtime. The export stays conservative by default and skips preset prompt overlays unless operators opt in, because spoken invocation followed by surprise interactive forms is not a good default.

## Talon reinforces the same adapter-lane lesson

Talon's current docs still describe Linux support in terms of X11 and explicitly say Wayland support is not planned, while also emphasizing that Talon scripts are just `.talon` files plus Python modules inside `~/.talon/user/`. That makes Talon a good second **adapter lane** for VHK rather than a reason to absorb another speech/runtime stack into the engine.

That led directly to `vhk gen-talon-pack`: VHK now generates a reviewable Talon `.talon` command file, companion Python action module, and JSON spoken-form ledger, and the generated action only shells back into `vhk run ...` instead of duplicating automation semantics in Talon itself.

## App-scoped voice commands are the next honest refinement

Dragonfly still documents `AppContext` around foreground-window executable/title/handle data and supports additional window attributes such as `cls`, while Talon community docs continue to frame `.talon` files around context headers like `app` and `title`. That makes app-scoped voice exports a much better next step than trying to invent a compositor-agnostic voice runtime inside VHK.

That led directly to `voice_when`: VHK macros/presets can now carry a conservative window-selector subset for voice adapters, and the generated Dragonfly/Talon packs only emit those contexts when the mapping is honest. Unsupported selector fields are skipped instead of being silently discarded, which keeps the export reviewable and avoids the dangerous illusion that every voice toolchain can express every VHK window condition.

That lesson also exposed a second design boundary: once voice contexts are real, spoken-phrase uniqueness should be **scoped by context**, not forced globally across the whole project. VHK now follows that rule for Dragonfly/Talon exports and pairs it with `vhk lint-project` warnings when phrases still collide inside the same effective backend scope.


### AutoKey's file-pair model is a good export target precisely because it stays explicit

AutoKey's current docs still describe phrase/script storage as paired body files plus sidecar metadata files, and the docs still tell users to restart AutoKey after sourcing folders because it does not monitor its directories live. Combined with the scripting API docs for `system.exec_command()` and `keyboard.send_keys()`, that makes AutoKey a good **adapter export** target for VHK rather than a reason to embed yet another trigger/runtime inside VHK itself.

That led directly to `vhk gen-autokey-pack`: VHK now emits a reviewable `data/` tree of AutoKey script + sidecar pairs, plus a local README and `pack.json` manifest. The generated scripts shell back into `vhk run ...`, return-mode hotstrings call `vhk run --print-return`, and VHK only exports window scoping when it can be represented honestly as one AutoKey `windowInfoRegex`.
A more careful read of current AutoKey behavior also forced a correction: upstream discussion still describes the window filter as one regex applied to window title **or** class, not a precise selector lane that can target only one of those fields. VHK now reflects that by skipping scoped AutoKey exports by default, only allowing simple `class`-only or `title`-only scope as an explicit approximation behind `--allow-window-filter-approximation`, and validating raw `title_regex` patterns before writing metadata.

A second lesson from current upstream traffic is that AutoKey's trigger/editor surface still has rough edges of its own. Issue templates continue to foreground the Xorg/X11 boundary, and current issue traffic still includes user-visible abbreviation-editor failures. That reinforces the idea that VHK should keep AutoKey as a reviewable, optional X11 adapter lane rather than hiding AutoKey-specific semantics behind a generic “Linux hotkeys just work” claim.

Refs:
- https://autokey.github.io/intro.html
- https://autokey.github.io/api/system.html
- https://pypi.org/project/autokey/
- https://github.com/autokey/autokey/issues/1013
- https://github.com/autokey/autokey/issues/1061


## Lint should surface export loss before pack generation

A useful cross-tool lesson is that Linux automation adapters often look cleaner in marketing language than they do in the actual config/runtime seams:

- Espanso's docs still say app-specific configs are not supported on Wayland, and only one app-specific config is active at a time.
- Dragonfly keeps context matching explicit through `AppContext`, which means unsupported selector fields should be rejected rather than silently dropped.
- Talon's docs still keep Linux on X11, with context expressed through `.talon` headers rather than a richer generic selector language.
- AutoKey still exposes one `windowInfoRegex` concept, and upstream discussion continues to describe that filter as matching window title **or** class rather than independently targeting one field.

The VHK lesson is that adapter honesty cannot live only inside exporters. `vhk lint-project` should warn early when a project is about to ask too much of one adapter lane, so authors can choose between simplifying the export, changing the target surface, or keeping the richer condition inside VHK itself.


## xremap filter-shape follow-through (2026-03-09)

Another concrete lesson from current xremap docs is that its app/window filters are richer than a plain exact-string lane but still narrower than VHK's full selector contract. xremap's current README still documents exact-or-regex `application` filters, regex `window` title filters, and first-match ordered keymaps. VHK now reflects that more honestly: `title_regex` / `app_id_regex` can survive into the generated xremap config, while `vhk lint-project` warns when a binding still depends on runtime-only selector fields such as `workspace`, `pid`, or window-state flags.


## Trigger-lane honesty lesson from current remappers/hotkey daemons

Recent official docs still point to a very split Linux trigger landscape. keyd's
mainline README still describes it as a system-wide evdev/uinput daemon, while
the temporary `keyd-fork` now advertises a separate experimental
`keyd-application-mapper` lane for app-aware remapping rather than folding that
behavior into the core config. Kanata's config guide still emphasizes
keyboard-level processing knobs like `process-unmapped-keys`, KMonad's quick
reference still centers `allow-cmd`, `cmd-button`, and explicit layers, and
sxhkd's man page still describes a simple X hotkey daemon with press/release
chords and SIGUSR1 reload rather than any per-window criteria system.

The design lesson for VHK is that these trigger lanes should stay explicit and
reviewable: some own global capture, some own app-aware gating, and some only
launch commands while VHK keeps the real selector contract. That led directly to
stronger `vhk lint-project` export-honesty coverage for keyd, Kanata, KMonad,
and sxhkd instead of pretending they all preserve `when:` in the same way.


## Literal voice-command syntaxes argue for phrase-quality lint, not just duplicate checks

Talon's current docs still present `.talon` commands as literal spoken-command lines scoped by simple context headers, while Dragonfly's current docs still frame command rules as spoken-form strings or mapping-rule specs. That means the VHK adapter problem is not only “are two phrases duplicated?” but also “what *literal phrase* will the export actually produce after normalization?”

That led directly to a second voice-lint layer in VHK: `vhk lint-project` now warns when explicit `voice_phrases` normalize to nothing, calls out punctuation/case variants that export as a different literal phrase, flags redundant variants that collapse to the same exported spoken form, and nudges authors away from very short one-word global commands unless they add `voice_when` scope. That keeps the generated Dragonfly/Talon packs reviewable without pretending VHK should absorb a full pronunciation or grammar-design system.

## Portal shortcut trigger language is richer than VHK originally assumed

The current freedesktop Shortcuts Specification now lives as a published spec, and
it explicitly says shortcut identifiers come from xkbcommon keysym names without
the `XKB_KEY_` prefix. That means punctuation-oriented triggers such as
`bracketleft` and `semicolon` are valid language elements for GlobalShortcuts,
not just letters, digits, and `Return`. The product lesson for VHK is simple:
when an adjacent Linux-native surface has a real published trigger language, the
exporter should learn that language instead of prematurely declaring common keys
"unportable."

The same official GlobalShortcuts docs also keep reinforcing that the portal is
*global* by design: shortcuts fire regardless of focused window state, then the
client decides what to do with the activation signal. That means VHK should keep
warning authors that `when:` selectors remain runtime-owned in the portal lane
instead of pretending the portal itself has app-aware binding scope.
