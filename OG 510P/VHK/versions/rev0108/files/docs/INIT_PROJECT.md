# Initializing projects

VHK projects are intentionally lightweight: a project is just a folder containing
`project.yaml`, a `macros/` directory, and (optionally) `assets/`.

This mirrors the "bundle" style used by image-based automation tools where the
script and its images live together (e.g., SikuliX `.sikuli` folders).

## `vhk init`

Create a new project skeleton:

```bash
vhk init ./my_project --name "My Project"
```

This creates:

- `project.yaml`
- `macros/main.yaml`
- `assets/needles/` and `assets/baselines/`
- `assets/TODO.png` (a 1×1 placeholder PNG you can safely reference from
  **disabled** TODO steps)

Templates:

- `--template minimal` (default): tiny macro that logs + returns
- `--template demo`: includes a Notify + TypeText example
- `--template vision`: includes **disabled** vision stubs (WaitForImage/ClickNeedle)

If the target directory already exists and is non-empty, `vhk init` refuses to
run unless you pass `--force`.

## `vhk new-macro`

Add a new macro file under `macros/` and optionally register it under
`project.yaml`:

```bash
vhk new-macro ./my_project hello_world --template demo
```

If you prefer the loader’s auto-discovery behavior (load all `macros/*.yaml`),
use `--no-register`.
