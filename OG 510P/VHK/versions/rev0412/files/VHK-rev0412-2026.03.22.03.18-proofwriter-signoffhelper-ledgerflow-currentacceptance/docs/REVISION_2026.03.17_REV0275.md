# REV0275 — Picker-native chooser lanes become planner-visible

Date: 2026-03-17
Codename: choosertruth-pickerlane-scriptpath-riverglass

## What changed

This revision turns Linux picker-native chooser workflows from implied launcher
trivia into an explicit planning lane.

Added:

- `picker-native-chooser` to `plan-project` surface choices
- `script-mode-picker-lane` to reference patterns
- `picker-protocol-thin-launch-surface` to ecosystem lessons
- updates to planning/spec/issue docs so chooser-rich flows are treated as a
  real Linux-native control surface

## Why

VHK already had most of the runtime pieces:

- prompt-aware macro steps
- the project palette
- launcher-script export
- rofi-mode export

But the planner still left a gap between:

- “prompt-rich workflow”
- “palette exists somewhere”
- actual Linux-native picker shells like rofi/fuzzel/wofi

That gap matters because searchable chooser UIs are one of the most Linux-native
ways to drive automation without overloading the global keyspace or inventing a
custom GUI for every project.

## Product effect

`plan-project` can now say something sharper for chooser-heavy projects:

- keep one stable action catalog
- expose picker-native entry surfaces explicitly
- let VHK remain the runtime after selection instead of hiding logic in picker
  scripts

That keeps VHK more Linux-native while still learning from existing tools rather
than hand-waving at “launchers” in general.

## Tests run

Passed:

- `tests/test_plan_project_cli.py`
- `tests/test_design_pack_cli.py`
- `tests/test_portability_pack_cli.py`
- `tests/test_setup_pack_cli.py`
- `tests/test_lint_project_cli.py`

## Docs updated

- `docs/SPECS.md`
- `docs/PLAN_2026.03.17_LINUX_NATIVE_AHK_PARITY.md`
- `docs/ISSUES_2026Q1.md`
- `docs/RESEARCH_2026.03.17_PICKER_NATIVE_CHOOSER_LANES_AND_SCRIPT_MODE_PROTOCOLS.md`
