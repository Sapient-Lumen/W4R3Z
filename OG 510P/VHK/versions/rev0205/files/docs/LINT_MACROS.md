# Linting macros (advisor mode)

VHK ships a baseline recorder (`vhk record-x11`). Like most macro recorders,
the raw output tends to contain **hard sleeps** (`Delay`) and **absolute pixel
coordinates** (`MouseClickAt`). Those work for quick hacks, but they are also
the main source of flaky automation when:

- the machine is slower/faster than usual
- the window is moved, a monitor scale/DPI changes, or the UI layout shifts

`vhk lint` is an *advisor* that points out common pitfalls and suggests a more
robust primitive.

## Commands

### Lint one macro

```bash
vhk lint macros/login.yaml
```

Machine readable output:

```bash
vhk lint macros/login.yaml --json
```

CI-friendly mode (non-zero exit code when warnings are present):

```bash
vhk lint macros/login.yaml --check --fail-on warning
```

### Lint a whole project

```bash
vhk lint-project .
vhk lint-project . --json
vhk lint-project . --check
vhk lint-project . --no-session-check
```

Project lint now does two jobs:

- macro-level hygiene (hard sleeps, coordinate clicks, broad searches, recorder noise)
- session-fit advice (for example: the project uses hotkeys or text injection, but the current desktop session reports those capabilities as missing or limited)

## What it looks for

This is intentionally best-effort and conservative.

### Fixed sleeps that look like "waiting for UI"

Most UI automation ecosystems recommend **waiting on a condition** rather than
sleeping a fixed time.

- Selenium: explicit waits / conditions (`WebDriverWait`) instead of sleeps.
  https://www.selenium.dev/documentation/webdriver/waits/
- Playwright: auto-waiting + locator retry-ability.
  https://playwright.dev/docs/best-practices

In VHK, prefer:

- `WaitForImage` / `WaitForText`
- `WaitForWindow` (i3/sway/Hyprland)
- `WaitForFile`, `WaitForNewFile`, `WaitForProcessExit`

Or replace a brittle sequence with a single robust step:

- `ClickNeedle` (wait + click)

### Coordinate-only clicks

Absolute coordinates (`MouseClickAt x/y`) can break when the window moves,
resizes, or a monitor scale changes.

Tools that use image recognition typically recommend clicking **relative to the
matched image/text**, rather than hard-coding pixel coordinates.

Reference:
https://www.macrorecorder.com/doc/find/

In VHK, prefer:

- `ClickNeedle` (template-match + openQA click points)
- `WaitForImage` + `MouseClickAt` using the match variables (`match_x/match_y`)

### Full-screen searches

OCR/template matching across the entire screen is slower and can increase false
matches. Lint will suggest adding a `region:`.

Tip: use `vhk select-region` to capture a region interactively.

### Tight polling loops

Polling too frequently can burn CPU for little benefit. Lint will flag very low
`poll_ms` values.

### Recorder artifacts

If a macro contains lots of `KeyDown/KeyUp`, `MouseClick(down/up)`, or repeated
`MouseMove`, lint suggests running:

```bash
vhk optimize <macro.yaml> --in-place
```

## Philosophy

`vhk validate` is a **static correctness** check (references, expressions,
required assets).

`vhk lint` is a **workflow advisor**:

- it is ok to ignore warnings when you know a click is stable
- it is meant to nudge you toward more resilient primitives when you are
  building something you want to keep working
