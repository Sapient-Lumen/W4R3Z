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
- window title
- PID (when available)
- geometry
- a copy/paste-ready i3 criteria string like:

```text
[class="Firefox" instance="Navigator" title="^Mozilla Firefox$"]
```

### A note on titles

i3 criteria for `class/instance/title` are regular expressions (PCRE). Titles
change frequently, so it’s usually best to match primarily on `class` and
`instance`, and only use `title` with anchors (`^...$`) for known-stable windows.

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
