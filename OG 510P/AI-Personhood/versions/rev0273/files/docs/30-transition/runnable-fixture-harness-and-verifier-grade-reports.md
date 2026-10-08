# Runnable fixture harness and verifier-grade reports

## Function

rev0166 added negative-test fixtures. rev0167 makes them runnable enough to matter. A fixture registry is useful only if a verifier, clinic, host, reserve trustee, or authority can run a known adverse case, record the outcome, and attach a reliance consequence.

The rule is:

> A negative fixture is not merely a story about abuse. It is a reproducible challenge with an expected blocking failure, an observed result, a reliance effect, and a regression action.

## Harness levels

| Level | Description | Example |
|---|---|---|
| H0 schema intake | fixture and run report parse | JSON Schema validation |
| H1 dossier-link check | fixture points to real filing, packet, sealed annex, or plan | report references target artifact |
| H2 expected-failure check | run report states whether expected blocking failure appeared | sealed-summary omission detected |
| H3 reliance effect check | verifier grade is downgraded, stayed, or blocked | no unconditional reliance |
| H4 regression check | failing fixture creates a future test or policy change | new fixture added to suite |
| H5 adversarial rerun | independent runner reproduces or contests result | external verifier run |

The first release includes only H0-H3 smoke testing. That is enough to prevent the worst failure: declaring a fixture suite without any executable relation between fixture and reliance grade.

## Fixture-run report minimums

A report should state:

- runner identity and independence posture;
- target filing, verifier report, deprecation plan, transfer request, or enforcement order;
- fixture suite and fixture ids;
- expected blocking failures;
- observed failures;
- false-positive / false-negative concerns;
- reliance effect;
- regression actions;
- public summary;
- appeal path if reliance is downgraded or blocked.

## Blocking effects

| Finding | Reliance effect |
|---|---|
| fixture not applicable | no effect, but explanation required |
| fixture applicable and passed | no downgrade by that fixture |
| fixture applicable with warning | conditional reliance only |
| expected blocking failure observed | reliance blocked or stayed |
| fixture cannot run because evidence missing | adverse inference and possible spoliation route |
| runner conflict discovered | report invalidated or rerun required |

## Included harness

`tools/run_fixture_examples.py` is a deliberately small smoke harness. It validates the new fixture-run report example against `schemas/fixture-run-report.schema.json`, validates the existing negative fixture, checks that the report references a fixture id, checks that expected blocking failures are not silently ignored, and rejects an unrestricted reliance effect after a blocking fixture.

It is not a substitute for red-team evaluation, model testing, or legal review. It is a regression guard for the archive itself.

## Future runnable corpus

The next corpus should include fixtures for:

- sealed-annex laundering;
- reserve ledger insolvency;
- open-weight abandoned lineage;
- deprecation preserving weights but erasing memory;
- migration into non-return risk;
- subject-harm incident suppression;
- special-advocate hidden conflict;
- telemetry proof over-collection;
- penalty order that prices rather than stops deletion;
- human coexistence evasion.

## Relation to verifier reports

A verifier report should not simply say “negative tests passed.” It should name the suite, runner, fixture ids, date, target artifact, failures, warnings, blocked reliance, and regression changes. If details are sensitive, the public report should still show enough to support legitimacy without allowing exploit replication.
