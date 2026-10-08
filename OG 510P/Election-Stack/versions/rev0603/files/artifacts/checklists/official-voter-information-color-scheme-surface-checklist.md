# Official voter-information color-scheme surface checklist

Use this checklist when an election office needs the **current answer/help lane to remain coherent across light/dark theme variants, browser chrome theming, and color-scheme-sensitive embedded assets**.

## Scope and boundary review

- [ ] Record which public routes declare or effectively support light/dark theme variants.
- [ ] Distinguish this surface from ordinary contrast review, forced-colors / high-contrast system-palette override, broader identity-signal review, and outright third-party dependency failure.
- [ ] Keep theme-variant failures explicit instead of burying them inside generic “dark mode,” branding, or contrast residue.

## Variant-parity review

- [ ] Review important routes in each light/dark scheme the page declares or deliberately supports.
- [ ] Check whether warnings, selected states, invalid-field cues, and next-step actions remain reconstructible in each reviewed variant.
- [ ] Confirm that browser-provided controls and affordances (such as form controls or spellcheck underlines) do not visually detach from the route in one scheme.

## Browser chrome and metadata review

- [ ] Review any use of `color-scheme`, `<meta name="color-scheme">`, or `<meta name="theme-color">` for coherence with the same official route.
- [ ] Check whether browser toolbar/address-bar theming or surrounding UI could imply a different state or product in one scheme.
- [ ] Avoid claiming dual-theme support casually when only one variant keeps the route legible and state-clear.

## Embedded asset review

- [ ] Review theme-sensitive SVGs, iframes, logos, icons, and other embedded assets whose appearance may inherit the active color scheme.
- [ ] Check whether any embedded or cross-origin asset becomes misleading, unreadable, or identity-confusing only in one scheme.
- [ ] If the issue is that the dependency fails to load at all, route the fix to the external-dependency lane rather than to this theme-variant lane.

## Toggle humility and evidence review

- [ ] Keep any manual theme toggle subordinate to the same controlling answer/help lane.
- [ ] Preserve a small public digest of reviewed routes, declared schemes, theme-sensitive assets, and last review time.
- [ ] Do not preserve individualized theme-preference telemetry or exhaustive screenshot matrices merely to prove the posture was reviewed.
