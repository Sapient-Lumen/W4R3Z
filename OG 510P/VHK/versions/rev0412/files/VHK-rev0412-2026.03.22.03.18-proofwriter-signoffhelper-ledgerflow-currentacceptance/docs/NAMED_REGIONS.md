# Named regions (ROI)

UI automation gets dramatically more reliable when you *scope* visual operations
(image search, pixel search, OCR) to a stable **region of interest** instead of
scanning the whole screen.

This idea shows up across the "visual automation" ecosystem:

- **Sikuli/SikuliX** treats a `Region` as a first-class primitive: find/click/wait
  inside a region, and even observe changes in a region.
- **Pulover’s Macro Creator** (AutoHotkey GUI) exposes an explicit *Image Search*
  region/capture area and includes UX for adjusting the rectangle with hotkeys.

VHK supports the same workflow via **named regions** stored in `project.yaml`.

## Define regions in `project.yaml`

```yaml
regions:
  toolbar:
    x: 0
    y: 0
    w: 1400
    h: 120

  right_panel:
    x: 1480
    y: 0
    w: 440
    h: 1040
```

## Capture a region interactively

Use the same tool VHK already uses for region selection (`slop` on X11, `slurp` on
Wayland):

```bash
vhk select-region --project /path/to/project --name toolbar
```

If the name already exists, pass `--overwrite`.

## Use a named region in macros

Anywhere a step supports `region:`, you can reference a named region:

```yaml
- type: WaitForImage
  needle_path: assets/needles/ok.png
  region: "@toolbar"
  timeout_ms: 8000
```

Shorthand: if the string matches a key under `project.yaml` `regions:`, you can
also write:

```yaml
region: toolbar
```

## Copy/paste geometry strings

VHK also accepts a simple geometry string form:

- `"640x480+10+20"` meaning `w=640`, `h=480`, `x=10`, `y=20`

This is convenient when you’re pasting coordinates from other tooling.
