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
keypress/click patterns into higher-level steps for easier editing.

For heavy text entry, you can optionally collapse rapid character streams into
a single `TypeText` step:

```bash
vhk record-x11 --duration-ms 5000 --optimize --optimize-compress-text > macros/recorded.yaml
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
