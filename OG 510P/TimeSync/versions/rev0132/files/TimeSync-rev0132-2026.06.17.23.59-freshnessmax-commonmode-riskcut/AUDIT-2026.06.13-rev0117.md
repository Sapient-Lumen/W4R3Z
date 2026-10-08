# TimeSync rev0117 audit — lifecycle/current-use mutation pressure

## Scope

This audit continued FT-0090 from rev0116 and intentionally avoided a registry/doctrine expansion. The focus was executable mutation pressure against lifecycle/current-use/freshness-adjacent semantics that can remain schema-shaped while changing operational meaning.

## Findings closed

1. **Profile lifecycle actionability survivor.** A passing actionable local assessment could have `profile_lifecycle_state` changed from `active` to `revoked` or `superseded` and still pass. rev0117 now rejects actionable or conditional current actionability unless the profile lifecycle remains current.
2. **Lifecycle-authority no-compromise effect survivor.** A `none_known` compromise response could assert `historical_only` or `contested_visibility` as its replay effect. rev0117 requires `no_current_effect` when no compromise is known.
3. **Aggregate lifecycle decision-table row drift.** Required row ids such as `active-current` could retain the same id while their semantic posture changed. rev0117 pins required row ids to canonical lifecycle states, allowed effects, allowed decisions, and key posture requirements.
4. **Retained-record current-use promotion.** A `retained_operator_record` digest surface could be promoted to current use by flipping `current_use_allowed`. rev0117 keeps that surface retention-only.

## Refactor performed

Aggregate lifecycle decision-table semantics moved into `tools/aggregate_lifecycle_decision_semantics.py`. This removes the table-row and `expected_lifecycle_decision` concern from the monolithic validator while making row-shape drift executable and self-tested.

## New executable coverage

- Semantic vectors: `TV-N324` through `TV-N327`.
- Fixture derivations: `DF-0117-001` through `DF-0117-004`.
- Mutation probes: `MP-0117-001` through `MP-0117-004`.

## Remaining accepted survivors

The broad scan still shows downgrade-style mutations that appear intentional: current replay visibility can be downgraded to historical-only, current-use digest surface rules can be made stricter by setting `current_use_allowed` false, and historical-only recovery artifacts can remain valid when their current-ness is reduced. Those are not treated as bugs unless they still claim current actionability or current replay visibility.
