# 30 — Source diversity and common-mode dependency posture — rev0068

## Purpose

`source_posture` says whether a TimeState is single-source, multi-source, authenticated-only, mixed, holdover-only, or unknown. It deliberately does not expose a source roster or describe upstream dependency topology.

rev0068 adds `extension_hooks.source_diversity_posture` as a compact, profile-facing hook for the missing question: whether apparent timing-source agreement is likely to share a common root or failure mode.

The hook is summary-only. It is not a source-selection algorithm, grandmaster-election protocol, PNT risk register, provenance graph, or exported path history.

## Shape

```json
{
  "dependency_class": "single_source | multiple_sources_same_root | multiple_roots_common_distribution | multiple_independent_roots | holdover_from_prior_source | unknown",
  "common_mode_risk": "confirmed_common_mode | possible_common_mode | mitigated_by_diversity | not_assessed | unknown",
  "assessment_basis": "local_measurement_summary | operator_configuration | profile_catalog_rule | local_policy_rule | policy_redacted | unknown",
  "evidence_posture": "claimed | assessed | profile_defined | redacted | unknown",
  "export_detail": "summary_only"
}
```

## Normative constraints

- `export_detail` MUST remain `summary_only`.
- The hook MUST NOT contain source identifiers, upstream path history, raw observations, grandmaster-election data, or local clock algorithm details.
- `timestate.source_posture: single_source` MUST NOT be paired with a multiple-source dependency class.
- `timestate.source_posture: local_holdover_only` MUST use `holdover_from_prior_source` or `unknown`.
- `common_mode_risk: mitigated_by_diversity` requires `dependency_class: multiple_independent_roots`.
- `multiple_sources_same_root` may show agreement, but MUST NOT claim common-mode risk is mitigated by diversity.

## Profile placement

```text
P1: requestable
P2: requestable
P3: requestable
P4: profile-default
P5: profile-default
P6: requestable
```

P4 and P5 make this profile-default because precision network and critical-infrastructure consumers can be misled by `multi_source_agreement` when all apparent sources share a common root, common distribution path, or common operator dependency.

## Evidence class

rev0068 adds `source_diversity_summary` to the evaluator evidence class catalog. It may satisfy a source-diversity obligation, but only as a compact summary. It does not license source roster export.

## Boundary

A consumer may use the hook to decide whether a profile obligation is met, whether fallback is required, or whether current policy accepts a retained assessment. The hook does not by itself prove source correctness, UTC traceability, freshness, or clock continuity.
