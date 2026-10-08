# X11 lexical recorder (`vhk record-x11`)

VHK currently ships a **baseline** ("lexical") recorder for X11 sessions:

```bash
vhk record-x11 --duration-ms 5000 > macros/recorded.yaml
```

It is intentionally closer to **xmacrorec-class** tooling than a full "studio".
The goal is to bootstrap authoring, then let future tooling convert the raw
recording into robust, wait-driven, selector-aware steps.

Recent recorder upgrades:

- motion-thinning presets: `--smoothing precise|normal|compact`
- distance-aware mouse move filtering via `--mouse-min-delta`
- pending motion flushes so short gestures still end at the correct final coordinate
- drag collapse now survives intermediate motion samples instead of falling back to down/up pairs

## How it works

- Uses `xinput test-xi2 --root` to observe global XI2 events.
- Translates `detail:` keycodes into keysyms using `xmodmap -pke`.
- Applies both **time-based** and **distance-based** mouse move thinning (record when time > T or distance > N).
- Converts events into VHK steps:
  - `KeyPress/KeyRelease` → `KeyDown`/`KeyUp`
  - `Motion` → sampled `MouseMove`
  - `ButtonPress/ButtonRelease` → `MouseClick` down/up
  - wheel buttons (4/5/6/7) → `MouseWheel`
  - inserts `Delay` steps for large gaps (configurable)

This is inspired by the way classic recorders avoid motion floods: only record
motion changes periodically, and capture down/up transitions as the "semantic"
events.

## Post-processing (recommended)

You can have the recorder immediately clean up the raw step stream using the same
optimizer that powers `vhk optimize`:

```bash
vhk record-x11 --duration-ms 5000 --optimize > macros/recorded.yaml

# More faithful pointer path
vhk record-x11 --duration-ms 5000 --smoothing precise > macros/recorded_precise.yaml

# More portable / lower-noise output
vhk record-x11 --duration-ms 5000 --smoothing compact --optimize > macros/recorded_compact.yaml
```

This merges delay fragments, squashes redundant mouse moves, and collapses common
keypress/click patterns into higher-level steps for easier editing. When text
compression is enabled, shifted text runs such as `Hello!` can now collapse into
one `TypeText` span instead of a pile of `shift+...` chords, and short corrected
runs such as `hex` + `Backspace` + `llo` or `helo` + `Left` + `Left` + `l` + `Right` + `Right` can now collapse to the final literal
text users actually meant.

For heavy text entry, you can optionally collapse rapid character streams into
a single `TypeText` step:

```bash
vhk record-x11 --duration-ms 5000 --optimize --optimize-compress-text > macros/recorded.yaml

# For long literal single-line text, you can also ask the optimizer to rewrite
# the recovered TypeText step into explicit clipboard-paste mode. This stays
# opt-in so Return/Tab-heavy form snippets remain typed by default.
vhk record-x11 --duration-ms 5000 --optimize --optimize-compress-text \
  --optimize-promote-paste-text --optimize-paste-text-min-chars 80 > macros/recorded_fasttext.yaml
```

## Writing into a project

If you already have a VHK project folder (created with `vhk init`), you can
record directly into it:

```bash
vhk record-x11 --duration-ms 4000 --optimize --project ./my_project --macro login_flow
```

This writes `macros/login_flow.yaml` (or the path configured in `project.yaml`
under `macros:`) and optionally registers the macro name in `project.yaml`.

This workflow is deliberately similar to "codegen" tools that generate scripts
directly into your repository while you interact with the UI, then expect you
to review/edit the output.

### Generated warm-stack recording review

The generated i3/X11 warm-runtime stack now treats recorder evidence as a
first-class control-plane surface instead of optional console trivia:

- `bin/record_macro.sh <macro>` now writes a predictable sidecar next to the
  resolved macro source (`<macro>.window-context.yaml`)
- that wrapper also defaults pointer replay toward `--coord-mode-mouse window`
  so recorded pointer steps are more likely to survive a window move
- `bin/macro_recording_json.sh <macro>` summarizes the sidecar for humans or a
  private LLM without making them scrape YAML directly

### Optional window-context capture

Recent recorder work now lets authors capture app/window scope at the same time
as lexical input:

```bash
vhk record-x11 --duration-ms 4000 --optimize \
  --project ./my_project --macro login_flow \
  --capture-window-context --apply-window-context \
  --window-context-out build/login_flow.window-context.yaml
```

What this does:

- samples the active window while recording
- derives a conservative `stable` selector and a more title-sensitive `exact`
  selector using the same selector-suggestion heuristics as `vhk record-selectors`
- can write that review payload to a JSON/YAML sidecar
- can apply only the `stable` selector to the recorded macro's top-level `when:`
  block when writing into a project

This is intentionally conservative: recorded macros should gain honest app scope
more easily, but title-sensitive or regex-heavy matches still stay reviewable
sidecar evidence instead of being silently baked into the macro.

### Relative mouse coordinates (`CoordMode`)

VHK can also turn the recorded pointer steps into active-window-relative or
client-relative coordinates:

```bash
vhk record-x11 --duration-ms 4000 --optimize \
  --coord-mode-mouse client \
  --project ./my_project --macro login_flow \
  --apply-window-context
```

