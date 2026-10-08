# Research notes (inputs for roadmap)

This file is a scratchpad of "things worth stealing" from other tools.

## i3 keybindings and `--release`

The i3 User Guide notes that some tools (e.g. `xdotool`) may fail when invoked on
KeyPress because the keyboard is still grabbed; `bindsym --release` runs after
keys are released. This affects how we should generate hotkey bindings and
strongly suggests that any i3-managed hotkey should default to `--release`.

## Screenshot capture + region selection patterns

- i3 docs often demonstrate ImageMagick `import` for screenshots.
- `maim` is common on X11 and supports explicit geometry capture (`-g WxH+X+Y`).
- `slop` (“Select Operation”) is widely used as the glue between "user draws a
  rectangle" and "a CLI tool takes that geometry".

This is the exact workflow we want for an inspector/capture tool: select a
region, capture it, then turn it into a stable needle.

## Clipboard tools and persistence

`xclip` and `xsel` interact with X11 selections (PRIMARY vs CLIPBOARD). Without a
clipboard manager that saves the data, selections are often owned by the process
that set them.

One practical note from real-world usage: `xclip`/`xsel` may fork a background
process to keep owning the selection (so it remains available after the command
returns). This matters for headless automation reliability.

On Wayland, `wl-paste` provides a `--watch` mode that runs a command each time a
new selection appears. This acts as a rough analogue to `clipnotify` on X11 for
"wake up when clipboard changes" workflows, and avoids polling in long-running
watchers when the compositor supports the wlroots data-control protocol.

References:

- wl-paste man page (`--watch`): https://man.archlinux.org/man/wl-paste.1.en
- wl-clipboard man page (data-control requirement for watch mode): https://manpages.ubuntu.com/manpages/jammy/man1/wl-copy.1.html

## Wait primitives vs busy loops

Macro tools in the wild explicitly differentiate:
- `Find` (one attempt)
- `WaitUntilFound` / "Pause until ..." (blocking with timeout/backoff)

Users of some recorders report high CPU usage when they implement IF image-found
as a tight loop rather than a real wait/backoff.

This strongly suggests VHK should keep dedicated wait actions (WaitForImage,
WaitForPixel, WaitForWindow, WaitForA11yEvent) as first-class primitives.



## i3/sway IPC subscriptions for window waits

i3 and sway's IPC protocol supports a `SUBSCRIBE` message that keeps a socket
open and streams JSON events like `window` and `workspace`. This is the pattern
used by `i3-msg -t subscribe -m` / `swaymsg -t subscribe -m` for "wait until a
window appears" workflows, and it avoids busy polling when the compositor can
tell you about state changes directly.

References:

- i3 IPC docs (SUBSCRIBE + event types): https://i3wm.org/docs/ipc.html
- sway IPC docs (`sway-ipc(7)`): https://man.archlinux.org/man/sway-ipc.7.en
- Example "wait for a window event" usage: https://superuser.com/questions/1647488/is-it-possible-to-let-i3-msg-wait-until-some-window-is-shown

Design takeaway for VHK:

- keep a dedicated subscription socket open and **block** on it by default
  (idle watchers should not reconnect every few seconds)
- for waits with a deadline, use a short socket timeout to periodically re-check
  timeout/panic conditions while still waking quickly on real events
## Download completion + "stable file" detection patterns

Real download flows often write to a temporary file and rename/move it only at
the end (e.g. Chrome’s `.crdownload`). A common, lightweight shell pattern is
to watch for `close_write` and `moved_to` (rename) events using `inotifywait`.

References / examples:

- inotifywait usage with `close_write`/`moved_to`: https://serverfault.com/questions/415596/determine-if-file-is-in-the-process-of-being-written-upon
- inotify event types (`IN_Q_OVERFLOW`, `IN_IGNORED`, etc.): https://man7.org/linux/man-pages/man7/inotify.7.html
- `inotifywait --timeout` is specified in seconds (integer semantics): https://man7.org/linux/man-pages/man1/inotifywait.1.html
- Practical "wait until file is stable" scripts (size unchanged): https://unix.stackexchange.com/questions/91207/wait-for-multiple-files-to-be-finished-downloading

Design takeaway for VHK:

- prefer event helpers when available, but keep a polling fallback (portability)
- provide a `stable_ms` / `min_size` knob for workflows where the file appears
  before the content is complete

## Visual matching similarity defaults (SikuliX)

SikuliX documents a default minimum similarity of 0.7 when searching for images,
with configurable per-pattern thresholds.

This provides a reasonable starting point for a future "pattern tuning" UI:
store per-asset thresholds, provide an interactive slider, and surface similarity
scores during waits.

## SikuliX `waitVanish()` and scan rate knobs

SikuliX has two ideas that show up in nearly every visual-macro workflow:

- `waitVanish(pattern, seconds)`: keep scanning until the pattern can no longer
  be found (or timeout). This is the canonical "wait for spinner/progress UI to
  disappear" primitive.
- `Settings.WaitScanRate`: scans per second while waiting for patterns to
  appear/vanish. This is a more user-friendly control than raw poll
  milliseconds for many users.

VHK adopts both ideas:

- `WaitForImageVanish` mirrors the `waitVanish()` semantics.

- SikuliX notes that `waitVanish()` accepts either an image path or **plain text**; VHK now mirrors this with `WaitForTextVanish` (OCR + pattern match).
- wait-style steps accept `scan_rate_hz` as an alternative to `poll_ms`.

References:

- SikuliX Region API (`waitVanish`, `wait`, scan rate note): https://sikulix.github.io/docs/api/region/
- SikuliX scripting settings (`Settings.WaitScanRate`): https://sikulix-2014.readthedocs.io/en/latest/scripting.html

## openQA needles as the asset model to copy

openQA needles are `PNG + JSON`, where the JSON describes:
- match areas
- exclude areas (ignore dynamic stuff like clocks)
- optional click points inside match areas

