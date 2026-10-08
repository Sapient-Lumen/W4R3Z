# Override lease and temporary-exception spec

## Purpose

The archive already has route leases, runtime activity overrides, temporary diagnostic-depth changes, reviewed access exposure, and effective-state reads.
What it still lacked was one public contract for a more operational question:

> when the operator makes a temporary exception, what exactly changed, what durable baseline did it sit on top of, how does it end, and what proof remains later that the exception really was temporary?

This document answers that question.
It exists so AnonSync does not recreate a common sync-product failure mode where short-lived operator intent is implemented as a pile of durable settings edits, ad hoc support ritual, or sticky “remember to set it back later” folklore.

## Resilio-derived motivation

Current Resilio docs still solve several temporary operator needs through scattered setting edits or support ritual instead of one explicit lease model:

- forcing LAN-only behavior can require disabling relay/tracker via config, clearing cached public endpoint state by setting peer-expiration to `0`, restarting, and then restoring the previous value
- scheduler and bandwidth behavior live partly in Preferences, while LAN rate limiting needs a separate `rate_limit_local_peers` power-user setting
- speed-tuning guidance separately pushes predefined hosts, port-forwarding/UPnP, and optional `lan_encrypt_data` changes when the operator wants temporary throughput wins
- diagnostic-depth guidance still uses advanced toggles, tray gestures, or `debug.txt` in the storage folder, plus a later reminder to stop collecting logs

Those are real operator needs.
They are not one trustworthy temporary-exception contract.

## Core rule

A temporary exception is a first-class lease.
It may affect route posture, runtime phases, diagnostics depth, access exposure, transfer caps, or another domain-specific control surface.
It must still answer the same five questions:

- what subject it targets
- what baseline it modifies without rewriting
- what effect is active now
- what ends it (expiry, exhaustion, cancel, or reviewed handoff)
- what receipt proves creation, renewal, expiry, exhaustion, or cancellation later

If the operator cannot answer those five questions from one surface, the exception model is still too implicit.

## Public objects

### Override lease

A first-class temporary exception that sits on top of durable policy without silently becoming the new baseline.

Fields:

- `override_id`
- `family` (`activity`, `route`, `diagnostic-depth`, `access-exposure`, `transfer-budget`, `fidelity-exception`, `implementation-test`)
- `target_type` (`system`, `device`, `share`, `mount`, `peer`, `policy`, `incident`, `endpoint`)
- `target_id` nullable
- `mode` (`pause-transfer`, `drain-egress`, `suspend-ingress`, `throttle`, `maintenance`, `allow-direct-route`, `raise-diagnostic-depth`, `temporary-listener`, `temporary-fidelity-downgrade`)
- `requested_effects[]`
- `effective_effects[]`
- `baseline_refs[]`
- `domain_refs[]`
- `reason`
- `provenance_kind` (`operator`, `plan-apply`, `incident-response`, `workflow-helper`, `auto-safety`)
- `risk_tier` (`low`, `reviewed`, `high-consequence`)
- `created_by`
- `created_at`
- `starts_at`
- `expires_at` nullable
- `exhaustion_mode` (`time`, `byte-cap`, `first-success`, `manual-only`, `plan-handoff`)
- `exhaustion_budget` nullable
- `status` (`pending`, `active`, `expiring-soon`, `exhausted`, `expired`, `canceled`, `superseded`)
- `renewable`
- `cancelable`
- `no_expiry_ack_ref` nullable
- `revert_behavior` (`restore-baseline`, `restore-next-schedule-window`, `hold-for-review`)
- `effective_state_ref`
- `receipt_refs[]`

### Override receipt

A durable record proving that a temporary exception was created, renewed, reviewed, exhausted, expired, canceled, or explicitly converted into a durable policy mutation.

Fields:

- `override_receipt_id`
- `override_ref`
- `action` (`create`, `review`, `renew`, `ack-no-expiry`, `exhaust`, `expire`, `cancel`, `convert-to-durable-policy`)
- `before_summary`
- `after_summary`
- `actor_ref`
- `created_at`

### Lease conflict report

