# Reviewed recipient-target guard, retarget stale truth, and reissue interface spec

## Purpose

The archive already separates:

- local evidence from frozen outward packets
- frozen shareable artifact from outbound channel execution
- outbound channel completion from actual delivery witness
- current artifact head from compact carryforward explanation
- reviewed-action expected basis from ambient latestness

One narrow seam still remained under-specified:

> when a reviewed action is **recipient-specific** or **target-scoped**, what happens if the operator later points the same reviewed thing at a different recipient, different audience scope, or different outside destination before send or issue?

This document turns that seam into one explicit contract.
It is the recipient/target companion to `140-external-escalation-packet-and-redaction-review-interface-spec.md`, `252-outbound-channel-execution-delivery-witness-and-claim-ceiling-interface-spec.md`, and `255-reviewed-draft-basis-guard-stale-attempt-and-reissue-interface-spec.md`.

## Why this needs its own spec

Cross-reading the companion datacubes sharpened a distinction AnonSync should keep explicit:

- **pyCausalWeave** showed that continuity of an object is not the same thing as continuity of the target that a reviewed request was meant to hit
- **DeriveBSD** reinforced that exact scope and exact audience should stay visible instead of collapsing into loose near-matches
- AnonSync's own recipient-specific packet and carryforward work already implies the same law, but had not yet stated it cleanly for reviewed target changes

The product should therefore answer one explicit question in one place:

- which exact recipient, audience class, or outside destination the reviewed action expected
- which current target the operator is now trying to use
- whether the difference is exact-match, reviewed-equivalent, narrowed, widened, ambiguous, or stale-target
- whether a fresh reissue is required before send / issue / disclose / queue
- what receipt later proves the old target was refused or the new target was explicitly re-reviewed

If the operator still has to infer from remembered recipients, draft chips, or last-used channel state whether an older reviewed packet may be sent to a newly chosen recipient, the surface is not explicit enough.

## Core rule

For recipient-specific or target-scoped reviewed actions, **target identity is part of the reviewed basis**.

A change in recipient, audience scope, destination handle, or outside posting class must not silently inherit the older review.
The product is only allowed to preserve continuity automatically when it can prove the current target is explicitly equivalent under a visible equivalence rule.
Otherwise the product must surface `stale-target`, `retarget-needed`, or `reopen-required` truth and require explicit reissue.

The operator must be able to answer ten questions in one place:

1. what target the reviewed action expected
2. what target is current now
3. whether the difference is recipient identity, audience width, destination class, or mere label/alias presentation
4. whether the current target is exactly the same, reviewed-equivalent, narrower, wider, ambiguous, or missing
5. whether the action may proceed unchanged
6. whether explicit retarget review is required
7. whether the prior reviewed action remains historical truth
8. whether any already-recorded channel executions still point at the old target only
9. what tempting but unsafe shortcut is being refused
10. which receipt later proves stale-target refusal or explicit retarget reissue

If `already reviewed` still has to impersonate `safe to send to this different recipient now`, AnonSync has not made target-scoped review honest enough.

## Public objects

### Reviewed recipient-target guard row

A compact object describing the expected target for one reviewed action and the current comparison verdict.

Suggested fields:

- `reviewed_recipient_target_guard_row_id`
- `action_ref`
- `action_family` (`offer-issue`, `escalation-packet-issue`, `refresh-note-send`, `other`)
- `expected_target_rows[]`
- `current_target_rows[]`
- `target_comparison_verdict` (`matches`, `reviewed-equivalent`, `narrowed-target`, `widened-target`, `stale-target`, `ambiguous`, `missing`, `non-comparable`)
- `equivalence_rule_refs[]`
- `next_honest_actions[]`
- `supporting_receipt_refs[]`

### Target row

One expected or current destination element used in comparison.

Suggested fields:

- `target_row_id`
- `target_kind` (`named-recipient`, `recipient-class`, `constellation-member`, `private-archive`, `support-ticket`, `forum-post`, `clipboard-local-only`, `download-local-only`, `api-destination`, `unknown`)
- `target_descriptor`
- `audience_width` (`single`, `bounded-set`, `class`, `public`, `local-only`, `unknown`)
- `address_or_locator_ref` nullable
- `equivalence_class_ref` nullable
- `sensitivity_posture` (`same-as-reviewed`, `narrower`, `wider`, `ambiguous`, `unknown`)
- `notes`

### Retarget explanation

A read object explaining exactly why the current target may proceed, must reissue, or is blocked.

Suggested fields:

- `retarget_explanation_id`
- `action_ref`
- `expected_target_summary`
- `current_target_summary`
- `target_comparison_verdict`
- `why`
- `allowed_shortcuts[]`
- `forbidden_shortcuts[]`
- `proof_refs[]`

### Retarget review plan

A prepared review object for explicitly moving a reviewed action onto a different target.

Suggested fields:

