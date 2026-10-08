# Revision REV0269 — explicit X11 adapter planning for AutoKey lanes

This revision turns a useful exporter into an explicit planning/runtime story.
VHK already knew how to generate an AutoKey pack, but the planner still treated
that lane as mostly invisible beside Espanso, remappers, and portal/helper
surfaces.

## What changed

- added `autokey-x11-adapter` to `plan-project` surface scoring for X11/i3
  projects that actually look like AutoKey-style text/hotkey workflows
- added `autokey-reviewable-adapter` to planner reference patterns so the
  X11 adapter lesson becomes machine-readable output instead of a buried doc
- updated text-tier macro route guidance so X11-class projects now surface
  `vhk gen-autokey-pack ...` alongside Espanso-oriented commands
- kept the lane narrow on purpose: this is a reviewable **X11 adapter** story,
  not a claim that AutoKey suddenly solves generic Linux or Wayland automation
- added a focused research note documenting the upstream lessons that justify
  the lane split

## Why it matters

A Linux-native AHK analogue cannot just accumulate exporters. It has to decide
which exported surfaces are actually part of the product story.

This revision makes one distinction more explicit:

- Espanso-class exports are a **text/package** answer
- AutoKey-class exports are a **reviewable X11 adapter** answer
- keyd/Kanata/KMonad/xremap-class exports are **low-latency trigger/remap**
  answers

Those lanes can cooperate, but they should not be collapsed into one fuzzy
"Linux automation" bucket.

## Validation

Focused suites pass for the affected planner/export surfaces:

- `tests/test_plan_project_cli.py`
- `tests/test_autokey_pack_cli.py`
- `tests/test_lint_project_cli.py`

The AutoKey planner regression coverage now checks that:

- X11 projects receive an explicit AutoKey surface candidate
- the corresponding planner pattern is present
- text-tier route/export guidance includes `gen-autokey-pack`
