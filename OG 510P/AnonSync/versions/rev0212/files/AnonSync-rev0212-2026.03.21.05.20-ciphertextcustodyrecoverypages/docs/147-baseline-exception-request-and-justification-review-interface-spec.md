# Baseline exception request and justification review interface spec

## Purpose

`rev0120` made the archive explicit about two things that are easy to blur in real systems:

- which standing change is the intended **baseline**
- which targets later **match**, **drift**, or remain **unobserved** relative to that baseline

That resolves one dangerous seam.
It immediately exposes the next one:

- what if a target is supposed to differ from baseline on purpose?
- how do we distinguish a sanctioned durable exception from accidental drift?
- what future inheritance is blocked because this target stays different?
- how long is that difference allowed to remain?
- what should cause it to end?

This document defines the interface contract for turning sanctioned durable difference into a reviewed **baseline exception request** instead of leaving it as a remembered manual override.

## Core rule

Any durable difference that is intentionally preserved against an approved standing baseline must be represented as an explicit **baseline exception request**.

The product must not let `special case`, `leave this one alone`, `that host is different`, or `we set that manually earlier` stand in for a first-class exception object.

## Why this needs its own spec

Current official Resilio docs sharpen this need in a useful way.

They currently document:

- linked-device modes and default folder locations that can make one member receive future folders differently from another
- custom placement workflows that depend on switching the receiving side into `Disconnected` before connecting the folder to a chosen path
- `Folder Preferences` that are per-folder and desktop-only
- `folder_defaults.transfer_priority` that affects shares whose priority was not altered manually in folder preferences
- host-level defaults like `share_file_ttl`
- configuration mode explicitly described as a way to apply the same settings on a number of different machines while overriding folders previously added from WebUI and disabling WebUI for that setup

None of those capabilities are fake.
Some of them are exactly what serious operators need.
The problem is that a later observer can still be left to infer:

- whether the difference is legitimate or accidental
- what baseline the target is excepted from
- whether the difference applies only now or to future arrivals too
- what event should end the exception
- whether the operator is preserving one target safely or quietly normalizing a wider fork

AnonSync should therefore insist on one more first-class answer surface:

- a **baseline exception request and justification review** for `why this target is allowed to differ, what inheritance it blocks, what local difference it preserves, and how the exception is supposed to end`

## Public objects

### Baseline exception request

The durable object describing one sanctioned durable deviation from one approved baseline.

Suggested fields:

- `baseline_exception_request_id`
- `baseline_ref`
- `target_ref`
- `target_kind` (`member`, `host`, `subject`, `member-subject-cell`, `template-slice`, `future-arrival-class`)
- `requested_difference_summary`
- `request_state` (`draft`, `reviewed`, `approved`, `rejected`, `expired`, `superseded`)
- `strongest_reason`
- `duration_posture` (`temporary-but-durable`, `until-platform-change`, `until-capacity-change`, `until-manual-close`, `indefinite-with-review`)
- `rejoin_plan_summary`
- `inheritance_consequence_summary`

### Baseline exception reason row

One explicit reason why baseline should not hold on this target.

Suggested fields:

- `baseline_exception_reason_row_id`
- `reason_kind` (`platform-limitation`, `storage-constraint`, `network-segmentation`, `custody-requirement`, `regulatory-scope`, `manual-preservation`, `migration-phase`, `operator-safety`, `performance-isolation`)
- `reason_summary`
- `evidence_ref`
- `confidence`
- `still-expected-to-hold` bool

### Blocked inheritance row

One future effect that baseline would normally impose but this exception intentionally blocks.

Suggested fields:

- `blocked_inheritance_row_id`
- `inheritance_kind` (`future-arrival-path`, `future-materialization-mode`, `future-download-priority`, `future-transport-default`, `future-publication-rule`, `future-share-default`, `future-ttl-default`)
- `baseline_behavior_summary`
- `excepted_behavior_summary`
- `touches_existing_objects` bool
- `touches_future_objects` bool

### Rejoin trigger row

One event that should cause the target to rejoin baseline or at least re-open review.

Suggested fields:

