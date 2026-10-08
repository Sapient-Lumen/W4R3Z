# Revision REV0270 — explicit narrow Wayland text lanes for virtual-keyboard typing

This revision tightens one subtle planning overclaim.

VHK already knew about `wtype`, clipboard, and helper-backed text injection, but
`plan-project` still leaned too casually toward `wtype` as though it were the
obvious generic Wayland text answer. That made the planner more optimistic than
modern Linux desktops deserve.

## What changed

- added `wtype-wayland-text` to `plan-project` surface scoring for Wayland
  projects that actually look like text-heavy/snippet-heavy automation
- added `wtype-narrow-wayland-text-lane` to planner reference patterns so the
  fast typed-text lesson becomes machine-readable output instead of just prose
- added `wtype-virtual-keyboard-boundary` to ecosystem lessons so the repo now
  explicitly teaches that compositor protocol support is part of the product
  story
- changed the generic Wayland `text_injection` toolchain default from a blunt
  `wtype` answer to a clipboard-first split lane with `wtype` as the explicit
  fast path when the session proves it
- added a focused research note documenting why this lane should stay narrow and
  why portal/global-shortcut progress does **not** magically turn Wayland text
  typing into one universal backend

## Why it matters

A Linux-native AHK analogue needs the same discipline for text entry that it now
has for triggers and remappers:

- text/package exports are the broad, reviewable lane
- virtual-keyboard typing is a **narrow compositor-dependent fast path**
- helper/uinput daemons remain a separate fallback/escape hatch

Those are complementary, but they are not interchangeable.

## Validation

Focused suites pass for the affected planning and planner-consuming surfaces:

- `tests/test_plan_project_cli.py`
- `tests/test_design_pack_cli.py`
- `tests/test_portability_pack_cli.py`
- `tests/test_setup_pack_cli.py`
- `tests/test_session_fit_pack_cli.py`
