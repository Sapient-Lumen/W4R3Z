# Migration map — rev0066 to rev0067

## Added

- `extension_hooks.source_diversity_posture`.
- `source_diversity_summary` evidence class.
- `spec/30-source-diversity-and-common-mode-posture.md`.
- Positive P5 source-diversity fixture.
- Negative fixtures for source-diversity contradictions and roster leakage.

## Profile obligation changes

- P1/P2/P3/P6: source diversity is requestable.
- P4/P5: source diversity is profile-default.
- P4/P5 evidence minimum summaries include `extension_hooks.source_diversity_posture`.

## Digest impact

All six profile normative digests changed because obligation placement is normative.

## Compatibility

rev0066 consumers can ignore the new hook when it is requestable. P4/P5 rev0067 satisfied assessments require the hook when using the rev0067 profile catalog.
