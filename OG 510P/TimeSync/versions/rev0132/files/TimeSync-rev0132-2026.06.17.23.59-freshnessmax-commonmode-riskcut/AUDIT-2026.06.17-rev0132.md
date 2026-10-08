# Audit — rev0132 freshness max and common-mode risk cut

## What was riskiest

After rev0131, the next dangerous failure mode was not missing vocabulary. It was a too-optimistic aggregate summary:

- `freshness.max_staleness_ms` used the minimum input value, which could hide the stale input that forced fallback.
- The multi-source diversity hook summarized overlapping adapter states as `multiple_roots_common_distribution`, even though the input adapter states only supported same-root/common-mode-risk summaries.

Both defects could lead a consumer to treat a conservative fallback/intersection output as fresher or more independently sourced than it really was.

## What changed

- Multi-source freshness now uses the maximum admitted input staleness.
- Input `source_diversity_posture` summaries are collected and carried forward.
- Tests now assert `freshness_max_staleness_ms`, `dependency_class`, and `common_mode_risk` directly.
- A generated fallback example was added as `TV-132-001`.

## What remains open

- Live chronyd/ntpd/NTPsec host capture remains unproven in this cloud container.
- NTS and symmetric-key reports remain unverified until packet/session evidence is actually checked.
- Named UTC realization and leap-smear policy discovery remain open.
- PTP comparison remains open.
- The multi-source adjudicator is still not a replacement for NTP's source-selection and clustering algorithms.
