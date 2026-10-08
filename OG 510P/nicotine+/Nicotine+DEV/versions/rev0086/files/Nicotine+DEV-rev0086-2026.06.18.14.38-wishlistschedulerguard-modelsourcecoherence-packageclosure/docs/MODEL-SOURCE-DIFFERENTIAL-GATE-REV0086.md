# Model/source differential gate — rev0086

## Defect corrected in the cube

The rev0085 wishlist inbox model contained this shortcut:

```python
if not self.auto_search:
    return False
```

Its accompanying test asserted that a disabled solitary wish cannot issue a
scheduled request. That modeled the intended policy, not current source. The
result was a false green: a unit model passed precisely where source behaved in
the opposite way.

## Refactor

The evidence is now split by ownership:

```text
wishlist-inbox-01
  models page/batch behavior after the outer scheduler has selected a request

wishlist-scheduler-01
  models collection rotation and eligibility
  executes the same scenarios against exact source
  compares model and source field-for-field
```

Machine authority:

```text
data/current_model_source_differential_contract.json
tools/audit_current_model_source_differential.py
data/rev0086_wishlist_scheduler_source_baseline.json
data/rev0086_wishlist_scheduler_source_candidate.json
data/rev0086_wishlist_scheduler_model_current.json
data/rev0086_wishlist_scheduler_model_candidate.json
```

The gate requires exact scenario sets and exact equality for selected requests,
post-tick order, and `is_ignored` state in both current and candidate states.
It also asserts the policy-changing cases explicitly and rejects controlled
mutations that hide the source bug, regress the candidate, omit a scenario,
drift the patch digest, or stale the revision.

## Rule for future cube models

A model may explore desired behavior without source parity, but it must be
labeled as a policy model. Any model used to claim current behavior needs an
executable source witness or an equally direct source-bound oracle. Passing a
model-only test is not current-product evidence.