A report-shaped explanation for overlapping or mutually surprising temporary exceptions.
This exists so the operator can tell whether two leases stack safely, partially mask one another, or leave an unsafe gap at expiry.

Fields:

- `lease_conflict_report_id`
- `override_refs[]`
- `subject_ref`
- `current_effect_summary`
- `conflict_kind` (`scope-overlap`, `masking-baseline`, `expiry-race`, `budget-race`, `cross-domain-surprise`)
- `recommended_resolution`
- `created_at`

## Rules

1. **Specialized temporary controls still share one lifecycle.**  
   Route leases, diagnostic-depth raises, maintenance drains, temporary access exposure, and similar exceptions may keep domain-specific fields, but they should all render through one lease grammar.

2. **Baseline and effective state must be shown together.**  
   The operator should not have to infer what will resume when the lease ends.

3. **Temporary by default means temporary by proof.**  
   Every lease should normally expire automatically or exhaust against an explicit budget. `No expiry` requires an explicit acknowledgement receipt.

4. **Expiry and exhaustion are events, not silence.**  
   When a lease ends, the system should emit a receipt and, when appropriate, an attention event explaining what changed.

5. **Renewal is distinct from recreation.**  
   A renewed lease should preserve history and reason continuity instead of disappearing into “latest state only” folklore.

6. **Conflicting leases must be explainable.**  
   If two temporary exceptions overlap, the effective-state view should name the combined outcome and warn when expiry order matters.

7. **Converting a temporary exception into durable policy must be explicit.**  
   A convenience action like “keep this setting” should create a policy mutation receipt, not silently mutate baseline state behind the original lease.

## CLI contract

Minimal commands:

```text
anonsync override list
anonsync override show ov_01J...
anonsync override explain ov_01J...
anonsync override create --target share:media --mode throttle --down 4MiB/s --up 1MiB/s --ttl 6h --reason "hotel uplink"
anonsync override renew ov_01J... --ttl 2h
anonsync override cancel ov_01J...
anonsync override receipt show ovr_01J...
```

These commands should answer:

- what durable baseline the lease is modifying
- what effect is active now versus only requested originally
- when the lease will expire or what budget will exhaust it
- whether other active leases on the same subject are interacting
- which receipt proves the lease was created, renewed, expired, or canceled

## Workbench contract

The workbench should expose an `Exceptions` page distinct from `Policies`, `Attention`, and per-subject detail pages.
Its job is not to add another settings area.
Its job is to answer:

- what temporary exceptions exist right now
- which ones are route, runtime, diagnostic, access, or other family types
- what baseline they are masking or widening
- which ones are nearing expiry, already exhausted, or carrying `no-expiry` acknowledgement
- which ones overlap in surprising ways

The page should support:

- filtering by family, target, expiry horizon, and risk tier
- opening one consistent lease drawer that shows baseline, active effect, end condition, and receipts
- jumping from a subject page to all active leases affecting that subject
- one-click cancellation or renewal where policy allows it
- surfacing lease-conflict reports without forcing the operator to compare multiple pages manually

## Report-language integration

The shared report language should support at least these families here:

- `override-effect` — what the temporary exception changes relative to baseline
- `override-conflict` — why overlapping leases do or do not compose safely
- `override-expiry-risk` — what meaningful behavior will change soon when the lease ends

These reports should behave like any other report-backed finding: severity, freshness, scope, and safest next action stay explicit.

## Design tests

The model is not explicit enough if any of the following remains true:

- a temporary route, diagnostic, or activity change still looks like an unexplained durable setting change
- the operator cannot tell what baseline will resume after expiry
- `renew` effectively destroys the original lease history instead of extending it
- a `no expiry` exception can exist without an explicit acknowledgement record
- overlapping temporary exceptions still require folklore to explain which one wins

## Outcome

A mature AnonSync surface should let the operator move from `I need a temporary exception` to `create reviewed lease` to `inspect baseline/effective state` to `see it expire, exhaust, or convert with receipts` without leaving the public model or re-learning one domain-specific ritual per feature.
That is what this document locks in.
