# Accessibility stack boundaries — 2026-03-09

This note exists to keep future passes from collapsing several genuinely different accessibility layers into one fuzzy “a11y crate” story.

## Main judgment

Rust now has meaningful accessibility substrate.
That means the sharper missing crates are increasingly **coordination artifacts above substrate**, not more raw bindings.

The useful stack here is:

1. **authoring lane** — semantic intent inside the toolkit or application (often AccessKit-shaped),
2. **platform exposure lane** — AT-SPI / UIA / NSAccessibility facts as exposed to assistive technologies,
3. **policy lane** — scenario-derived checks and standards-informed expectations,
4. **support lane** — captures, diffs, repro bundles, and manual-review markers.

A good pass should say which lane a proposal owns.

## Proposal boundaries

### P-0087 UI Accessibility Kit
Read **P-0087** as the **authoring + doctor + gating** layer:

- toolkit integration patterns,
- AccessKit usage guidance,
- local semantic overlays,
- CI-friendly checks for obvious missing names/roles/focus traps.

### P-0202 Cross-Platform Accessibility Interop & Conformance Kit
Read **P-0202** as the **capture + normalization + interop lab** layer:

- cross-platform tree/event capture,
- normalized outputs,
- scenario packs,
- semantic diffs,
- portable repro bundles,
- and explicit comparability rules.

These proposals can share bundle vocabulary and fixtures, but they should not merge into one giant “accessibility platform”.

## Working rule

When touching accessibility work in this archive, do **not** collapse:

- authoring semantics,
- platform API exposure,
- standards-informed policy expectations,
- and user/support handoff artifacts

into one vague claim that “the accessibility crate handles it”.

Future passes should prefer:

- lane-explicit artifacts,
- redaction-aware bundles,
- scenario packs instead of prose-only checklists,
- and explicit manual-review markers where automation is insufficient.

They should avoid:

- pretending WCAG is fully automatable,
- pretending AccessKit alone solves cross-platform regression triage,
- or proposing another platform binding when the sharper gap is the reviewable capture artifact above existing bindings.
