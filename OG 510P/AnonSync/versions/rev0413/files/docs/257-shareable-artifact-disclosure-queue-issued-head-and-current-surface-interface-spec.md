# Shareable-artifact disclosure queue, issued head, and current-surface interface spec

## Purpose

The archive already separates:

- current retained head from current frozen shareable head
- shareable head from carryforward / refresh-note explanation
- reviewed target continuity from ambient retargeting
- local channel completion from stronger later delivery witness

One narrow seam still remained under-specified:

> when a family already has an older artifact that was actually issued outwardly, a newer frozen shareable head, and perhaps even a queued send, what exact surface says which artifact is **currently in force outwardly** for one recipient or audience right now?

This document turns that seam into one explicit contract.
It is the outward-currentness companion to `247-shareable-artifact-lineage-head-register-and-warning-surface-interface-spec.md`, `252-outbound-channel-execution-delivery-witness-and-claim-ceiling-interface-spec.md`, `253-shareable-artifact-carryforward-delta-ledger-and-refresh-notice-interface-spec.md`, and `256-reviewed-recipient-target-guard-retarget-stale-and-reissue-interface-spec.md`.

## Why this needs its own spec

Cross-reading the companion datacubes sharpened a distinction AnonSync should keep explicit:

- **EvidenceVault** showed that candidate queue state, executed publication, and stable public surface are different objects with different jobs
- **Goldenrule** reinforced that current-head summaries must stay explicit instead of relying on ambient latestness
- AnonSync's own head-register, carryforward, channel-ceiling, and target-guard work already implies the same law, but had not yet stated it cleanly for outward currentness

The product should therefore answer one explicit question in one place:

- which artifact is current for new reuse right now
- whether any outward issue is only draft, prepared, queued, or blocked
- which exact issue event most recently executed
- which artifact is currently outwardly in force for one recipient or audience
- which current outward-surface snapshot corresponds to that issued artifact
- which stronger recipient receipt, if any, exists beyond the issue event itself

If the operator still has to infer from a newer frozen head, a queued send badge, or a copied refresh notice what the other side should currently be assumed to have, the surface is not explicit enough.

## Core rule

For retained outward artifact families, **current shareable head is not the same truth as current issued head**.

A newer frozen head may become the current shareable head for future use before it becomes the current outward surface for any recipient.
A queued issue item may prepare or schedule that transition without making it true yet.
Only an executed issue event may advance the current issued head for one target or audience.
Later delivery witness may strengthen what is known after that, but it does not rewrite the issue transition itself.

The operator must be able to answer ten questions in one place:

1. what artifact is current for new reuse now
2. whether a newer outward issue is only draft, prepared, queued, or blocked
3. which exact target or audience the queued issue is for
4. which exact issue event executed most recently
5. which artifact is currently issued outwardly for that target now
6. which frozen outward-surface snapshot corresponds to that issued artifact
7. whether a newer shareable head exists but is not yet outwardly current
8. whether target guard or basis guard is blocking the queued transition
9. whether stronger delivery witness exists beyond issue execution
10. which receipt later proves the outward currentness changed

If `ready`, `queued`, or `newest head` still has to impersonate `this is what the other side currently has`, AnonSync has not made retained outward state honest enough.

## Public objects

### Artifact disclosure register

A compact object describing one artifact family for one target or audience together with the current shareable head, current queued issue posture, latest executed issue event, and current issued head.

Suggested fields:

- `artifact_disclosure_register_id`
- `artifact_family_ref`
- `target_scope_ref`
- `target_scope_summary`
- `current_shareable_head_ref` nullable
- `queued_issue_item_ref` nullable
- `latest_issue_execution_ref` nullable
- `current_issued_head_ref` nullable
- `current_issued_surface_snapshot_ref` nullable
- `delivery_claim_ceiling` (`none`, `issue-executed`, `passed-to-target`, `recipient-ack`, `same-product-redeem`, `unknown`)
- `register_verdict` (`nothing-issued-yet`, `issued-head-current`, `new-shareable-head-unissued`, `issue-queued-awaiting-execution`, `issue-blocked-stale-basis`, `issue-blocked-stale-target`, `ambiguous`, `unknown`)
- `next_honest_actions[]`
- `supporting_receipt_refs[]`

### Artifact issue queue item

A prepared or queued outward-action object for one frozen head and one target.

Suggested fields:

- `artifact_issue_queue_item_id`
- `artifact_family_ref`
- `artifact_ref`
- `target_scope_ref`
- `queue_state` (`draft`, `prepared`, `queued`, `running`, `blocked-stale-basis`, `blocked-stale-target`, `executed`, `cancelled`, `failed`, `unknown`)
- `basis_guard_ref` nullable
- `target_guard_ref` nullable
- `requested_channel_kind`
- `prepared_refresh_notice_ref` nullable
- `created_at`
- `executed_at` nullable

### Issue execution receipt

A durable object proving one queued or immediate outward issue event actually executed.

Suggested fields:

- `issue_execution_receipt_id`
- `artifact_issue_queue_item_ref` nullable
- `artifact_ref`
- `target_scope_ref`
- `channel_execution_ref` nullable
- `executed_transition` (`issue-executed`, `issue-refused-stale-basis`, `issue-refused-stale-target`, `issue-cancelled`, `issue-failed`)
- `resulting_current_issued_head_ref` nullable
- `resulting_surface_snapshot_ref` nullable
- `recorded_at`
- `proof_refs[]`

### Issued-surface snapshot

