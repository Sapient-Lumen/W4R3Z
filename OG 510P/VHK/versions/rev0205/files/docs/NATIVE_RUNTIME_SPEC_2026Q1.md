# Linux-native runtime spec (2026 Q1)

This is the compact product/runtime spec that sits on top of the larger
`docs/SPECS.md` inventory.

## Goal

Build VHK into a Linux-native automation stack that preserves the practical
value of AutoHotkey + Pulover's Macro Creator:

- fast keyboard/pointer automation
- window-aware app targeting
- visual/OCR fallback when semantic hooks are unavailable
- recorder-to-robust-macro authoring flow
- explicit diagnostics when the host/session cannot support a capability

## Non-goals

- pretending Wayland is one uniform capability surface
- promising full AHK parity through one universal backend
- hiding helper/service/portal requirements behind vague “supported” labels

## Product shape

VHK should ship as four connected surfaces:

1. **Runner/engine**
   - deterministic macro execution
   - wait-driven control flow
   - variables, expressions, retries, diagnostics
2. **Recorder + conversion helpers**
   - raw capture on X11 where possible
   - conversion toward structured waits, app scopes, and visual assertions
3. **Project/tooling layer**
   - planner, validator, linter, portability and deployment packs
   - explicit host/session capability modeling
4. **Future studio**
   - visual editing, capture, parameter forms, run history, issue review

## Capability tiers

### Tier A: X11 / i3-class first-party lane

This is the primary “AHK-like” lane today.

Required characteristics:

- low-latency pointer + keyboard injection
- stable window enumeration/focus data
- screenshot + OCR + image matching
- recorder support that can capture useful event detail

### Tier B: Wayland with compositor-native bridges

This is a real target, but not a single backend.

Required characteristics:

- explicit per-desktop routing (GNOME, KDE, wlroots, Hyprland, etc.)
- compositor-native dispatch/introspection where available
- portal and helper lanes treated as optional capability routes
- honest warnings when a project needs behavior the current session cannot
  provide cleanly

### Tier C: Portal/helper fallback lane

This lane is valuable for packaging and sandboxed environments, but must remain
capability-scoped rather than oversold.

Required characteristics:

- route selection based on live doctor/validate/planner output
- support docs that explain consent prompts, missing interfaces, and helper
  prerequisites
- safe fallback to launcher-driven, prompt-driven, OCR-driven, or WM-native
  flows when unrestricted hooks are unavailable

## Authoring rules

- prefer **waits over sleeps**
- prefer **window/app scope over blind global replay**
- prefer **semantic target → visual target → coordinate target** in that order
- keep diagnostics first-class: every brittle lane needs explainable failure
  output
- generated/project docs are part of the product, not afterthought packaging

## Runtime requirements

The engine should make these patterns easy and cheap:

- expression-based branching and looping
- expression-based waits (`WaitUntil`) for observable state
- retries/backoff/jitter on flaky edges
- fast region-limited visual search
- per-session backend selection with capability reporting
- clean macro parameter collection and saved profiles

## Performance envelope

VHK should optimize for:

- low overhead between steps on X11/native lanes
- scoped screenshots/vision work instead of full-screen brute force by default
- bounded polling with backoff instead of busy loops
- generated macros that remove redundant mouse motion and dead sleeps

## Reliability envelope

Every shipping lane should answer:

- what triggers it
- what permissions/helpers it needs
- what evidence proves it works on a host
- what fallback lane exists when the preferred route fails

## Immediate implementation priorities

1. keep strengthening wait-driven control flow and recorder conversion
2. sharpen app/window scoping on X11 and compositor-native lanes
3. keep Wayland support route-based, not slogan-based
4. build studio/editor surfaces on top of the planner/capability language that
   already exists in the repo
5. keep packaging/install/rehearsal/support artifacts reviewable and reversible

## Acceptance bar for “Linux-native AHK-class” progress

A real milestone should be able to demonstrate all of the following on at least
one target lane:

- record a workflow
- convert it into a scoped, wait-driven macro
- rerun it repeatedly without hand-edited sleeps
- explain what would fail on a different session and why
- export/install it through a native Linux surface without mystery steps
