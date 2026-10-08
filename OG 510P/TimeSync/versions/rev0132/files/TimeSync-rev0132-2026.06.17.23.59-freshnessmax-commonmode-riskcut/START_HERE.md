# TimeSync rev0132 — start here

TimeSync is a narrow-waist time-use admission model. The core object remains a six-field TimeState: interval, timescale, freshness, regime, source posture, and applicability.

rev0132 is a current-use adjudication hardening cut. Individual adapters can produce local assessed states, and the multi-source adjudicator decides how a consumer should treat multiple such states together:

- overlapping intervals are intersected;
- the weakest P1 lane is carried forward;
- combined freshness is aged from the stalest admitted input, not the freshest;
- same-root/common-mode diversity summaries from inputs are carried forward and cannot be upgraded by overlap;
- disjoint, mismatched, or unsafely combined inputs fail closed with a union interval;
- no authentication, UTC traceability, or source independence is promoted from mere adapter agreement.

Read `tools/multisource_adjudicator.py`, then `tests/multisource-adjudication.yaml`, then `examples/evaluator/multisource-p1-stale-freshnessmax-commonmode-fallback.json`.
