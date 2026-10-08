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
- `docs/VHK_STARTER_GUIDE.md` (planner-derived onboarding guide)
- `docs/VHK_STARTER_PLAN.json` (machine-readable planner snapshot for the new project)

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

## Starter artifacts

By default `vhk init` now bootstraps two planning artifacts from the same
strategy engine used by `vhk plan-project`:

- `docs/VHK_STARTER_GUIDE.md`
- `docs/VHK_STARTER_PLAN.json`

These are intentionally **session-agnostic** starter materials. They summarize
likely product lanes, integration targets, deployable surfaces, setup recipes,
toolchain choices, reference patterns, and early verification gates for the new
project before you have run desktop-specific checks.

That makes `init` a better Linux-native onboarding step: the project begins with
a concrete install/deployment story instead of a bare folder plus TODO macros.

Disable either artifact if you want a leaner skeleton:

```bash
vhk init ./my_project --no-starter-guide --no-starter-plan-json
```

Refresh the thinking later on the real target session with:

```bash
cd my_project
vhk doctor --json
vhk validate . --json
vhk plan-project . --json
```
