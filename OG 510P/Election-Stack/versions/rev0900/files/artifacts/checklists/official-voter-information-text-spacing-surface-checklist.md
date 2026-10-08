# Official voter-information text-spacing surface checklist

Use this checklist when an election office needs the **current answer/help lane to remain readable when voters increase line, paragraph, word, or letter spacing through ordinary accessibility tools**.

## Scope and boundary review

- [ ] Record which public routes contain decisive text that voters must read before they can act or continue.
- [ ] Distinguish this surface from generic reflow/zoom review, contrast review, field-entry-hint review, keyboard-open recovery, and reader-mode extraction.
- [ ] Keep spacing-induced clipping/overlap failures explicit instead of silently burying them inside generic mobile or typography polish.

## Spacing-override review

- [ ] Review important routes with text spacing increased to the bounded metrics used by WCAG text-spacing testing.
- [ ] Check whether text containers can expand rather than clipping or hiding content when spacing increases.
- [ ] Review short strings too: labels, chips, warnings, helper text, breadcrumbs, tabs, and action controls.

## Clipping and overlap risk review

- [ ] Check fixed-height, overflow-hidden, or absolutely positioned text containers for clipping or overlap risk.
- [ ] Make sure warning text, office-contact details, and next-step cues do not disappear once spacing expands.
- [ ] Allow wrapping or expansion when needed instead of preserving one-line styling at the cost of readability.

## Language/script and recovery review

- [ ] Record any language/script-specific applicability limits explicitly instead of assuming one spacing model fits every locale.
- [ ] Keep a truthful recovery story when a component cannot remain single-line under increased spacing.
- [ ] Do not imply that a custom spacing widget is required; the review is about resilience to ordinary user overrides.

## Evidence and minimization review

- [ ] Preserve a small public digest of reviewed routes, spacing bounds, critical text components, and last review time.
- [ ] Do not preserve individualized accessibility settings, user-style telemetry, extension inventories, or session replays merely to prove the posture was reviewed.