A frozen outward-facing wrapper describing what artifact became current for one recipient or audience after one executed issue event.

Suggested fields:

- `issued_surface_snapshot_id`
- `artifact_family_ref`
- `target_scope_ref`
- `issued_head_ref`
- `visible_summary`
- `refresh_notice_ref` nullable
- `supersedes_snapshot_ref` nullable
- `created_from_issue_execution_ref`
- `created_at`

### Issued-head transition receipt

A durable receipt proving how current issued head changed for one target or audience.

Suggested fields:

- `issued_head_transition_receipt_id`
- `artifact_family_ref`
- `target_scope_ref`
- `prior_issued_head_ref` nullable
- `new_issued_head_ref` nullable
- `cause` (`first-issue`, `queue-executed`, `manual-issue`, `withdrawn`, `superseded`, `ambiguity-cleared`, `unknown`)
- `issue_execution_receipt_ref` nullable
- `recorded_at`
- `proof_refs[]`

## Register verdicts

### `nothing-issued-yet`

Use when the family has no currently issued outward artifact for that target.
A current shareable head may still exist.

### `issued-head-current`

Use when the current shareable head and current issued head are the same artifact, or when no newer queued/blocked issue challenges the current issued answer.

### `new-shareable-head-unissued`

Use when a newer shareable head exists but has not yet been executed outwardly for this target.
The current issued head therefore remains older on purpose.

### `issue-queued-awaiting-execution`

Use when a prepared/queued issue item exists for a newer head but has not executed yet.
This verdict must not silently advance current issued head.

### `issue-blocked-stale-basis`

Use when the queued transition can no longer execute honestly because its expected basis drifted.
The old current issued head remains current until a new execution replaces it.

### `issue-blocked-stale-target`

Use when the queued transition can no longer execute honestly because its reviewed target drifted.
Again, the old current issued head remains current until a new execution replaces it.

### `ambiguous`

Use when the product lacks enough proof to name one unique current issued head.
Ambiguity must stay visible rather than being squeezed into `latest`.

## Fixed inspection order

Every artifact-disclosure-register surface should preserve the same sections in the same order:

1. **Artifact family and target scope**
2. **Current shareable head**
3. **Queued issue state**
4. **Current issued head and outward-surface snapshot**
5. **Delivery witness beyond issue execution**
6. **Receipts and next honest action**

This order is mandatory across GUI, local web, TUI, CLI, and API-backed projections.

## Rules

### Rule 1 — freeze does not issue

Making a newer artifact the current shareable head does not, by itself, change what is outwardly current for any recipient.

### Rule 2 — queue does not issue

Preparing, scheduling, or queueing a send/issue does not, by itself, change current issued head.
Only execution may do that.

### Rule 3 — execution does not imply receipt

An executed issue event may advance current issued head and issued-surface snapshot for one target without proving that the recipient actually received, opened, redeemed, or adopted it.
Those stronger truths stay in delivery-witness surfaces.

### Rule 4 — target scope remains part of outward currentness

Current issued head is scoped to one recipient or audience.
One target may remain on an older issued head while another has already moved to a newer one.

### Rule 5 — stale guards block transition, not history rewrite

If basis guard or target guard blocks a queued issue, the product must keep the current issued head unchanged and record the blocked attempt explicitly.
It must not silently promote the newer head nor erase the old issued-surface history.

### Rule 6 — carryforward and outward currentness are adjacent but different

Carryforward explains what changed since an older disclosed artifact.
The disclosure register explains which artifact is currently outwardly in force.
Neither one replaces the other.

## CLI / API parity notes

Suggested CLI forms:

```text
anonsync artifact disclosure show --family <family> --target <target>
anonsync artifact issue prepare --family <family> --artifact <artifact> --target <target>
anonsync artifact issue queue show <queue_item>
anonsync artifact issue record-execution <queue_item>
```

Suggested API additions live best beside artifact carryforward, target guards, and outbound-execution resources rather than inside lineage-only resources.

## Acceptance examples

- `Newer packet frozen, no send prepared yet, vendor still has older issued packet` → `new-shareable-head-unissued`
- `Newer packet queued to same vendor, queue not yet executed, older packet still current outwardly` → `issue-queued-awaiting-execution`
- `Queued packet blocked because approval basis drifted; older issued packet still current` → `issue-blocked-stale-basis`
- `Queue executes for mailbox A; mailbox B still remains on older issued head` → two different disclosure registers with different `current_issued_head_ref`
- `Vendor acknowledgment arrives later` → delivery witness strengthens beyond issue execution without changing the historical execution receipt

## Failure examples

- treating `newest frozen head` as proof of what a recipient currently has
- treating `queued` as proof that outward currentness already changed
- rewriting older issued history when a queued transition later blocks on stale basis or stale target
- letting carryforward summary or refresh notice replace the need to say which artifact is actually current outwardly now

## Relationship to the broader archive

This spec does not create a generic release manager or messaging subsystem.
It only closes one specific seam where AnonSync still risked lying:

- `current shareable head`
- `queued issue item`
- `executed issue event`
- `current issued head`
- `later delivery witness`

are all different truths and should remain different truths.


## Companion surfaces

- `258-issued-artifact-correction-notice-supersession-and-residual-reliance-interface-spec.md`
- `259-imported-recipient-acknowledgment-binding-exactness-and-claim-ceiling-interface-spec.md`
- `260-imported-acknowledgment-actor-scope-delegation-and-audience-ceiling-interface-spec.md`