The key idea worth copying:
**the stable region is what you match** (not necessarily the whole screenshot).

openQA further specifies:
- per-area similarity as an integer percentage (`match: 90`)
- exclude areas to ignore unstable subregions
- click points relative to match areas (used by `assert_and_click`)

VHK v0.4 now:
- respects `exclude` areas (masked template matching)
- honors per-area `match` percentage when present
- implements `ClickNeedle`, which uses click points when available

Implementation note:
OpenCV's `matchTemplate` only supports masking for a couple of matching modes
(notably `TM_SQDIFF(_NORMED)` and `TM_CCORR_NORMED`). When an exclude mask is
present, VHK uses a mask-capable method for scoring.

References:
- OpenCV template matching docs (mask support): https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html
- OpenCV `matchTemplate` reference (mask supported modes): https://docs.opencv.org/4.x/df/dfb/group__imgproc__object.html

## xdotool modifier quirks

`xdotool --clearmodifiers` is a common workaround when keybindings are invoked
with modifiers held, but some users have reported stuck modifier behavior.

Design takeaway:
- allow `clearmodifiers` as a knob on input steps
- don’t hardcode it everywhere

## xmacro file format (interop)

xmacro records X11 events into a simple text stream with commands like:
- `KeyStrPress <keysym>` / `KeyStrRelease <keysym>`
- `ButtonPress` / `ButtonRelease`
- `Delay <ms>`

This is a compelling low-effort import/export format for a "human readable"
record/replay interop story.

## Privileged helper pattern

Ui.Vision RPA uses a browser extension + separate native helpers ("XModules")
for desktop automation and capture. The architectural takeaway for VHK:
separate Studio/UI from OS integration (agent/helper) to simplify packaging,
security boundaries, and debugging.

## Wayland: compositors ship their own cursor movers

Wayland intentionally does not provide a generic "move the cursor" API. Tools
therefore converge on a few strategies:

- uinput daemons (`ydotoold`, `kanata`, `kmonad`) that emulate devices (powerful
  but permission-heavy)
