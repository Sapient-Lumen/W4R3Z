# rev0311 post-readout public/closure firebreak refactor

## Problem

The field rail already blocks post-readout dispatches from widening owner-action,
next-evidence-ask, or public-language classes. The remaining risk was in release
examples: a packaged post-readout action or lifecycle row could still drift
toward `closure_permitted=true` or stronger public-language wording while the
followthrough was live.

## Change

Two existing validators now enforce the same boundary outside scratch:

- `tools/check_post_readout_actions.py` blocks live `FT-0181` closure-permitted
  post-readout examples and requires lane-bound public-language text.
- `tools/check_service_lifecycle_decisions.py` blocks lifecycle rows whose
  post-readout action text promotes or widens public claims.

Both validators include in-memory synthetic regressions, so the failure mode is
checked without adding fixture files or new registry surface.

## Boundary

This refactor does not create a public-language action, lifecycle decision,
service-record edit, evidence acceptance, custody record, closeout, or closure.
It only prevents packaged examples from describing those outcomes before the
real owner-evidence chain supports them.
