# TimeSync rev0132

rev0132 continues FT-0121 with a safety hardening pass on the multi-source adjudicator. rev0131 prevented cherry-picking by intersecting overlapping assessed intervals; rev0132 corrects the next risk: combined freshness must be governed by the stalest admitted input, and source-diversity/common-mode summaries must not be upgraded just because two assessed intervals overlap.

The risk cut is executable and deliberately narrow. It changes the current-use adjudicator and its tests; it does not add a new registry, a clock-selection algorithm, or an independence proof.

## Start points

1. `tools/multisource_adjudicator.py` — executable multi-source local-state adjudicator with conservative freshness and common-mode carry-forward.
2. `tests/multisource-adjudication.yaml` — overlap, weak-lane, freshness-max, common-mode, and disjoint-interval acceptance cases.
3. `examples/evaluator/multisource-p1-stale-freshnessmax-commonmode-fallback.json` — generated fallback example proving stalest-input freshness is retained.
4. `examples/evaluator/multisource-p1-overlap-intersection-satisfied.json` — generated overlap example with same-root diversity posture carried forward.
5. `tools/ntp_bound.py` and `tools/adapter_equivalence.py` — retained shared-bound and cross-adapter equivalence guards.
6. `AUDIT-2026.06.17-rev0132.md` — audit/refactor notes and remaining risks.

## What changed in rev0132

- Changed multi-source `freshness.max_staleness_ms` from the minimum input value to the maximum input value.
- Added executable expectations for `freshness_max_staleness_ms`, `dependency_class`, and `common_mode_risk` in the multi-source self-test.
- Carried input `source_diversity_posture` summaries into the output adjudication instead of replacing them with a stronger multiple-roots/common-distribution claim.
- Added generated semantic-vector example `TV-132-001` for the stale-input fallback path.
- Updated the multi-source example generated in rev0131 so its diversity hook reflects same-root/common-mode risk rather than stronger independence.

## Still not claimed

- No live chronyd, ntpd, or NTPsec host state was captured in this cloud container.
- No NTS, symmetric-key, packet-MAC, or packet-transcript verification is performed.
- Cross-adapter agreement is not proof of independent reference roots or absence of common-mode failure.
- Named UTC realization, leap-smear discovery, and PTP comparison remain open.

## Validation summary

```text
TimeSync rev0132 validation passed.
Validated 374 semantic vectors, 6 profile maps, 6 transport adapters, and 25 evidence classes.
TimeSync multi-source adjudication self-test passed.
```
