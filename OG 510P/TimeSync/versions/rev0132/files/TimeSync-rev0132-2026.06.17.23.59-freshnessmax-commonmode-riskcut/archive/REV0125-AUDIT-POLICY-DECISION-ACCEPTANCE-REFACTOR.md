# rev0125 audit/refactor note — policy-decision acceptance

The refactor removes duplicated chrony/P1 policy thresholds from evaluator code and places them in a single machine-readable artifact. The new helper validates lane ordering, monotonic weakening, inclusive thresholds, fail-closed stratum/leap requirements, and the diagnostic-only unsatisfied row.

The acceptance runner targets the operationally risky edges:

- exactly 300 seconds versus 300.000000001 seconds;
- exactly 3600 seconds versus 3600.000000001 seconds;
- exactly 86400 seconds versus 86400.000000001 seconds;
- unknown source posture under otherwise fresh input.

This is intentionally a narrow executable acceptance layer, not a conversion of the entire narrative acceptance corpus into BDD machinery.
