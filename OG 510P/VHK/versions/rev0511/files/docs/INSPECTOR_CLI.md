# Inspector CLI helpers

VHK will eventually ship a full "Inspector" panel (Window Spy + AT-SPI tree +
vision capture), but the CLI already provides a few practical building blocks.

## Pick a window → i3 criteria

```bash
vhk pick-window
```

This prompts you to click a window (via `xdotool selectwindow`, falling back to
`slop -f %i`) and prints a JSON payload that includes:

- WM_CLASS `instance` + `class`
- `WM_WINDOW_ROLE` when present
- window title
- PID (when available)
- geometry
- the raw clicked-window criteria string plus two suggestions:
  - `stable`: class + instance (+ window_role when present)
  - `exact`: class + instance (+ role) + exact title
- a live preview of how many current i3 windows match each suggestion when IPC is reachable

Example exact selector:

```text
[class="^Firefox$" instance="^Navigator$" window_role="^browser$" title="^Mozilla Firefox$"]
```

When you use `--no-json`, VHK prints the **stable** suggestion so you get a
safer default for `for_window`, `assign`, or binding criteria.

## Wayland-friendly: active Window Spy

On Wayland, click-to-inspect tools like `xdotool selectwindow` generally don't
work. VHK ships a focus-based inspector that uses compositor tooling when
available:

```bash
vhk window-spy
```

It prints a JSON payload that includes:

- compositor (`wm`)
- active window fields (best-effort)
- selector suggestions you can paste into:
  - `bindings[].when` or `hotstrings[].when`
  - `vhk run --require-window '{...}'`

Tip: add `--include-workspace` if you want to scope a selector to a workspace
name.

## Record selectors (Window Spy, but over time)

Sometimes a single `window-spy` snapshot isn't enough: titles change, and you
want to see which fields remain stable while you switch focus.

```bash
vhk record-selectors --duration-ms 3000
```

The JSON output includes `suggested.stable` / `suggested.exact` selectors and a
small summary of what fields varied. When you use `--no-json`, VHK prints a
minimal YAML snippet designed to be pasted under a `when:` block.

If titles vary, the `exact` suggestion may use a conservative `title_regex`
pattern (explicit alternation when there are only a few titles, or a prefix
match when it looks meaningful).

### A note on titles

i3 criteria for `class/instance/title/window_role` are regular expressions
(PCRE). Titles change frequently, so it’s usually best to match primarily on
`class`, `instance`, and `window_role`, and only use `title` with anchors
(`^...$`) for known-stable windows.

## Select a region

```bash
vhk select-region
```

Returns a `Region` JSON object (`x,y,w,h`), intended to be fed into:

- `vhk capture-needle`
- `CaptureScreenshot` steps
- future image/pixel/OCR steps that operate on screen regions

## Capture a needle (openQA-style)

```bash
vhk capture-needle ./my_project ok_button --out-dir assets/needles --tags "ok,button"
```

Creates:

- `assets/needles/ok_button.png`
- `assets/needles/ok_button.json`

The JSON format is compatible with openQA’s basic needle model: match/exclude/
ocr areas plus optional click points.


## Print a macro step at the current cursor position

When you're building mouse-driven macros and already have the pointer where you
want it, this helper prints a YAML step snippet:

```bash
vhk cursor-step click
vhk cursor-step move
```

Use `--json` if you prefer a single JSON object.


## Build rules from selectors or a clicked window

```bash
vhk build-rule --pick --workspace "2: web"
```

This command sits one step above `pick-window`: it turns selector fields into
ready-to-paste window-management snippets. Output can include:

- `assign ... <workspace>` for mapping-time workspace placement
- `for_window ... <commands>` for runtime i3 actions
- a devilspie2 Lua snippet for users who already run devilspie2
- `wmctrl` apply-once commands for X11-only fallbacks like `above` or sticky state

Useful flags:

- `--pick`: click a window first and seed selector fields from its properties
- `--workspace`: target workspace for placement
- `--float`, `--mark`, `--focus`, `--sticky`: common i3/devilspie2 actions
- `--x/--y/--width/--height`: geometry hints
- `--include-title`: include exact title in the emitted selector (fragile, but sometimes necessary)
- `--apply-once`: apply the generated actions to the current session immediately when possible

### Why `assign` vs `for_window` both matter

i3 documents an important behavioral difference:

- `assign` runs when the window is first mapped
- `for_window [criteria] move to workspace ...` can run later when properties change

That means workspace-placement rules are often safer as `assign`, while
`for_window` is better when you need to combine placement with other actions like
`floating enable`, `mark`, or geometry changes.

Example JSON-oriented workflow:

```bash
vhk build-rule --pick --workspace "2: web" --json
```

Example exact rule with extra actions:

```bash
vhk build-rule --pick --include-title --float --sticky --x 100 --y 80 --width 1200 --height 800 --no-json
```

## Stream WM events

When you’re trying to understand what your compositor is actually emitting,
use:

```bash
vhk wm-events --kind focus --kind title --with-window
```

This prints an event stream (optionally as JSON lines via `--json`) and can
attach best-effort window info.
