# Ballot-style and sample-ballot surface checklist

Use this quickcheck before publishing or correcting public ballot-style / sample-ballot information.

## Minimum publishables
- [ ] One authoritative public lookup or sample-ballot directory is declared for the election scope.
- [ ] Each published style has a stable `ballot_style_id` and effective timestamp/window.
- [ ] Each current sample-ballot artifact has a recorded digest.
- [ ] Public help / fallback contact information is present.

## Accessibility + language
- [ ] Primary sample-ballot path is available in an accessible format (for example HTML or tagged PDF).
- [ ] Plain-language summary / help text is present.
- [ ] Required minority-language versions or notices are published where applicable.
- [ ] Inaccessible or unavailable paths have an alternate help route.

## Supersession discipline
- [ ] Corrections produce an explicit superseding event; no silent replacement.
- [ ] Correction notice identifies the superseded style/version or artifact digest.
- [ ] Correction notice includes effective time and voter-help path.
- [ ] If the correction changes voter actionability, related directory / polling-place references are cross-checked.

## Parity
- [ ] Website, downloadable sample-ballot artifact, mirror, and hotline script agree on the effective state.
- [ ] Any divergence is captured in a parity snapshot or incident note.
- [ ] Cache/freshness behavior for the primary public surface has been checked.

## Safe bounds
- [ ] No voter-file extracts, districting internals, or sensitive proofing workpapers are published by default.
- [ ] Tiny-cell or targeting-sensitive usage analytics are excluded.
- [ ] Raw internal artifacts move only through controlled disclosure when needed.
