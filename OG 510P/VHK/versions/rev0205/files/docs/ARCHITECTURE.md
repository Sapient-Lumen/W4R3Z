# Architecture (early scaffold)

This repo currently implements the **headless runner** and a growing set of primitives.
The long-term goal is a full Studio (record/inspect/compose/debug/run) built on top
of the same runtime model.

For an explicit “what are we building?” contract, see `docs/SPECS.md`.

## Layers

- **Project**: folder-based packaging format (manifest + macros + assets).
- **Core model**: typed step nodes (a workflow is displayed as a list, but evolves into a graph).
- **Runner**: executes a macro with variable interpolation + small expression evaluator.
- **Backends / adapters**:
  - `vision/`: OpenCV template matching + pixel search + Tesseract OCR
  - `i3/`: minimal i3 IPC client (pure Python socket protocol) + tree matching helpers
  - `system/`: thin wrappers over common CLI tools
    - screenshot (`maim` / ImageMagick `import`)
    - input (`xdotool`)
    - clipboard (`xclip` / `xsel`)
    - notify (`notify-send` / `dunstify`)
    - region selection (`slop`) for capture tooling

## Why this shape?

The requirements document emphasizes:

- a project format that bundles workflows + assets
- headless run mode
- vision primitives (ImageSearch/PixelSearch/OCR)
- i3 IPC as the authoritative WM API
- "AHK feel": waiting/retry/diagnostics everywhere

This scaffold creates stable interfaces now, so later we can swap implementations:

- replace file-based screenshots with live X11 capture + an interactive inspector
- replace template matching with multi-scale matching and per-asset tuning UI
- adopt openQA-style needles (PNG + JSON match/exclude/OCR areas) as the asset model
- add AT-SPI selectors and event-based waits
- split UI (studio) from OS integration (agent/helper), following patterns from Ui.Vision

## Observability & safety

- The runner can write a JSONL timeline (`docs/RUNNER_LOGGING.md`).
- A simple panic-file mechanism can stop long-running macros between steps.
- `settings.dry_run` helps debug control-flow without triggering side effects.

## Safety notes

The expression evaluator is intentionally limited: it does not allow imports,
attribute assignment, or arbitrary function calls.
