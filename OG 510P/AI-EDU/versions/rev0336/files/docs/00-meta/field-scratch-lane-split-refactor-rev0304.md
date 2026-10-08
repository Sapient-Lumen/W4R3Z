# rev0304 field scratch lane split refactor

## Audit target

The audit target was the live cloudtainer scratch layout after the rev0303
firebreak. Rev0303 made the router ignore checker scratch. Rev0304 asks whether the
working directory itself can make the right thing the default.

## Finding

The previous default scan root was still `scratch/`. That meant the router had to
be defensive against every local artifact class in one shared tree. The firebreak
worked, but it left a waste pattern intact: operators and checkers both wrote under
the same top-level space, so every future helper had to remember the separation.

The riskiest incomplete work is not late-stage closure. The riskiest incomplete
work is dropping the first real owner action because the maintainer sees a large,
ambiguous scratch tree and begins explaining it instead of using the field rail.

## Refactor performed

The default field scan/output lane is now:

```text
scratch/field/ft0181/
```

The checker lane is now:

```text
scratch/checks/
```

Concrete changes:

- `tools/decide_ft0181_field_next_action.py` defaults `--scratch-root` and
  `--output-dir` to `scratch/field/ft0181/...`.
- Router-emitted field commands now write owner packets, send/session logs,
  contact statuses, route blocks, live-window artifacts, post-readout artifacts,
  and context receipts under the field lane.
- Tool defaults for the FT-0181 owner rail now point at the field lane when no
  explicit `OUT` is supplied.
- Checker fixtures now use `scratch/checks/check-*` paths, and the field-router
  regression still proves that checker scratch and provenance-linked helper
  artifacts do not alter a clean route.

## What this avoids

This avoids three kinds of waste:

1. **False position**: a synthetic helper artifact cannot make the maintainer feel
   the project is later in the field rail than it really is.
2. **Narrative churn**: the next turn is less likely to become another audit about
   why scratch looks confusing.
3. **Operator friction**: a clean `make owner-field-work` now creates and follows
   the live lane without requiring a custom `SCRATCH=` convention.

## Compatibility boundary

Legacy scratch can still be inspected deliberately with `SCRATCH=...`. That is an
explicit override. The default path is now the live field lane.

Release zips still exclude all of `scratch/`. The change is for cloudtainer session
correctness, not packaged evidence.

## Remaining risk

The field lane can still contain stale real field scratch if an operator reuses it
after abandoned experiments. The router ranks artifacts by manifest clocks before
file modification time, but the operator still owns the decision to start fresh,
preserve, or intentionally point `SCRATCH=` at a legacy lane.

The next high-value correction would be an optional lane-cleanliness report that
summarizes live field artifacts without creating any new evidence or closure state.
That should wait unless stale field scratch actually blocks a real owner action.
