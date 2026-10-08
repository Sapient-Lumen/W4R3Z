# Differential privacy for election-adjacent data releases (careful, limited use)

**Track:** A (Deployable core)


Differential privacy (DP) is often proposed as a way to release data while limiting individual leakage.
For elections, DP is generally **not appropriate** for certified official tallies, but it can be useful for
optional datasets (research releases, certain analytics) *if* claims are evaluated and communicated properly.

## Where DP can help

- releasing microdata or detailed aggregates for research (after certification)
- turnout analytics where small-cell privacy matters
- protecting poll-worker or administrative datasets

## Where DP does not fit

- official certified totals and winner determination
- legal recount/audit evidence where exactness is required

## Requirements

- Any DP release MUST include a signed DP configuration summary:
  epsilon/delta, sensitivity assumptions, composition rationale, evaluation method
- DP claims SHOULD be evaluated against published guidance (see NIST)

## References

- NIST: Guidelines for evaluating differential privacy guarantees (finalized 2025)