- `retarget_review_plan_id`
- `prior_action_ref`
- `prior_target_rows[]`
- `requested_target_rows[]`
- `target_comparison_verdict`
- `requested_outcome` (`reissue-on-new-target`, `keep-old-target`, `cancel-old-action`, `freeze-old-action`, `other`)
- `carryforward_fields[]`
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Retarget receipt

A durable object proving that a stale-target attempt was refused or that a newer action explicitly replaced the older one on a different target.

Suggested fields:

- `retarget_receipt_id`
- `prior_action_ref`
- `prior_target_rows[]`
- `current_target_rows[]`
- `target_comparison_verdict_before`
- `outcome` (`stale-target-refused`, `retarget-reissued`, `retarget-cancelled`, `equivalence-admitted`)
- `successor_action_ref` nullable
- `recorded_at`
- `proof_refs[]`

## Comparison verdicts

### `matches`

Use when the current target rows are exactly the same reviewed destination set.

### `reviewed-equivalent`

Use only when a visible equivalence rule proves the current target is materially the same destination for review purposes.
Examples may include a reviewed mailbox alias equivalence, an explicitly mapped support-ticket alias, or another already-proved same-recipient identity.
This class must cite the equivalence rule; it must never be inferred from similar labels alone.

### `narrowed-target`

Use when the current target is strictly narrower than the reviewed target and policy allows that narrowing to proceed only after an explicit visible verdict.
This class must not silently auto-send just because the new target feels safer.

### `widened-target`

Use when the current target broadens audience width, destination class, or disclosure reach.
This class must always require explicit reissue or reopen.

### `stale-target`

Use when the action was reviewed for one target and the current target is different enough that the earlier review no longer honestly binds.
This is the default retarget failure class.

### `ambiguous`

Use when the product lacks enough proof to decide sameness or safe narrowing.
Ambiguity must block silent inheritance.

## Fixed inspection order

Every recipient-target guard surface should preserve the same sections in the same order:

1. **Reviewed action and expected target**
2. **Current target now**
3. **Comparison verdict and equivalence proof**
4. **What is blocked or still allowed**
5. **Retarget reissue path and receipt promise**

This order is mandatory across GUI, local web, TUI, CLI, and API-backed projections.

## Rules

### Rule 1 — target continuity is not action continuity

A packet, offer, or refresh note may remain the same family while its intended target changes.
That does not preserve the truth of the older reviewed send/issue request by itself.

### Rule 2 — widening target always reopens

Moving from one named recipient to a broader class, from a private archive to a forum post, from a support vendor packet to a public community packet, or from any local-only destination to any outward destination must never silently inherit the older review.

### Rule 3 — narrowing still needs an explicit verdict

A narrower current target may be allowed, but only through an explicit visible verdict such as `narrowed-target` or `reviewed-equivalent`.
The product must not auto-send just because the new target looks safer.

### Rule 4 — channel changes and target changes are different truths

Changing from clipboard to web-share or from save-as to attachment export is a channel change.
Changing who or what the artifact is meant to reach is a target change.
The product must keep those truths separate.

### Rule 5 — old channel executions stay attached to the old target

If an earlier local execution already copied, downloaded, or passed data toward the old target, later retarget review must not rewrite that history as if it had always pointed at the new target.

### Rule 6 — equivalence must be cited, not guessed

`reviewed-equivalent` requires one visible equivalence proof.
Matching display names, adjacent ticket numbers, or operator memory are not enough.

## CLI / API parity notes

Suggested CLI forms:

```text
anonsync reviewed-action target-guard show <action>
anonsync reviewed-action retarget compare <action> --to <target>
anonsync reviewed-action retarget reissue <action> --to <target>
```

Suggested API additions live best beside the basis-guard resources rather than inside channel-execution resources.

## Acceptance examples

- `Reviewed vendor packet still points at same ticket mailbox` → `matches`
- `Reviewed vendor packet now points at renamed alias with explicit same-ticket proof` → `reviewed-equivalent`
- `Reviewed packet for trusted operator now aimed at public forum paste` → `widened-target` and reissue required
- `Reviewed packet for recipient class now aimed at one named member` → explicit `narrowed-target` verdict or reissue, never silent send
- `Older copied packet history remains attached to old target while new target awaits reissue` → preserved dual truth

## Failure examples

- letting a reviewed support packet silently inherit a new recipient because only the channel UI changed
- treating `same display name` as recipient identity proof
- rewriting older `copied` or `share invoked` history to make it look like the newer retarget had already happened
- using `already reviewed` as permission to widen from private disclosure to public posting

## Relationship to the broader archive

This spec does not create a general-purpose workflow engine.
It only closes one specific seam where AnonSync still risked lying:

- `reviewed action exists`
- `current basis still matches`
- `current target still matches`
- `channel executed locally`
- `recipient actually received`

are all different truths and should remain different truths.