- `rejoin_trigger_row_id`
- `trigger_kind` (`deadline`, `platform-upgrade`, `capacity-restored`, `network-restored`, `migration-complete`, `manual-close`, `next-rollout`, `next-observation-window`)
- `trigger_summary`
- `expected_effect`

### Exception collateral row

One risk created by preserving the exception.

Suggested fields:

- `exception_collateral_row_id`
- `risk_kind` (`future-divergence`, `operator-confusion`, `shadowed-baseline`, `publication-asymmetry`, `support-burden`, `path-fragmentation`, `policy-proliferation`)
- `risk_summary`
- `mitigation_summary`
- `review_importance`

## Fixed inspection order

Every baseline-exception request surface should preserve this order:

1. **What baseline currently applies**
2. **What exact target is asking to differ**
3. **Why that difference is justified**
4. **What future inheritance is blocked or preserved**
5. **How long the exception is expected to remain valid**
6. **What event should cause renewal, promotion, or rejoin**

### 1) What baseline currently applies

The top of the surface should restate the standing baseline plainly.
Examples:

- `member M would normally receive future subjects with selective arrival under baseline B`
- `host H would normally inherit default download priority Older first`
- `subject class S would normally publish to cohort C under publication template P`

### 2) What exact target is asking to differ

The target should be explicit and narrow.
Examples:

- `member M only`
- `host H only`
- `member M for subject class Finance`
- `future arrivals for mobile devices in cohort Field`

### 3) Why that difference is justified

The interface should force typed reasons plus evidence.
Examples:

- `mobile platform cannot support this folder-level control`
- `local storage budget is temporarily insufficient`
- `network zone requires predefined-host posture`
- `migration is preserving current path until cutover completes`

### 4) What future inheritance is blocked or preserved

This is the most important semantic section.
The operator should see statements like:

- `future arrivals for this member will not inherit default path /srv/anonsync; they will remain manually placed at /mnt/field-cache`
- `this share will not inherit baseline download priority until exception closes`
- `this host remains excluded from host default TTL and will preserve prior issuance window`

### 5) How long the exception is expected to remain valid

The product should not allow a blank `special case forever` posture.
It must show one of:

- `review again on date`
- `valid until platform capability changes`
- `valid until migration completion receipt`
- `indefinite but must justify every review window`

### 6) What event should cause renewal, promotion, or rejoin

The closing section should make the future action path explicit:

- `renew exception`
- `promote pattern into baseline rollout`
- `attempt rejoin to baseline`
- `collect stronger evidence first`

## Public rules

### Rule 1 — drift and exception are different objects

A known intentional difference must not wait to be rediscovered later as `matches-with-exception` in a drift audit.
It should already exist as a named exception request or approval.

### Rule 2 — every exception must name the blocked inheritance

It is not enough to say `this target differs`.
The surface must say what future behavior baseline would normally impose and what is being blocked.

### Rule 3 — every exception must have an ending model

An exception may be long-lived, but it still needs a renewal posture or rejoin trigger.

### Rule 4 — exception scope must stay narrower than baseline by default

The interface should bias toward the smallest target that answers the need.
If the proposal is broad, it should ask whether this is really a baseline change instead.

### Rule 5 — repeated exceptions should challenge the baseline

If the same reason is appearing across many targets, the product should suggest that the operator open a baseline rollout draft instead of preserving many separate exceptions.

### Rule 6 — exception review must show what others will infer later

The approval surface should explain how this target will appear in later drift audits and provenance traces so the operator understands the long tail of preserving the difference.

## Dense row contract

A dense exception row should preserve these labels in this order:

- `Target`
- `Baseline`
- `Requested difference`
- `Blocked inheritance`
- `Reason`
- `Review again`
- `State`

## Example prompts

- `Why is this target allowed to differ from baseline?`
- `What future behavior is this exception blocking?`
- `Is this a one-off exception or evidence that baseline is wrong?`
- `How long is this special case supposed to live?`
- `What will cause this target to rejoin baseline?`

## Anti-goals

- do not let sanctioned durable difference hide as `manual override present`
- do not make the operator infer exception legitimacy from scattered settings pages
- do not allow an exception with no blocked-inheritance explanation
- do not treat many repeated exceptions as normal without challenging the baseline
