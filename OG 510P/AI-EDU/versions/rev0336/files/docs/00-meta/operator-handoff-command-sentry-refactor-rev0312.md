# rev0312 operator handoff command sentry refactor

## Problem

The cube had strong late-stage guards but a weak re-entry contract: the official
operator handoff could still pass with stale command syntax. In rev0311 it listed
`run_lint_suite.py --mode ...` even though the runner accepts `--lane`. That is
not merely cosmetic; it breaks the path back into field work and burns the
operator's attention on avoidable command repair.

## Change

The handoff validator now requires:

- `python3 tools/run_lint_suite.py --lane owner-reply-field`
- `python3 tools/run_lint_suite.py --lane fast-changed`
- `python3 tools/run_lint_suite.py --lane release-controls`
- `python3 tools/run_lint_suite.py --lane full-release`
- a `make handoff-release ...` packaging command
- the router/report-first allowed actions: `make owner-field-work`, `make
  owner-field-report`, and `make owner-field-next CSV=/path/to/real-owner-return.csv`

The same validator rejects direct downstream actions in the handoff allowed list
when they bypass the field router/report contract.

## Effect

A future release cannot advertise obsolete runner modes or tell the maintainer to
jump straight into intake, activation, readout, import, or closeout actions. The
next step remains one bounded field-router command, not a registry or doctrine
round.

## Non-effect

The guard is not owner evidence, not SRC2+, not custody, not public-summary
support, not lifecycle authority, and not closure.
