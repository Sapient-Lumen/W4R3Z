# FT-0066 closure — source diversity and common-mode dependency posture

Closed in rev0067.

## Decision

Add `extension_hooks.source_diversity_posture` as a compact, summary-only hook. The hook distinguishes single source, same-root multi-source, common-distribution multi-root, independent-root diversity, holdover-from-prior-source, and unknown dependency posture.

## Why

`source_posture: multi_source_agreement` is not enough. Multiple timing feeds can agree while sharing GNSS dependency, an upstream grandmaster, a common operator policy, a distribution path, or another common-mode failure surface.

## Guardrails

- No source roster.
- No path history.
- No raw observations.
- No clock-selection or grandmaster-election algorithm.
- No conversion into a provenance graph or PNT risk register.

## Validator-backed rules

- Single-source TimeState cannot claim multiple independent roots.
- Local-holdover-only TimeState must report holdover/unknown dependency posture.
- Same-root multi-source posture cannot claim common-mode risk is mitigated by diversity.
- Discovery-returned source-diversity values are nested schema validated.
- `source_diversity_summary` is an allowed evidence class but remains summary-only.
