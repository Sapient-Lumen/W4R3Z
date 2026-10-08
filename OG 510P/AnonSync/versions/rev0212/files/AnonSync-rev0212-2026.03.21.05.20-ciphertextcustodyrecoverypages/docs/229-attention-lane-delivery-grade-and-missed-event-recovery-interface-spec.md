# Attention lane, delivery grade, and missed-event recovery interface spec

## Purpose

The archive already had a home/now/soon/quiet rhythm and basic attention objects.
What it still lacked was one stricter contract for the operator question that appears whenever a product claims it `notified` someone:

> did this event actually reach me on this seat, on this surface, under this power/background posture, and what proves recovery if it did not?

Current Resilio docs make this seam concrete.
Desktop preferences still expose notifications as a toggle, the main desktop UI still uses a bell for approvals and other events, Linux still has no tray icon and no notifications outside Sync UI, and Android settings still warn that disabling notifications lowers Sync's priority and may cause it to stop working in the background.

Those are not just cosmetic differences.
They mean `notification` still does not describe one honest delivery contract.

## Core decision

AnonSync must treat attention as a first-class lane with an explicit **delivery grade**.
Every high-signal event should declare:

- whether it is merely visible in the current surface
- whether it is expected to reach the system shell / OS notification channel
- whether it requires active polling
- whether seat power/background posture may suppress it
- what missed-event recovery path is guaranteed

The product should never imply `you were notified` when the honest statement is `the event was visible only if you happened to have this surface open`.

## Why this matters

Current Resilio behavior still leaves four truths scattered across different pages:

- desktop alerts are a preference toggle
- desktop attention also depends on a bell icon inside the app
- Linux lacks out-of-app notification integration entirely
- Android can degrade background participation when notifications are disabled

AnonSync should instead hold one stronger rule:

> every important event carries an explicit delivery grade and a recovery guarantee.

## Fixed review order

Every high-signal attention event should render the same sections in the same order:

1. **Event class**
2. **Delivery grade**
3. **Suppression factors**
4. **Recovery path**
5. **Acknowledgement receipt**

### 1) Event class

Show:

- event kind (`approval-request`, `blocked-mutation`, `repair-needed`, `entitlement-change`, `upgrade-available`, `other`)
- severity (`info`, `review`, `warning`, `blocking`)
- response deadline, if any
- whether the event is local-only or multi-seat visible

### 2) Delivery grade

Show one explicit grade:

- `surface-only`
- `in-app-attention`
- `system-channel`
- `push-or-system-channel`
- `poll-required`
- `delivery-not-guaranteed-on-this-seat`

Also show the attempted channels and their observed status.

### 3) Suppression factors

Show anything that may explain non-delivery:

- notifications disabled
- seat suspended / asleep / background-throttled
- shell integration unavailable
- headless/local-web seat with no OS channel
- access surface not currently open
- delivery unknown

### 4) Recovery path

Show:

- inbox or review queue location
- event retention window
- whether another seat can acknowledge or approve
- whether the event will re-announce on next active session
- escalation options if deadline-sensitive

The operator must be able to answer:

> if I missed it live, where does it still exist and how do I prove I handled it?

### 5) Acknowledgement receipt

The receipt must preserve:

- event id
- delivery grade shown at the time
- suppression findings
- acknowledgement actor and seat
- whether acknowledgement completed the underlying workflow or only silenced the alert

## Main surface

Every seat should have one **Attention** page with fixed sections:

- `Needs action now`
- `Waiting / recoverable`
- `Seen elsewhere`
- `Delivery degraded on this seat`
- `Quiet / archived`

A badge or bell is allowed as a shortcut.
It must never be the only truthful home of the event.

## Object model implications

### Attention event

Fields:

- `attention_event_id`
- `event_kind`
- `severity`
- `subject_ref` nullable
- `seat_scope`
- `created_at`
- `deadline_at` nullable

### Delivery assessment

Fields:

- `delivery_assessment_id`
- `attention_event_ref`
- `seat_ref`
- `surface_ref`
- `delivery_grade`
- `attempted_channels[]`
- `suppression_factors[]`
- `recovery_path_ref`
- `assessed_at`

### Attention receipt

Fields:

- `attention_receipt_id`
- `attention_event_ref`
- `delivery_assessment_ref`
- `acknowledged_by`
- `acknowledged_from_seat_ref`
- `acknowledgement_kind` (`seen`, `triaged`, `completed`, `muted`)
- `recorded_at`

## Explicit non-goals

AnonSync should not:

- equate `event exists` with `user was notified`
- let a bell icon be the only durable recovery path
- hide seat-specific non-delivery behind generic notification wording
- require operators to infer whether another seat can safely handle the event

## Relationship to nearby specs

This spec is the attention-specific companion to:

- `154-home-now-soon-quiet-and-review-rhythm-interface-spec.md`
- `159-local-web-first-bringup-auth-and-empty-state-interface-spec.md`
- `192-pause-scheduler-and-destructive-signal-separation-interface-spec.md`
- `208-suspended-seat-resume-quarantine-and-offline-precedence-interface-spec.md`

Those documents already define review rhythm and seat posture.
This one fixes the delivery truth of attention itself.
