# 705 — Negative-control fixtures and expected-failure scorecard

**Track:** Shared / Track A pilot readiness  
**Status:** Release-hardening note for v830

## Purpose

The v829 scorecard proved that the synthetic Example County happy path was internally closed. That was useful but incomplete: a verifier rehearsal should also prove that common tampering patterns fail closed.

v830 adds a negative-control layer. It deliberately mutates temporary copies of known-good synthetic packets, runs the public verifier, and records whether the verifier rejects each temporary mutation with expected stable problem codes.

## What changed

New registry:

- `artifacts/registries/negative-control-fixtures.csv`

New tool:

- `tools/example_county_negative_control_runner.py`

New generated Example County outputs:

- `artifacts/examples/example_county_2026_municipal_pilot/negative-control-report.json`
- `artifacts/examples/example_county_2026_municipal_pilot/negative-control-results.csv`
- `artifacts/examples/example_county_2026_municipal_pilot/public-negative-control-summary.md`

New release-gate check:

- `scripts/check_negative_control_fixtures.py`

The evaluator scorecard now includes an additional metric for negative-control fixture rejection while keeping the total score at 100 points.

## Fixture rule

A negative-control fixture is a synthetic expected failure. It must name:

1. a valid source packet,
2. one bounded mutation,
3. the expected verifier status,
4. the expected publishable problem code or codes,
5. a public interpretation sentence, and
6. explicit non-claims.

The runner copies the source packet to a temporary directory, applies the mutation, runs the verifier on that temporary copy, and deletes the mutated packet when the process exits. The release ZIP does not ship the tampered packet as evidence.

## Current fixture families

The v830 fixture set covers these failure classes:

- content-addressed object byte drift,
- payload-pointer digest tampering,
- payload-digest tampering,
- to-be-signed digest tampering,
- manifest digest tampering,
- missing manifest,
- unsupported envelope major version, and
- missing detached payload object.

## Public boundary

A PASS in this layer means only this:

> The synthetic verifier rejected a temporary tampered packet with the expected problem code.

It does not mean:

- live deployment evidence exists,
- an election is certified,
- an outcome is correct,
- an actor intended misconduct,
- fraud occurred, or
- a court would admit the evidence.

## Operator commands

```bash
python3 tools/example_county_negative_control_runner.py --json
python3 scripts/check_negative_control_fixtures.py
python3 tools/example_county_evaluator_scorecard.py --json
```

## Release-gate invariant

The negative-control layer is now part of the smallest useful synthetic rehearsal. If a verifier refactor makes happy-path packets pass but tampered temporary packets no longer fail as expected, the release gate must fail.
