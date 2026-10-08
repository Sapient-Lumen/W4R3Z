# 53 — Current terminology glossary

rev0086 separates several meanings of “current” that were easy to conflate in aggregate lifecycle work.

## `current_time_claim`

A timing claim is fresh enough to be considered in the local assessment. This is about the time interval, freshness, timescale, regime, source posture, and applicability.

It is not the same as profile conformance or aggregate correction-authority lifecycle.

## `current_profile_conformance`

A local assessed state satisfies the active profile at the assessment boundary. This depends on profile rules and evidence obligations.

Aggregate lifecycle summaries cannot satisfy profile obligations.

## `current_actionability`

A profile-assessed state may be used for the profile's action class at a particular time. This can be withdrawn by validity horizon, lifecycle policy, stale assessment policy, or local profile rules.

Aggregate rollups cannot create actionability.

## `current_replay_visibility`

A detached replay-transparency receipt can be interpreted as current at evaluation time. This is replay metadata and is not TimeState provenance.

## `current_aggregate_interpretation`

An aggregate verifier audit summary, correction lineage, or correction-authority lifecycle reference can support current aggregate interpretation.

In rev0086 this is governed by `current_interpretation_decision` and the aggregate lifecycle decision table.

## `current_authority_binding`

A correction-authority reference reports authorized, non-revoked, non-withdrawn, non-contested posture checked before the aggregate artifact was created.

This is not an authority registry and does not expose authority rosters or keys.

## `historical_only`

A record may remain useful for retained audit interpretation while not supporting current reliance. Historical-only is not failure by itself. It is a non-current interpretation.

## `suppressed_*`

Suppressed decisions mean the record must not support current aggregate interpretation for the named reason: emergency withdrawal, revocation, contestation, unknown lifecycle, notification staleness, or portability failure.

Suppression does not delete the record and does not rewrite prior publications. It constrains how the record may be interpreted now.
