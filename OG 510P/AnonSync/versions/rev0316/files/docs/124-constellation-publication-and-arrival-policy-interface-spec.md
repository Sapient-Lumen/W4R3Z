# Constellation publication and arrival-policy interface spec

## Purpose

The archive already says:

- constellation membership is not owner merge
- announcement is not claim
- claim is not bind
- visibility is separate from authority

What still remained under-specified was the outbound/publication side of that truth.

> if a share can become visible on another member merely because that member belongs to `my devices`, the product has already recreated the ambient-publication seam we explicitly do not want.

This document defines how publication to a personal constellation or member set must be reviewed.

## Why this needs its own spec

Current Resilio docs are again strong enough to show both the attraction and the problem.
When devices are linked under one identity, all folders become available across linked devices, and the chosen synchronization mode controls how much data lands there.
Custom placement on one member still commonly depends on switching that whole member to `Disconnected` mode first.
Those behaviors are convenient and often useful.
They also prove that publication scope, local arrival posture, and per-share path choice are still too entangled.

AnonSync should therefore make one additional boundary explicit:

> membership in a constellation may make a member eligible for publication, but it must not itself publish every subject there.

## Core rule

Publication to constellation members is a reviewed per-subject act.
It is not a side effect of membership.

Every publication surface must keep six truths adjacent:

1. what subject is being published
2. to which members or member classes it will become visible
3. what arrival posture each target member will receive
4. what path/materialization remains local and unresolved on those members
5. what authority does and does not widen because of publication
6. what receipt later proves the publication scope and arrival policy

## Public objects

### Publication row

A compact per-subject/per-target publication summary.

Suggested fields:

- `publication_row_id`
- `subject_ref`
- `source_member_ref`
- `target_scope` (`member`, `member-class`, `constellation`, `named-set`)
- `target_refs[]`
- `arrival_posture` (`announced-only`, `deferred-by-default`, `claim-review-required`, `metadata-visible`, `encrypted-only`, `do-not-publish`)
- `default_path_hint_policy_ref` nullable
- `default_materialization_hint_ref` nullable
- `authority_effect_summary`
- `receipt_refs[]`

### Publication review plan

A reviewed change object for making or changing a publication decision.

Suggested fields:

- `publication_review_plan_id`
- `subject_ref`
- `source_member_ref`
- `current_publication_state[]`
- `requested_publication_state[]`
- `blockers[]`
- `effect_summary`
- `non_effect_summary`
- `receipt_promise`

### Publication receipt

A durable proof of who a subject was published to and with what arrival posture.

Suggested fields:

- `publication_receipt_id`
- `subject_ref`
- `source_member_ref`
- `target_scope`
- `target_refs[]`
- `arrival_posture_summary`
- `authority_summary`
- `non_effect_summary`
- `recorded_at`
- `proof_refs[]`

## Fixed review order

Every publication review should preserve the same section order:

1. **Subject and source member**
2. **Target members and arrival posture**
3. **Local choice still left to each member**
4. **Authority and approval consequences**
5. **What publication does not mean**
6. **Receipt promise and later rollback**

### 1) Subject and source member

This section should answer:

- what subject is being considered
- which member is publishing it
- whether this is a one-off publication, template reuse, or a change to existing publication posture

### 2) Target members and arrival posture

This section should name the actual target members or classes and what they will receive.
Examples:

- `Studio-NAS: announced only`
- `Travel-Laptop: claim review required`
- `Cold mirror class: encrypted only`

The surface should never compress those into `available on my devices`.

### 3) Local choice still left to each member

This section should keep path, bind, and materialization truth explicit:

- which targets still need local claim review
- whether any default path hint is only a hint
- whether any materialization hint is only a suggestion
- whether the publication creates no path at all yet

### 4) Authority and approval consequences

This section should say:

- whether publication only changes visibility
- whether any member gains mutation, re-share, approval, or successor power
- whether approval memory or standing policy will later interact with this publication

### 5) What publication does not mean

This section should make non-effects explicit.
Examples:

- does not auto-bind paths on target members
- does not imply `writer` merely because the member is personal
- does not force a whole-device mode flip on the target member
- does not retract the subject elsewhere unless a wider withdrawal action is chosen

### 6) Receipt promise and later rollback

This section should say:

- which receipt proves the publication change
- how rollback, narrowing, or withdrawal will later cite this publication
- whether rollback is local to one member or wider to a class/scope

## Member-row anatomy

A dense publication row should preserve these labels in this order:

- `Subject`
- `Targets`
- `Arrival posture`
- `Local choice still needed`
- `Authority effect`
- `Next action`

Example:

```text
Photos-2026   Travel-Laptop, Home-NAS   announced only / encrypted only   path and claim still local   visibility only   Review publication
```

## Cross-surface rules

### Rule 1 — publication is separate from membership

Joining a member to a constellation must not silently add all current or future subjects to that member.

### Rule 2 — per-share publication must not require device-wide mode ritual

If one target member needs a custom path later, AnonSync should carry that as per-share arrival posture and claim review, not by asking the operator to reconfigure the whole member just to make one later connection safe.

### Rule 3 — visibility defaults may exist, but they must compile to inspectable publication state

A template may suggest `announce work shares to laptops`.
It must still produce inspectable per-subject publication rows and receipts.

### Rule 4 — withdrawal scope must be explicit

`Stop publishing to this member`, `stop publishing to this class`, and `withdraw from the whole constellation` are different actions and must remain different verbs.

## Workbench expectations

The workbench should expose a `Publication` lane or view that lets the operator answer:

- which subjects are published where
- which members only see announcements versus claimable arrivals versus encrypted-only replicas
- which publication changes would widen authority and which only change visibility
- which publication decisions are still drafts versus already receipted

## CLI/TUI parity

Textual surfaces should preserve the same adjacency, for example:

```text
Subject: workdocs
Source member: Studio-Laptop
Targets: Travel-Laptop, Home-NAS
Arrival posture: announced only, encrypted only
Local choice still needed: Travel-Laptop must claim path; Home-NAS stores encrypted replica only
Authority effect: visibility widened only; no writer or re-share rights added
Next: apply reviewed publication
```

## Acceptance test

The publication surface is good enough when a cautious operator can answer all of the following from one review pane:

- which subject is being published
- exactly which members will see it
- what posture each target member receives
- what still remains local and unresolved on those members
- whether authority widened or only visibility changed
- what receipt will later prove that publication decision