What this does:

- samples active-window geometry while recording (the same capture lane used for
  selector suggestions)
- rewrites recorded `MouseMove`, `MouseDrag`, and `MouseClickAt` coordinates so
  they are relative to the recorded window or client area
- prefixes the output with `CoordMode(target=mouse, mode=window|client)`
- preserves the chosen relative anchor in the window-context sidecar when one is
  requested

Why this matters: Pulover-style authoring is much easier when clicks survive a
window move or workspace layout shift. This is still honest about Linux reality:
relative playback depends on the active window at run time, so combining
`--coord-mode-mouse` with `--apply-window-context`, `when:`, explicit focus
steps, and/or the segmented window-guard lane is usually the right review
path.

For `client` mode, VHK falls back to the outer window rectangle when the current
compositor/tooling cannot provide a distinct client rect. That matches the
runner's best-effort runtime behavior on Linux backends that do not expose a
separate client geometry.

### Window-scoped segment guards

Some real recordings cross application boundaries: launch a browser, wait for a
terminal, hop back to a dialog, and so on. A flat lexical stream loses that
truth.

`vhk record-x11` can now preserve those transitions directly:

```bash
vhk record-x11 --duration-ms 5000 --optimize \
  --segment-by-window-context \
  --window-guard-timeout-ms 3000 \
  --window-guard-scope active \
  --window-context-out build/flow.window-context.yaml
```

What this does:

- watches active-window changes during the same capture lane already used for
  selector suggestions
- splits long `Delay` spans at window boundaries so guards land where the window
  really changed instead of only between later user actions
- injects recorder-shaped window guards at segment boundaries
- defaults those guards to the recorded *active* window truth by adding `focused: true`; authors can opt back to simple presence checks with `--window-guard-scope present`
- can stay purely state-based (`--window-guard-mode state`) or use an event lane (`--window-guard-mode event`) that keeps the first segment as `WaitForWindow` and then emits `WaitForWindowEvent` for future focus/workspace/title/geometry transitions when the recorder actually observed a transition
- prefers conservative `stable` selectors when one segment is clearly unique,
  but automatically falls back to per-segment `exact` selectors when multiple
  recorded windows would otherwise collapse into the same broad stable match
- when `--coord-mode-mouse window|client` is active, translates pointer steps
  per segment so multi-window recordings can stay relative to the correct window
  instead of inheriting the first segment's anchor forever
- with `--segment-on-title-change`, can also split one recorded window into
  multiple guarded segments when the title changes and that title change is part
  of the workflow truth (for example tab/document transitions inside one app)

This is still intentionally honest. These inserted guards are *recorded evidence*
that the active window changed, not a claim that VHK has discovered full UI
semantics. The default guard scope is `active` because the recorder sampled the
focused window, not merely a matching background window. `--window-guard-scope
present` remains available for authors who intentionally want broader existence
checks. `--window-guard-mode event` is intentionally narrower: it currently
requires `--window-guard-scope active`, because focus/workspace/title/geometry events are about the
foreground window, not just background existence. Geometry refresh segments can
now use `WaitForWindowEvent(event=geometry, ...)` too: on i3/sway that maps to
direct window-change notifications such as `move`, while generic X11/KWin and
other desktops use best-effort active-window geometry polling. They are the
recorder-shaped equivalent of `WinWaitActive` / Window Spy discipline: better
than raw timing, but still something authors should review.

When the recorded workflow is really about **future transitions** instead of just
proving state, you can opt into the event-shaped guard lane:

```bash
vhk record-x11 --duration-ms 5000 --optimize   --segment-by-window-context   --window-guard-mode event
```

That keeps the first segment as `WaitForWindow` (current-state proof at macro
start) and then uses `WaitForWindowEvent(event=focus|workspace|title|geometry, ...)` for
later recorded transitions whenever the recorder can honestly classify them that
way. Geometry waits are direct on i3/sway and polling-backed elsewhere.

When one workflow stays inside the same window identity but the title changes in
a meaningful way, you can opt into that extra fragility explicitly:

```bash
vhk record-x11 --duration-ms 5000 --optimize \
  --segment-by-window-context \
  --segment-on-title-change \
  --segment-on-workspace-change
```

That mode is intentionally opt-in because title-based waits are more brittle
than class/app-id waits. It exists for cases like browser-tab, editor-buffer,
or document-title transitions where the title is the only honest boundary the
recorder can observe.

## Caveats

- **X11 only.** In Wayland sessions, `xinput` usually only sees Xwayland devices
  (if present) and cannot record native-Wayland input.
- Layouts/remaps can affect keycode→keysym translation. We record the
  **unshifted** keysym and rely on modifier press/release events for
  combinations.
- Drag recording is best-effort; the baseline format is still useful even when
  complex gestures are flattened.

## Next steps (planned)

- A "convert recording" pass to suggest:
  - window scoping blocks (`when:`)
  - waits (`WaitForWindow`, `WaitForImage`, OCR waits)
  - replacing fragile coordinates with `ClickNeedle` / `VisualAssert`
- Optional X11 RECORD-extension based mode for better synchronization.