- compositor-native dispatchers (Hyprland's `hyprctl dispatch movecursor x y`)

For VHK this suggests a best-effort approach:

- prefer compositor-native cursor movement when available (no `/dev/uinput`)
- keep uinput tools as the portability fallback (and make their permission
  story explicit via `vhk doctor` + `vhk gen-udev-uinput`)

## i3 criteria + window picker ergonomics

i3 config criteria are regular expressions (PCRE) for fields like class/title,
which is powerful but easy to make too-broad without anchors.

i3 also has a long-standing FAQ answer that ships a tiny helper script
(`i3-get-window-criteria`) built from `xwininfo` + `xprop` that prints a
copy/paste-ready criteria list when you click a window.

Two practical lessons from the surrounding ecosystem are worth baking into the
tooling:

- criteria such as `class`, `instance`, `title`, and `window_role` are PCRE, so
  unanchored values can easily be broader than users expect
- titles are often the least stable selector, which is why i3-resurrect defaults
  to `class,instance` and only adds `title` when the user explicitly wants that
  fragility tradeoff

VHK borrows this directly as `vhk pick-window`, but now emits both a stable
selector suggestion (class + instance + optional role) and an exact selector
that includes title, then previews the current match counts via i3 IPC.

## systemd timers as the Linux scheduling baseline

Most “run this macro every N minutes / at 9am” workflows map cleanly to a
`Type=oneshot` service + a `.timer` unit, using either `OnUnitActiveSec=` or
`OnCalendar=` plus `Persistent=true`.

VHK v0.4 adds `vhk gen-systemd` to generate those units.

## Wayland automation toolchain patterns

The de-facto "small tools" stack for Wayland automation is:

- **grim**: Wayland screenshot tool, supports `-g "<x>,<y> <w>x<h>"` geometry
- **slurp**: interactive region selector (outputs geometry in the format grim accepts)
- **wl-clipboard**: `wl-copy`/`wl-paste` for clipboard
- **wtype**: virtual keyboard input (the Wayland analogue to `xdotool type`)
- **ydotool**: uinput-based keyboard + mouse injection (requires daemon)

VHK v0.6 adds best-effort support for these tools when the desktop backend is
configured as Wayland.

## Espanso hotstrings: include/exclude + app scoping

Espanso has a clean model for scoping match *sets* to specific applications:

- Put scoped matches in a file prefixed with `_` so it is **not** loaded globally.
- Use an app-specific config with `filter_class` / `filter_title` and
  `extra_includes` to load that match set only in that app.

This is a good blueprint for VHK's hotstring story:

- VHK defines hotstrings at the project level (intent).
- VHK exports to an Espanso match set, and optionally generates the app-specific
  config files to scope hotstrings.

Caveat worth repeating: Espanso app-specific configs are not currently supported
on Wayland.


## Visual assert / verify and region-change patterns

Ui.Vision explicitly distinguishes:
- `visualAssert` (stop on mismatch)
- `visualVerify` (log/continue)
- `visualSearch` (count matches)
- `XClick/XMove` (image search + native input)

It also exposes the last screenshot used for debugging and encourages limiting
search areas for reliability. SikuliX separately documents region observation for
 appear/vanish/change events, with a configurable scan rate.

Design takeaways VHK now follows:
- separate assert-vs-verify semantics for visual checks
- keep the last screenshot path in vars for debugging
- provide a dedicated `WaitForRegionChange` primitive instead of forcing users to
  hand-roll screenshot polling loops
- keep visual comparisons explainable: changed-pixel counts, ratios, and masks

## Vision reliability gotchas worth documenting

Macro Recorder's troubleshooting docs are a good reminder that visual automation
reliability is often broken by zoom level, window size, DPI scaling, dark mode,
 dynamic content, and focus assumptions. Even when coordinates are right, image
 search can fail because the rendered pixels changed slightly.

Design takeaway:
- VHK docs and tooling should keep steering users toward stable regions, ignore
  zones, and reproducible window geometry/zoom.


## Retry / continue-on-failure are proven workflow primitives

Robot Framework has two especially relevant primitives:
- `Wait Until Keyword Succeeds` (retry a failing action with an interval)
- `Run Keyword And Continue On Failure` (log failure but keep executing)

Those patterns map well to desktop automation where many steps are "mostly
reliable" but not perfectly deterministic. VHK v0.8 now bakes this into every
step via `retry_count`, `retry_delay_ms`, `retry_backoff`, and
`continue_on_error` instead of forcing users to hand-build retry loops.

## Separate helper/module reporting should exist even before Studio UI

Ui.Vision's XModules page is a useful reminder that users need to know which
helper binaries are installed, their versions, and what capabilities they unlock.

VHK's `doctor` command is now evolving in that direction: a small CLI surrogate
for a future Studio "Modules" page, including machine-readable JSON output.

## Last-screenshot debugging is worth copying exactly

Ui.Vision explicitly exposes the last screenshot used for image search so users
can understand why a match failed. The main lesson is not just "save more PNGs"
but "save the *right* PNG" — the one that the failing matcher/OCR step actually
looked at.

VHK v0.8 therefore reuses the last real capture for screenshot-on-error and adds
visual diff artifacts for failed baseline comparisons.


## “Automation glue” matters: Actiona + event helpers

Actiona's public action list is a useful reminder that practical automation
suites are not just about clicking pixels. They expose file IO, clipboard
read/write, download/open-url, process control, wheel input, and window waits in
the same palette.

That is good evidence that VHK should keep adding small glue primitives instead
of treating them as "shell out yourself" chores. VHK v0.9 therefore adds text
file read/write/append, directory listing, file waits, clipboard-change waits,
and drag/wheel mouse helpers.

## Event-driven waits should use native helpers when available

`inotifywait` exists specifically to block efficiently until filesystem events
happen, and documents timeout/event filtering/CSV-safe output options.
Likewise, `clipnotify` exists to avoid polling X11 selections and simply exits
when the clipboard changes.

Design takeaway:
- use helper-backed waits when the helper is present
- keep polling fallback so projects still run on minimal systems
- surface helper availability in `vhk doctor` so users understand why a wait is
  efficient on one machine and polling on another


## Data-driven macros are worth treating as core, not plugins

Ui.Vision explicitly documents CSV read/write and data-driven workflows as a core
part of the product, including a `csvReadArray` mode that loads the entire CSV
into a 2-D array and row-oriented status variables for looping. That is a strong
signal that practical automation users expect structured data to live *inside* the
macro tool rather than outside it.

Actiona points the same direction from another angle: its action palette is not
just mouse/keyboard, but also text-file editing and data manipulation.

VHK v0.10 therefore adds a minimal built-in data slice instead of pushing users
toward ad-hoc Python or shell snippets for everything:
- CSV read/write
- JSON read/write
- `ForEach` over lists/tuples/dicts
- basic string cleanup transforms (`RegexReplace`, `TrimText`, `SplitText`, `JoinText`)

## Small but useful future issue discovered while researching

Actiona has an open enhancement request about allowing more explicit encoding and
line-ending control in file actions. That is a good reminder that text/data steps
usually start simple and then need portability knobs once users begin exchanging
files across systems.

## Rev 0.11 notes: browser/network/openers glue

- `xdg-open` is the standard XDG helper for opening either URLs or files in the
  user's preferred application, which makes it a better default than baking in a
  browser-specific command.
- `xdg-email` provides a matching "desktop default mail composer" primitive with
  support for `--cc`, `--bcc`, `--subject`, `--body`, and attachments.
- Actiona's broad action catalog is a reminder that practical automation suites
  need lots of small glue actions, not just vision and input.
- Robot Framework RequestsLibrary explicitly supports simple sessionless `GET` /
  `POST` style calls, which is a good conceptual model for VHK's first HTTP step:
  one request, one response object, no mandatory session ceremony.
- Ui.Vision's `!LAST_DOWNLOADED_FILE_NAME` feature is a strong signal that
  download-followup workflows matter in automation UX, hence `WaitForNewFile`.



## Prompt dialogs and background processes deserve first-class steps

Recent passes on Actiona / Power Automate / shell-dialog tools all point to the
same product lesson: users need a small stable set of “glue” actions for
confirmation prompts, input boxes, list pickers, and background processes.
Otherwise they end up tunneling everything through ad-hoc shell commands, which
works but makes flows harder to inspect, render, validate, and debug.

For VHK, the practical Linux-native baseline is to wrap common dialog helpers
(`zenity`, `yad`, `kdialog`, `dialog`) and keep process control separate from
synchronous shell execution.


## Clipboard rules are a real product pattern, not a gimmick

CopyQ's docs are unusually explicit that the product supports commands which can
run automatically when the clipboard changes, and that those commands can also be
bound to global shortcuts. That is very close to the "clipboard macro packs"
idea in the requirements.

clipmenu points in the same direction from the minimalist end: `clipmenud`
passively monitors X11 clipboard selections using XFixes instead of polling.

Design takeaway:
- clipboard-triggered macros belong in the project model, not just as shell snippets
- the project should carry regex/pattern rules and macro bindings for reuse/share
- watcher logs should explain why an event ran or was skipped
- helper-backed monitoring is ideal on X11 (`clipnotify` today; XFixes-like backends later)
- Wayland still needs caveat-heavy handling; `wl-paste --watch` and tools like
  `cliphist` show a good future direction, but support is compositor-dependent


## Structured control flow should feel boringly familiar

Robot Framework's user guide is a useful benchmark here because it treats `WHILE`,
`BREAK`, `CONTINUE`, `RETURN`, and `TRY/EXCEPT/FINALLY` as normal automation
primitives rather than advanced scripting escape hatches. Ui.Vision makes the same
product point from a more recorder-oriented angle: flow control is built in, not a
plugin afterthought.

Design takeaway for VHK v0.14:
- give users real loop / recovery blocks instead of forcing shell workarounds
- keep loop semantics familiar (`break`/`continue` like Python and Robot)
- put a hard safety cap on `While` iterations so bad conditions fail loudly instead of hanging forever
- let `Return` end a called macro early without losing already-computed variables
- treat expression-friendly `SetVar` as the glue that keeps simple control-flow macros readable


## Typing that actually works: clipboard and xvkbd fallbacks

TagUI's docs keep making the same product point: a dedicated "turbo mode" that
runs much faster than normal human speed is worth advertising because users feel
it immediately. The requirements doc translates that well for VHK: do not make
matching/waits less safe, just reduce incidental delays and allow faster text
injection when it is appropriate.

AutoKey's keyboard API is especially useful here because it treats clipboard
pasting as a first-class send mode alongside ordinary key events. It also spells
out an important limitation: clipboard send modes are only suitable for
printable text; embedded special keys/chords must remain in keyboard mode.

xvkbd fills another practical gap on X11: it can send text from a file (or stdin),
and its man page documents `-utf16` for Unicode text with `-file`. That makes it
a nice fallback when ordinary typed-key injection is awkward or unavailable.

Design takeaway for VHK v0.15:
- keep `TypeText` a single user-facing step, but let it choose between multiple backends
- make clipboard-paste an explicit mode, not a shell trick hidden in user macros
- restore the user's clipboard by default when VHK temporarily hijacks it for typing
- keep turbo mode narrow and explainable: scale incidental delays down, and prefer clipboard paste for long printable text


## Cursor hiding and screenshot fallback details are worth productizing

Fresh research around `xbanish`, `unclutter-xfixes`, `scrot`, and old-school `xwd` reinforced a useful product lesson: the boring helper-ladder matters.

- `xbanish` explicitly uses XFixes hide/show calls and is a strong precedent for “hide the pointer while keyboard-driven work is happening.”
- modern `unclutter` / `unclutter-xfixes` variants expose options like `--start-hidden`, `--timeout`, and `--hide-on-touch`, which makes them a practical building block for kiosk-ish or vision-heavy runs.
- `scrot` remains a very scriptable X11 screenshot fallback with a non-interactive rectangle option (`-a X,Y,W,H`), so it belongs in the backend ladder rather than being treated as an afterthought.
- `xwd` is still a useful “ubiquitous ugly fallback” when newer screenshot tools are absent, especially when piped into ImageMagick for PNG output.
- ImageMagick discussions and examples around `PNG32:` are a good reminder that capture pipelines need alpha-awareness; otherwise transparent regions may show up black in saved evidence.

Design takeaway for VHK v0.16:
- make cursor state an explicit part of the run model, not just a user shell trick
- surface screenshot fallback helpers in `vhk doctor` so users can understand why one machine is using `maim` while another is using `xwd+convert`
- keep a last-resort X11 screenshot path even if it is less elegant, because “capture anything at all” is better than total failure when debugging a macro


## Recent xdotool release behavior on Wayland/XWayland

Newer xdotool releases have become more explicit about refusing to run under Wayland/XWayland rather than pretending support exists. That is a useful product signal for VHK:

- backend auto-detection should prefer Wayland whenever `WAYLAND_DISPLAY` is present
- doctor output should surface mixed-session env vars clearly
- X11 helpers like `xdotool`, `xinput`, and `wmctrl` should be treated as X11-specific diagnostics/backends, not generic desktop primitives

This is partly a tooling issue and partly a UX issue: users need a crisp explanation for why an X11 macro helper was not selected inside a Wayland compositor.

## Trigger-backend diagnostics worth exposing early

For future hotkey/hotstring reliability, the most useful lightweight helper checks are not just `keyd` but also the surrounding debug stack: `intercept`, `uinput`, `evtest`, `xinput`, and `wmctrl`. Even before VHK ships kernel-level backends, surfacing those tools in `vhk doctor` helps users understand what kind of environment they are in.


## keyd can run shell commands, but they run as the keyd service user

keyd includes a `command(<shell command>)` action that executes an external shell
command when a binding fires. This is a powerful integration point for VHK
hotkeys in Wayland sessions where compositor binds are limited.

The ecosystem lesson is that this convenience comes with a sharp edge: keyd
usually runs as root, so the command inherits root's environment and may not
have access to user-session services (portals, notifications, etc.). Exporters
should therefore make “wrapper prefixes” a first-class knob instead of
pretending a single invocation will work everywhere.


## AT-SPI health belongs in Doctor, not tribal knowledge

The at-spi2-core docs make it clear that accessibility is not on the normal
session bus: `org.a11y.Bus` lives on the session bus and hands out the address
of a separate accessibility bus via `GetAddress`, and the registry service lives
on that separate bus. That is a strong hint that our diagnostics should test the
real bus path instead of only checking whether a package is installed.

VHK v0.18 now does a lightweight version of this in `vhk doctor` by probing the
AT-SPI bus with `busctl` when available and surfacing `NO_AT_BRIDGE` /
`toolkit-accessibility` context.

## Stuck-key recovery should be a first-class rescue hint

`x11vnc -clear_keys` is an unexpectedly practical X11 recovery trick when a macro
or binding leaves modifiers logically pressed. It is not something users will
remember in the middle of a broken desktop, which makes it a perfect Doctor item.

VHK v0.18 now includes an explicit emergency clear-keys command in `vhk doctor`
for X11 sessions when `x11vnc` is installed, including `DISPLAY` / `XAUTHORITY`
hints.

## ydotool permissions are a setup problem, not a user mystery

The ydotool/uinput ecosystem keeps rediscovering the same failure mode: the tool
may be installed, but `/dev/uinput` permissions or the daemon socket still block
useful input injection. That argues for Doctor output that explains permissions

Newer field reports add two more papercuts:
- Some distros load `uinput` lazily, so the udev rule never fires unless the module is loaded early.
- Recent systemd-udevd versions may ignore udev rules that reference a *non-system* group (so `uinput` should be a system group).
and daemon state instead of simply saying "helper missing."

## XTEST/RECORD should be treated as separate capabilities

`xdotool` is explicit that its input simulation rides on the X11 XTEST extension,
which makes XTEST availability a real prerequisite for "can we inject input?"
reporting rather than a vague guess based on whether `xdotool` is installed.

Xnee's docs are equally useful on the recorder side: synchronized replay leans on
RECORD, but replay without synchronization is still possible when RECORD is absent.
That strongly suggests Doctor messaging should degrade gracefully:
- missing **XTEST** => injection is broken
- missing **RECORD** => advanced synchronized recorder modes stay disabled, but
  basic/raw capture can still be offered

## Keyboard-layout diagnostics are worth surfacing directly

PMC's docs repeatedly call out layout/keymap problems as a cause of invalid
hotkeys. On X11, `setxkbmap -query` is a lightweight way to report the active
layout, variant, and options.

That makes it a good Doctor check because support conversations get much shorter
when the tool can say "you're on `us,de` with `grp:alt_shift_toggle`" instead of
forcing the user to discover that manually.

## i3/sway IPC health matters more than socket env vars

For window-scoped automation, a discovered socket path is only half the story.
Actually querying i3/sway (for example `get_workspaces`) is a better smoke test
than just checking `I3SOCK`/`SWAYSOCK`, because stale or inaccessible sockets are
real failure modes.

## Screenshot self-tests, OCR language packs, and mixed-DPI displays all belong in Doctor

Three practical lessons from the surrounding Linux automation ecosystem:

- **Wayland screenshot tooling is not just an install check.** `grim` documents
  its `-g "<x>,<y> <width>x<height>"` region format in layout coordinates, but
  real-world compositor support still varies because screencopy support is not
  universal. That argues for a Doctor probe that performs a tiny real capture
  rather than trusting PATH alone.
- **OCR readiness is not the same as `tesseract --version`.** Tesseract exposes
  `--list-langs` for installed traineddata, and distributions package language
  packs separately. User reports also show that `--list-langs` can emit scary
  warnings while still listing usable languages, so the probe should parse the
  language list tolerantly instead of treating any stderr as total failure.
- **Visual automation reliability is often a display-geometry problem.** XRandR
  reports current screen size and monitor geometry, and `--listmonitors` exists
  specifically to describe monitor layout. That makes it feasible for Doctor to
  estimate per-monitor DPI/scale and warn when a mixed-DPI desk is likely to
  make baseline screenshots or coordinate-based clicks drift.

VHK v0.20 now reflects those lessons in `vhk doctor`: it runs a temporary
screenshot self-test, reports installed OCR languages, and surfaces estimated
monitor DPI/scale on X11.



## Rule-builder heuristics: `assign` vs `for_window` vs devilspie2

The i3 user guide draws a subtle but important line between `assign` and
`for_window ... move to workspace`: `assign` happens when the window maps, while
`for_window` rules can re-trigger when matching properties change.

That turns into a practical UX rule for VHK:

- pure placement → recommend `assign`
- placement + extra runtime actions (float/mark/focus/geometry) → recommend `for_window`

The devilspie2 manual also reinforces that Lua rules are a viable fallback for
users who already run X11 lifecycle tooling, especially for geometry and
`always_on_top`-style behaviors that do not map cleanly to a single i3 rule.

VHK v0.22 bakes this into `vhk build-rule`, which emits both styles and explains
which one is likely the safer default.

## Hotstrings: lean on existing daemons instead of reinventing interception

There are already mature projects on Linux that implement “hotstrings” and
abbreviation-triggered actions. Two key takeaways:

- AutoKey is explicitly an **X11** automation tool; it doesn't work properly on
  Wayland sessions.
- Espanso treats snippets as YAML “matches” and can execute shell commands and
  inject their stdout as the replacement text.

For VHK, that argues for treating hotstrings as a *project-level intent* and
exporting them to a dedicated hotstring engine. This avoids forcing VHK to
solve keyboard interception in-process (hard on X11, usually impossible on
Wayland without compositor involvement).

VHK v0.22.2 adds `hotstrings:` to `project.yaml` and ships `vhk gen-espanso`
so users can bind triggers like `:sig` to macros that `Return` a text payload.

## "Window Spy" as a first-class workflow

AutoHotkey popularized a tiny but powerful pattern: ship a "Window Spy" helper
that exposes stable identifiers (class, title, process) to make matching less
guessy.

On Linux, this becomes two adjacent workflows:

- X11: click-to-inspect (`xdotool`, `xprop`, etc.)
- Wayland: focus-to-inspect via compositor IPC/tooling (e.g. `hyprctl -j activewindow`)

VHK now mirrors that split:

- `vhk pick-window` (X11)
- `vhk window-spy` (i3/sway/Hyprland focused window)

The goal is not to replace full accessibility/automation inspectors, but to
make it easy to build reliable `when:` selectors and `--require-window` gates.

## Event-driven window hooks: i3 IPC subscribe + Hyprland socket2

Another common automation pattern is “do something when focus changes”.

Two ecosystem lessons matter here:

- i3’s IPC docs explicitly warn that once you subscribe to events, replies to
  requests are no longer guaranteed to arrive before events, and recommend using
  a **separate connection** for events.
- Hyprland exposes a dedicated **socket2** event stream (`.socket2.sock`) with
  newline-delimited `EVENT>>DATA` lines (including `activewindow` and
  `workspace`).

VHK v0.22.6 introduces `window_watchers:` in `project.yaml` plus a
`vhk watch-window` command that follows these patterns: IPC subscriptions on
i3/sway, socket2 on Hyprland, and a polling fallback when the compositor is
unknown.

## 2026-02: event-driven window hooks

- i3 IPC window events include `focus`, `title`, and `urgent` changes.
- Hyprland socket2 exposes `activewindow*`, `windowtitle*`, and `urgent` events.
- Practical lesson from the ecosystem: always assume IPC connections can drop
  (WM restart/reload) and implement reconnect/backoff.

## 2026-02: OCR tuning + actionable bounding boxes

Automation stacks that lean on OCR (AHK community wrappers, openQA, ad-hoc scripts)
repeatedly land on the same pragmatic levers:

- **Preprocessing matters**: rescale small UI text, normalize to dark-on-light,
  and apply simple contrast/thresholding before OCR.
- **PSM/OEM matter**: picking a page segmentation mode that matches the target
  (single line, sparse text, etc.) can dramatically reduce garbage output.
- **Bounding boxes unlock automation**: word/line boxes make OCR results
  clickable ("ClickText"), and multi-match lists ("FindAll") enable list/grid
  workflows.

VHK exposes these levers as step parameters (`preprocess`, `scale`, `psm`, `oem`,
`tess_config`) and adds `OcrFindTextAll*` for multi-match OCR targeting.

## 2026-02: KDE Wayland reality check (KWin scripting + kdotool)

For "Window Spy" and cursor-position workflows, KDE Wayland sits in a tricky
spot:

- Wayland's security model means there's no generic global cursor position API.
- KWin *does* know the cursor position, but exposing it to external tools tends
  to go through KWin scripting + DBus.

Practical ecosystem lesson: tools like `kdotool` provide xdotool-like window
queries by generating temporary KWin scripts on-the-fly, and can also return
cursor position via `getmouselocation --shell`.

VHK now treats `kdotool` as a best-effort helper on KDE Wayland:

- Cursor position (`vhk cursorpos`) when installed
- Active window metadata + geometry (`vhk window-spy`, `CoordMode window`)

It is not intended for high-frequency polling, but it unblocks workflows that
otherwise dead-end on KDE Wayland.

## 2026-02: openQA needles aren’t just image ROIs (they can carry OCR ROIs too)

openQA’s needle JSON supports three area types: `match`, `exclude`, and `ocr`.

- `match`/`exclude` are commonly used to stabilize template matching by focusing
  on stable subregions and masking dynamic pixels.
- `ocr` areas exist as a first-class concept, but the docs note they’re "only
  rarely used".

Even if rarely used in openQA’s day-to-day, the idea maps extremely well to
*desktop automation*:

- Find a stable visual anchor (icon/button chrome)
- OCR a tight text rectangle that moves with that anchor

VHK now exposes this as `OcrNeedleText` and `WaitForNeedleText`.


## Time helpers in macro ecosystems

AutoHotkey exposes simple timing primitives like `A_TickCount` (milliseconds since
boot) and `A_Now`-style wall clock timestamps. The *pattern* shows up across macro
tools: users want a safe way to (a) measure durations and (b) tag external side
effects with a timestamp.

VHK now exposes a tiny, expression-safe set of helpers:

- `monotonic_ms()` / `monotonic_ns()` — duration-friendly counters (AHK-like)
- `now_ms()` / `now_ns()` — wall clock epoch timestamps (useful for comparing with
  file `mtime_ns`)

This keeps timing logic out of shell calls and makes waits like `WaitForNewFile`
more composable.

## 2026-03: download completion heuristics (temp suffixes + stability window)

Across desktop automation forums, “wait for download to finish” usually means a
mix of:

- ignore known temporary download suffixes (Chrome/Chromium: `.crdownload`,
  Firefox: `.part`, Safari: `.download`)
- require the final filename to show up (often via rename/move)
- optionally require the file size/mtime to stay stable for a short period

VHK bakes this into `WaitForDownload` as a convenience wrapper over
`WaitForNewFile`.

## Reliability patterns: retries with jitter + Retry-After

A repeated lesson from large-scale client libraries is that *plain exponential backoff*
can still cause lockstep retries ("thundering herd") when many clients fail at once.

A commonly recommended mitigation is adding **jitter**, with "full jitter" being a
simple and effective option (random delay between 0 and the computed backoff):

- AWS Architecture Blog: "Exponential Backoff And Jitter" — https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
- AWS Builders' Library: "Timeouts, retries and backoff with jitter" — https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/
- AWS SDK for Java: FullJitterBackoffStrategy — https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/core/retry/backoff/FullJitterBackoffStrategy.html

For HTTP polling/wait primitives, it is also common to respect the server-provided
`Retry-After` header when present (curl does this for retries) so clients do not
fight the service's own throttling / recovery logic:

- curl manpage `--retry` notes `Retry-After` compliance — https://curl.se/docs/manpage.html
- everything curl: "Retry" — https://everything.curl.dev/usingcurl/downloads/retry.html

## Atomic file writes for downloads

A pragmatic way to avoid half-written outputs is to write to a temporary file in the
same directory and then atomically swap it into place. The `atomicwrites` library
documents this pattern, and Python's `os.replace` provides atomic replacement when
source and destination are on the same filesystem.

- atomicwrites docs — https://python-atomicwrites.readthedocs.io/
- Python docs: `os.replace` — https://docs.python.org/3/library/os.html#os.replace


## 2026-03: cursor/hover states are a common cause of flaky image matching

Many “image not found” debugging guides for macro tools boil down to the same root cause:
the pixels you captured are not the pixels you’re matching at runtime.

Two repeat offenders:

- **Hover/tooltips** (the cursor sitting over the target changes its appearance)
- **Focus/pressed states** (captured focused, matched unfocused, or vice versa)

Macro Scheduler’s “Image Recognition Common Mistakes” calls this out explicitly: capture
the object in the same state as runtime and avoid including too much background.  
Ref: https://www.mjtnet.com/blog/2009/02/13/image-recognition-common-mistakes/

Macro Recorder’s Find UI reinforces the workflow with a **region overlay** and **Test**
button so users can validate that the current needle/settings match *right now*.  
Ref: https://www.macrorecorder.com/doc/find/ and https://www.macrorecorder.com/doc/capture/

VHK’s low-friction mitigations:
- `cursor_avoid: corner` for screen-capture image steps (move cursor away before capture)
- `debug_on_timeout: true` to emit an annotated screenshot showing the best match

## Delayed capture is a common UX affordance

Screenshot tools often provide a “delay” option so users can open menus or set up hover
states before the capture starts (e.g. Snipping Tool’s delay setting).  
Ref: https://support.microsoft.com/en-us/windows/use-snipping-tool-to-capture-screenshots-00246869-1843-655f-f220-97299b865f6b

VHK now supports `--delay-ms` on `vhk capture-needle` and `vhk capture-baseline` to make
capturing those state-dependent needles more reliable.


## 2026-03: clipboard/window automation needs de-dupe + cooldown controls

Real-world clipboard tooling tends to have strong opinions about duplicates:

- CopyQ historically **de-duplicates** items by default, which has prompted feature
  requests from users who *want duplicates preserved* for batch workflows.
  Refs: https://github.com/hluk/CopyQ/issues/576 and https://github.com/hluk/CopyQ/issues/1136

On the macro side, event hooks often have to decide what counts as a "change":

- AutoHotkey's `OnClipboardChange` only fires when content changes, which is useful
  for avoiding noise but can be surprising when you want to treat repeated copies
  as meaningful actions.
  Ref: https://www.autohotkey.com/docs/v2/lib/OnClipboardChange.htm

And, regardless of ecosystem, automation systems frequently need a simple throttle
to avoid loops ("cooldown" / "debounce" patterns show up constantly).

VHK's watcher knobs are modeled after these patterns:
- `dedupe_scope` (compare against last handled vs last seen)
- `dedupe_window_ms` (skip repeats seen recently)
- `cooldown_ms` (throttle macro runs while still logging events)


## AutoHotkey `WinWaitClose()`

- AutoHotkey exposes `WinWaitClose` (wait until a window does not exist). VHK mirrors this with `WaitForWindowVanish`.
- Docs: https://www.autohotkey.com/docs/v1/lib/WinWaitClose.htm

## 2026-03: "stable screenshot detection" is a practical way to wait out animations

Modern visual regression tooling often needs to avoid capturing a screenshot mid-animation.
A pragmatic approach is to keep taking screenshots until the image stops changing.

Vitest documents this as "Stable Screenshot Detection": it takes an initial screenshot,
then keeps capturing and comparing, rolling the baseline forward on mismatch until the
page becomes stable or a timeout is reached.
Ref: https://main.vitest.dev/guide/browser/visual-regression-testing

On the macro side, AutoHotkey users frequently implement the same idea by comparing
consecutive screen captures (e.g. ScrCmp() helpers that memcmp pixel buffers) to detect
changes in a region.
Ref: https://www.autohotkey.com/boards/viewtopic.php?style=7&t=82812

VHK mirrors these patterns with `WaitForRegionStable`, which repeatedly captures and
compares a region until it stays within configured change limits for a small stability
window.

---

## 2026-03 — Additional inspiration & ecosystem notes

### AutoKey (X11) — “phrases + scripts + GUI” as the wedge

AutoKey’s docs emphasize that phrases/scripts/abbreviations are meant to be reusable across apps, and the GUI is a major part of why people stick with it.

Takeaways for VHK Studio:
- A **fast editor + organizer** for triggers is half the product.
- Import/export matters (users want to backup/restore and generate content programmatically).

Refs:
- https://autokey.github.io/intro.html
- https://github.com/autokey/autokey

### Actiona — “drag & drop actions” plus optional scripting

Actiona is an open-source automation tool that mixes a visual action list editor with optional JavaScript for advanced logic.

Takeaways:
- A curated **action palette** helps novices.
- A real scripting escape hatch avoids painting ourselves into a corner.

Refs:
- https://github.com/Jmgr/actiona

### SikuliX — IDE-first visual automation

SikuliX positions the IDE as the main workflow: capture images, organize them, and write simple scripts (Python/Ruby/JS) only when needed.

Takeaways:
- A “capture + annotate + test match” loop is crucial for visual automation.
- Users want to **organize assets** in the tool, not a file browser.

Refs:
- https://sikulix.github.io/docs/

### sxhkd — chord chains and instant reload

The `sxhkd` model (hotkey daemon + SIGUSR1 reload) maps well to “edit macros + reload bindings instantly”.
Chord chains (using `;` or `:`) provide a leader-key layer without writing our own global grabber.

Refs:
- https://man.archlinux.org/man/sxhkd.1

### Hyprland IPC — closewindow payload limitation

Hyprland’s IPC events include `openwindow` with class/title, but `closewindow` only provides an address; by the time it arrives the client may not be queryable.

Takeaways:
- For close-triggered automation, we should treat “best effort” window metadata as optional.
- Store any needed metadata at `openwindow`/focus time if a later close event is the trigger.

Refs:
- https://wiki.hypr.land/IPC/

### systemd v258 udev policy — non-system GROUP/OWNER rules ignored

Multiple projects (kanata, various uinput-based tools) reported that systemd v258’s
udev behavior can ignore `GROUP=` assignments if the group is not a *system* group.
This breaks common “avoid sudo for /dev/uinput” recipes.

Takeaways:
- VHK docs/generators should recommend using a **system group** (or uaccess/ACL)
  for uinput, and the doctor output should explicitly call this out when uinput
  permissions are failing.

Refs:
- https://github.com/jtroo/kanata/issues/1798
- https://lists.freedesktop.org/archives/systemd-devel/2025-September/051670.html

### Portals / RemoteDesktop / EIS — reality check

Wayland “safe” input injection often depends on the XDG Desktop Portal RemoteDesktop
interface and compositor backend support. Coverage and UX can vary widely.

Takeaways:
- Keep the backend boundary explicit: portal/EIS is ideal when available, but
  uinput remains necessary for many setups.

Refs:
- https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.RemoteDesktop.html

## 2026-03-05: IPC escape hatches and reliability footguns

- **Hyprland dispatchers can emit custom socket2 events** via the `event` dispatcher, in the form `custom>>yourdata`. This is a clean way to connect WM config to automation without extra scripts.
- **hyprctl calls are synchronous inside the compositor**, so “spammy polling” can cause slowdowns. Prefer event-driven wakeups (socket2) and cache metadata when payloads are lossy.
- **sxhkd supports instant config reload via SIGUSR1**, which is a useful design reference for “fast authoring loop” tooling.
- **systemd v258 udev ignores OWNER=/GROUP= for non-system users/groups**, which breaks common `/dev/uinput` permission recipes. Prefer a system group or uaccess/ACL approaches, and document diagnostics.

Refs:
- https://wiki.hypr.land/Configuring/Dispatchers/
- https://wiki.hypr.land/IPC/
- https://wiki.hypr.land/Configuring/Using-hyprctl/
- https://wiki.archlinux.org/title/Sxhkd
- https://manpages.ubuntu.com/manpages/bionic/man1/sxhkd.1.html
- https://raw.githubusercontent.com/systemd/systemd/v258/NEWS
- https://github.com/systemd/systemd/issues/39056
- https://github.com/jtroo/kanata/issues/1798
- **systemd .socket units can listen on AF_UNIX SOCK_DGRAM paths** (datagram sockets), which is an interesting future direction for VHK bus socket activation. Today we run `vhk busd` as a normal service, but socket activation could reduce boot ordering issues.

Refs:
- https://www.freedesktop.org/software/systemd/man/systemd.socket.html
- https://manpages.debian.org/testing/systemd/systemd.socket.5.en.html


## 2026-03: Reload loops + WM-native event emitters

- sxhkd reloads its config on SIGUSR1. This is a widely used pattern for fast
  iteration on keybind setups.
- Hyprland provides an `event` dispatcher that emits `custom>>...` events on
  socket2. Bridging that stream into VHK's bus gives a compositor-native trigger
  surface without glue scripts.
- Hyprland documentation warns that `hyprctl` info calls are synchronous in the
  compositor; event-driven socket2 handling is preferred for live reactions.

## 2026-03-05: systemd socket activation + KDE KWin signals

- systemd socket activation passes pre-bound sockets to services using the
  sd-daemon protocol (`LISTEN_FDS`, `LISTEN_PID`), starting at fd 3. This lets
  small daemons start on-demand and avoid login-time race conditions.
- sd-daemon also supports **named** activated descriptors via `LISTEN_FDNAMES` (colon-separated). Services can use this to pick the right socket when multiple fds are passed; socket units can set names using `FileDescriptorName=`.
- KDE KWin scripting is JS-based and has a large API surface, but executing
  arbitrary external commands directly from scripts is not always the intended
  model; a common pattern is to emit a DBus signal and have an external helper
  react.

Refs:
- https://www.freedesktop.org/software/systemd/man/sd_listen_fds.html
- https://www.freedesktop.org/software/systemd/man/systemd.socket.html
- https://man7.org/linux/man-pages/man3/sd_listen_fds.3.html
- https://manpages.debian.org/testing/systemd/systemd.socket.5.en.html
- https://man7.org/linux/man-pages/man1/systemd-socket-activate.1.html
- https://develop.kde.org/docs/plasma/kwin/api/
- https://discuss.kde.org/t/execute-a-command-from-a-kwin-script/38954

## 2026-03-05: Global shortcuts portal

- The **GlobalShortcuts** portal provides a permissioned, DE-integrated way to
  request global keyboard shortcuts on Wayland.
- Triggers use the freedesktop **Shortcuts specification** (e.g.
  `CTRL+ALT+Return`, with modifiers `CTRL/ALT/SHIFT/NUM/LOGO`).
- Backend support is still uneven; some GNOME users report portal UX/prompts,
  and some portal backends have open issues around missing methods.

Refs:
- https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.GlobalShortcuts.html
- https://specifications.freedesktop.org/shortcuts/latest/
- https://discourse.gnome.org/t/how-do-you-enable-disable-global-shortcuts-in-gnome-48/29119

## 2026-03-05: Portals reality check + event-driven tools

### GlobalShortcuts portal (Wayland hotkeys)

- The GlobalShortcuts portal exists and is the most permissioned “global hotkey” story on Wayland.
- Backend support is uneven:
  - Plasma has an implementation.
  - wlroots setups commonly use xdg-desktop-portal-wlr, which currently implements Screenshot/ScreenCast only.
  - GNOME 48-era reports indicate some paths where `BindShortcuts` is not implemented.

Design implication: treat portal hotkeys as an optional tier; keep compositor-native and bus-based triggers as first-class.

### RemoteDesktop portal (permissioned input emulation)

- The RemoteDesktop portal is the official “permission prompt then remote-control session” API.
- If we later add libei/EIS integration, it should sit behind a capability matrix and strong diagnostics.

### HyprWhenThen and similar tools

HyprWhenThen is an example of a small service that listens to Hyprland events and runs actions based on rules.
It reinforces the “cheap event stream + rules” model we’re adopting via WM events + bus watchers.

## 2026-03-05: OSC as a controller/automation glue surface

OSC (Open Sound Control) is a simple UDP control protocol used widely by controller and audio ecosystems.

- Bitfocus Companion's generic OSC integration lets users specify an OSC path and value, which maps nicely to
  “button press triggers an action” workflows.
- Node-RED has OSC nodes (e.g. node-red-contrib-osc) that can bridge OSC to HTTP/MQTT/etc.

Design implication: supporting OSC as a first-class **external trigger surface** is a practical way to integrate
VHK with hardware buttons, dashboards, mixers, and automation graphs — without requiring those tools to speak
UNIX sockets.

Refs:
- https://bitfocus.io/connections/generic-osc
- https://flows.nodered.org/node/node-red-contrib-osc
- https://hangar.org/wp-content/uploads/2012/01/The-Open-Sound-Control-1.0-Specification-opensoundcontrol.org_.pdf
