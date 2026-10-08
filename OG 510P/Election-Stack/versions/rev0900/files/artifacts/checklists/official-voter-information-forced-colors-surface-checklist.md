# Official voter-information forced-colors surface checklist

Use this checklist when an election office needs the **current answer/help lane to remain understandable when a browser enters forced-colors / high-contrast mode and replaces the authored palette with a user-selected limited system palette**.

## Scope and boundary review

- [ ] Record which public routes depend on visible state, focus cues, icons, borders, fills, chips, or warning styling to expose the current answer/help lane.
- [ ] Distinguish this surface from ordinary contrast/non-color-cue review, keyboard-order review, durable validation-text review, text-spacing review, and reader-mode extraction.
- [ ] Keep forced-colors failures explicit instead of silently burying them inside generic “contrast” or “high contrast mode” residue.

## Forced-colors review

- [ ] Review important routes with forced-colors or equivalent OS/browser high-contrast palette override active.
- [ ] Check whether selected states, warnings, invalid fields, and next-step cues remain visually recoverable when authored colors, shadows, or decorative backgrounds are overridden.
- [ ] Review focus indicators under forced colors, not just in the ordinary authored palette.

## Custom-control and icon review

- [ ] Check whether custom controls still look like controls when forced colors follows native semantics rather than ARIA-added semantics.
- [ ] Review SVG icons, arrows, and state markers whose `fill`/`stroke` colors might disappear against the forced palette.
- [ ] Add simple borders/system-color adjustments where needed instead of relying on shadows or decorative backgrounds alone.

## forced-color-adjust humility review

- [ ] Keep any `forced-color-adjust` opt-outs rare, explicit, and justified by better legibility/state support.
- [ ] Do not use `forced-color-adjust` merely to preserve branding or defeat the voter’s chosen color posture.
- [ ] Remember that opting out can also disable browser-provided text backplates and other legibility help.

## Evidence and minimization review

- [ ] Preserve a small public digest of reviewed routes, critical visual components, any explicit opt-outs, and last review time.
- [ ] Do not preserve individualized preference telemetry, browser-extension fingerprints, or exhaustive screenshot inventories merely to prove the posture was reviewed.
