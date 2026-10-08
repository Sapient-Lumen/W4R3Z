# Multi-source adjudicator hardening — rev0132

rev0132 audits the current-use adjudicator added in rev0131 and corrects two places where a consumer-facing summary could become too optimistic.

## Freshness max guard

When multiple local assessed states are admitted into one current-use decision, the combined `freshness.max_staleness_ms` is now the maximum of the admitted inputs. The previous implementation used the minimum, which could advertise the freshest input while the output decision still depended on a stale fallback input.

The executable regression is `MULTISOURCE-P1-WEAK-FALLBACK-CANNOT-UPGRADE`, which now expects `freshness_max_staleness_ms: 3600000.0` when a fresh satisfied input overlaps a stale fallback input.

## Common-mode carry-forward

The adjudicator now reads each input state's `extension_hooks.source_diversity_posture`. If any input reports `multiple_sources_same_root` or confirmed common-mode risk, the combined output keeps `dependency_class: multiple_sources_same_root` with `common_mode_risk: possible_common_mode` instead of upgrading overlap to a stronger multiple-roots/common-distribution summary.

This remains summary-only. It does not export source identifiers, source rosters, path history, or clock-selection internals.

## Boundary retained

The adjudicator is still not an NTP selection/cluster algorithm, not a truechimer/falseticker implementation, and not an independence proof. It consumes already-assessed TimeSync local states and protects current-use admission from cherry-picking, freshness understatement, and diversity overclaim.
