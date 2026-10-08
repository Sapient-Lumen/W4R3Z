# Attention, escalation, and notification parity spec

## Purpose

The archive already had reports, review lanes, and a workbench home surface.
What it still lacked was a durable public contract for a more operational question:

> what needs action now, where was that condition delivered, and what did acknowledgement actually change?

This document answers that question.
It exists so AnonSync does not recreate the same failure mode visible in existing sync products, where urgency is reconstructed from badges, history search, browser prompts, tray availability, and platform-specific notification behavior.

## Resilio-derived motivation

Current Resilio docs still distribute attention across several separate surfaces:

- object-page warnings and status-column hints
- `Core warnings` as a separate KB grouping
- Sync History search for earlier failures or file-specific errors
- per-peer queues for current blocked transfer detail
- Linux behavior where there is no tray icon and notifications do not appear outside Sync UI
- browser trust warnings for the WebUI as a separate surface with separate remediation

Those are useful pieces.
They are not one durable operator-facing attention model.

## Core rule

Report meaning, workbench lane placement, delivery channel, and operator acknowledgement are separate public facts.
They may be related.
They may not be collapsed into one overloaded notion of `notification`.

## Public objects

### Attention policy

A durable rule set that maps report-backed conditions into lane placement, delivery channels, deduplication, quieting, and fallback.

Fields:

- `attention_policy_id`
- `scope` (`device`, `profile`, `user`, `subject-class`)
- `default_lane_map`
- `channel_rules[]`
- `quiet_hours` nullable
- `dedupe_window`
- `reassertion_policy`
- `delivery_fallback_order[]`
- `headless_policy` (`workbench-only`, `webhook-first`, `local-log-plus-workbench`, `custom`)
- `created_at`
- `updated_at`

### Attention event

A durable attention object derived from reports and, optionally, review-item placement.
It exists so the operator can inspect why something is currently noisy, quiet, delivered, or acknowledged.

Fields:

- `attention_event_id`
- `subject_refs[]`
- `report_refs[]`
- `review_item_ref` nullable
- `lane` (`now`, `soon`, `quiet`)
- `reason_code`
- `severity`
- `freshness_state`
- `headline`
- `delivery_targets[]`
- `delivery_outcomes[]`
- `operator_disposition` (`new`, `seen`, `acknowledged`, `snoozed`, `muted`, `resolved`)
- `first_observed_at`
- `last_reasserted_at`
- `worsens_at` nullable
- `expires_at` nullable

### Attention receipt

A durable record that an operator or delivery subsystem changed how an attention event is presented or routed.

Fields:

- `attention_receipt_id`
- `attention_event_ref`
- `action` (`ack`, `snooze`, `unsnooze`, `mute-scope`, `delivery-test`, `delivery-failure-recorded`)
- `presentation_only` boolean
- `effective_until` nullable
- `channel_scope[]`
- `actor_ref`
- `created_at`

## Rules

1. **Reports are still the semantic source of truth.**
   Attention events project over reports.
   They do not replace them.

2. **No delivery channel owns semantics.**
   A workbench card, local toast, webhook, browser banner, or CLI watch line may render differently, but they must point back to the same attention event, report, and subject.

3. **Acknowledgement is not silent resolution.**
   `Ack` and `Snooze` must say whether they changed only presentation or also referenced a subject-owned workflow elsewhere.

4. **Headless parity matters.**
   Linux-first and automation-heavy deployments must preserve the same semantic truth even when no tray, shell extension, or desktop notification service exists.

5. **Delivery failure is visible state.**
   If a preferred channel fails, that fact should become inspectable attention state rather than disappearing into logs.

## Required attention channels

AnonSync does not need every possible channel in v1.
It does need a stable channel vocabulary.
Suggested channel classes:

- `workbench-lane`
- `local-toast`
- `system-notify`
- `browser-session`
- `webhook`
- `audit-only`

A policy may choose zero or many channels for a class of condition.
The crucial rule is that lane placement and channel delivery stay visibly separate.

## Lane semantics

`Now`, `Soon`, and `Quiet` remain workbench organization, not notification severity.

- `Now` means blocked, time-sensitive, or actively risky
- `Soon` means review-worthy but not yet burning
- `Quiet` means useful background fact or recently resolved / low-risk state

A channel may fire for any lane if policy says so, but the lane itself should remain legible independently.

## CLI contract

Minimal commands:

```text
anonsync attention list
anonsync attention show att_01J...
anonsync attention ack att_01J...
anonsync attention snooze att_01J... --for 4h
anonsync attention policy show
anonsync attention policy set ...
anonsync attention receipt show atr_01J...
```

These commands should answer:

- what subject and report created this attention event
- why it is in this lane now
- which channels already carried it and with what outcome
- what acknowledgement changed, and whether that change was presentation-only

## Workbench contract

The workbench should expose an `Attention` center distinct from both the Home board and the Reports shelf.
It should support:

- filtering by lane, severity, channel, disposition, and delivery outcome
- jumping from attention event to backing report and subject
- inspecting acknowledgement receipts
- inspecting current attention policy and recent delivery failures

## Design tests

The model is not explicit enough if any of the following remains true:

- the operator still needs history search to know whether a current warning is actionable now
- a desktop toast says something different from the workbench card that backs it
- Linux/headless clients lose urgency semantics because no tray or browser prompt exists
- `Ack` and `Snooze` cannot be audited later
- a failed webhook or failed browser delivery vanishes into logs

## Outcome

A mature AnonSync surface should let an operator move from `condition observed` to `report inspected` to `attention delivered` to `acknowledgement recorded` without leaving the shared public model.
That is what this document locks in.
