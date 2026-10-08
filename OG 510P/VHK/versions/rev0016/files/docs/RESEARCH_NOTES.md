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

## Wait primitives vs busy loops

Macro tools in the wild explicitly differentiate:
- `Find` (one attempt)
- `WaitUntilFound` / "Pause until ..." (blocking with timeout/backoff)

Users of some recorders report high CPU usage when they implement IF image-found
as a tight loop rather than a real wait/backoff.

This strongly suggests VHK should keep dedicated wait actions (WaitForImage,
WaitForPixel, WaitForWindow, WaitForA11yEvent) as first-class primitives.

## Visual matching similarity defaults (SikuliX)

SikuliX documents a default minimum similarity of 0.7 when searching for images,
with configurable per-pattern thresholds.

This provides a reasonable starting point for a future "pattern tuning" UI:
store per-asset thresholds, provide an interactive slider, and surface similarity
scores during waits.

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

## i3 criteria + window picker ergonomics

i3 config criteria are regular expressions (PCRE) for fields like class/title,
which is powerful but easy to make too-broad without anchors.

i3 also has a long-standing FAQ answer that ships a tiny helper script
(`i3-get-window-criteria`) built from `xwininfo` + `xprop` that prints a
copy/paste-ready criteria list when you click a window.

VHK borrows this directly as `vhk pick-window`.

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
