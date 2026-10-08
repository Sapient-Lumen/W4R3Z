# TimeSync rev0098 audit — aggregate artifact-time and derivation drift

## Finding 1 — aggregate publication and artifact-check times were not tied together

rev0097 checked many nested aggregate lifecycle, authorization, and notification timestamps against `aggregate_record_created_at`, but the top-level relationship between `issued_at` and `aggregate_record_created_at` was still implicit. That left an aggregate audit summary able to claim a publication time later than the artifact/check time that is supposed to bound compact aggregate interpretation.

rev0098 adds `tools/aggregate_temporal.py` and rejects aggregate verifier audit summaries where:

```text
issued_at > aggregate_record_created_at
```

This is deliberately narrow. It does not turn aggregate publication metadata into TimeState freshness, profile evidence, current actionability, a verifier identity surface, or an authority registry.

## Finding 2 — aggregate period ordering was still inline inside the validator

The aggregate period start/end check was still hand-coded inside `tools/validate_archive.py`. rev0098 moves that interval check into the new aggregate temporal helper. This is a small refactor, but it is the correct kind: an executable concern leaves the monolith and gains a focused self-test.

## Finding 3 — fixture derivation needed its own uniqueness checks

Patch-derived fixture validation reduced copy drift, but the derivation manifest itself did not reject duplicate derivation IDs or two derivations targeting the same rendered output. rev0098 adds those checks to `tools/fixture_derivations.py`, so fixture-family conversion is less likely to create hidden ambiguity.

## New negative fixture

```text
examples/negative/aggregate-issued-after-created-invalid.json
```

The fixture is derivation-checked from `examples/discovery-request-with-replay-transparency.json` in `tests/fixture-derivations.yaml`.

## Remaining risk

FT-0090 should stay open. The highest remaining value is continued extraction of compact concern families from `tools/validate_archive.py` and conversion of copied negative families into derivation-checked fixtures where that prevents actual drift. Avoid new registries unless a validation rule needs them.
