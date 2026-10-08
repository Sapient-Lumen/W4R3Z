# Chrony P1 policy decision hardening — rev0125

rev0125 addresses the next risk after independent observation recomputation: profile-decision drift. In rev0124 the primary adapter and independent evaluator both knew the P1 thresholds through duplicated Python literals. That made the tests useful for recomputation but still left the policy lane table hidden inside code.

## What moved

`evaluator/p1-chrony-policy.json` is now the single machine-readable policy artifact for the chrony/P1 lane table:

- satisfied security-sensitive use: max 100 ms bound and max 300 s replay age;
- coarse logging fallback: max 1000 ms bound and max 3600 s replay age;
- display-only fallback: max 5000 ms bound and max 86400 s replay age;
- diagnostic-only rejection when leap/stratum fail, source posture is unknown, or all lane thresholds are exceeded.

The artifact also records the conservative clock-error formula and unsupported conditions. The evaluator still computes the observation-specific bound; the policy artifact only decides what that bound and age may be used for.

## Boundary rule

Lane thresholds are inclusive. Exactly 300 s remains security-sensitive if the bound is small enough. One nanosecond after 300 s drops to coarse logging. Exactly 3600 s remains coarse logging. One nanosecond after 3600 s drops to display-only. Exactly 86400 s remains display-only. One nanosecond after 86400 s becomes diagnostic-only.

This is not a new TimeState field. It is executable policy around the existing six-field output.

## Refactor shape

`tools/chrony_policy.py` validates the policy artifact and applies the lane table. It does not parse chrony, compute root-distance bounds, or emit TimeState. Those responsibilities stay in:

- `tools/chrony_adapter.py` for chronyc text/capture replay and primary evaluation;
- `tools/chrony_observation_eval.py` for independent typed-observation recomputation.

The independent evaluator still does not import `chrony_adapter.py`. rev0125 intentionally centralizes the threshold table while preserving the separate observation recomputation path.

## Executable acceptance

`tools/profile_decision_acceptance.py` runs `tests/profile-decision-acceptance.yaml` through both evaluator paths. The cases cover exact and one-nanosecond-after transitions for security, logging, display, and diagnostic-only decisions.

This does not make the older 124 prose acceptance scenarios executable. It creates a smaller executable acceptance layer exactly where a hidden threshold error would create a false authorization.

## Remaining risk

The live path still needs a host with chronyd/chronyc. This cloud container cannot prove live capture. NTS authentication, named UTC realization, leap-smear discovery, PTP comparison, and non-chrony RFC 9249 operational-state ingestion remain out of scope for rev0125.
