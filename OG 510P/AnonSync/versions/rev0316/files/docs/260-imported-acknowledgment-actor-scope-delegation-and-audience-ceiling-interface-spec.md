# Imported acknowledgment actor-scope, delegation, and audience-ceiling interface spec

## Problem it solves

`259-imported-recipient-acknowledgment-binding-exactness-and-claim-ceiling-interface-spec.md`
closed one real seam:

> what exact artifact, correction notice, or replacement object did this imported acknowledgment bind to?

But one adjacent seam still remained too easy to flatten:

> **who can this acknowledgment honestly speak for?**

A same-thread reply from one human may arrive in any of these shapes:

- one exact target mailbox replying as itself
- one operator replying **from** a shared mailbox
- one member replying in a group or list lane
- one ticket agent replying inside a support system for a broader organization target
- one delegate replying on behalf of a target without proof that the whole audience adopted or acknowledged the same thing

Those are useful signals, but they are not the same scope.

An exact-object acknowledgment by **one actor** must not silently impersonate:

- acknowledgment by the whole target mailbox lane
- acknowledgment by the whole group or support audience
- acknowledgment by the whole organization
- proof that every recipient who previously received the artifact now shares the same interpretation

This document defines one explicit **acknowledgment actor-scope / delegation / audience-ceiling** contract so AnonSync can keep
`what object was acknowledged?`
separate from
`who, or what target lane, can that acknowledgment honestly stand in for?`

## Why this deserves first-class treatment

The comparison pressure that made this worth stealing came from two places:

- **DeriveBSD** reinforced that audience class, organization scope, named-recipient scope, and binding hints should stay **lane-exact** instead of being promoted across neighboring scopes just because they look related.
- AnonSync's own newer outward-artifact work made the missing seam obvious: once issued-head, correction, carryforward, delivery, and object-binding exactness all exist, the next honest question is not only `what did they acknowledge?` but also `who does this count for?`

Current real mail/product lanes reinforce the same law:
group addresses can represent many members, shared mailboxes can be used by multiple operators, and reply permissions can differ from audience membership.
That means a truthful product must preserve actor scope and represented lane scope separately.

## Core doctrine

For imported acknowledgments, **actor identity, represented reply lane, and covered audience scope are different truths**.

A reply can be:

- exact about the object,
- exact about the actor,
- exact about the mailbox or lane it came through,
- but still weak about the wider audience or organization it can speak for.

AnonSync should therefore preserve at least these distinct answers:

1. which concrete actor or operator produced the reply
2. which visible lane the reply appeared in
3. how that actor relates to the expected target scope
4. whether the reply is only actor-scoped, lane-scoped, audience-member-scoped, or truly target-wide
5. what current audience/scope claim ceiling is justified
6. what stronger proof would justify promoting that ceiling

If `recipient acknowledged` still has to impersonate
`the whole target audience now acknowledged`,
the interface is not honest enough.

## Objects

### Recipient-acknowledgment scope row

A compact row classifying one imported acknowledgment against one expected target or audience while preserving actor scope, represented lane, delegation evidence, and current promotion ceiling.

Suggested fields:

- `recipient_ack_scope_row_id`
- `artifact_family_ref`
- `target_scope_ref`
- `ack_source_ref`
- `raw_actor_ref` nullable
- `presented_sender_ref` nullable
- `reply_lane_kind` (`individual-mailbox`, `shared-mailbox`, `distribution-group`, `group-thread`, `ticket-agent-lane`, `same-product-seat`, `api-client`, `manual-attestation`, `other`)
- `actor_relation_to_target` (`exact-target-seat`, `delegate-of-target-lane`, `member-of-target-audience`, `member-of-target-organization`, `same-domain-ambiguous`, `mismatch`, `unknown`)
- `represented_scope_kind` (`individual-seat`, `target-lane`, `target-audience`, `target-organization`, `related-lane-only`, `unknown`)
- `delegation_evidence_kind` (`same-address`, `send-as-proof`, `send-on-behalf-language`, `group-role-proof`, `ticket-operator-role`, `same-product-seat-binding`, `manual-classified`, `none`, `unknown`)
- `scope_exactness` (`actor-only-exact`, `lane-probable`, `lane-exact`, `audience-member-only`, `audience-probable`, `audience-exact`, `organization-only`, `ambiguous`, `unknown`)
- `scope_claim_ceiling` (`actor-responded`, `target-lane-responded`, `one-audience-member-responded`, `target-audience-response-probable`, `target-audience-response-exact`, `unknown`)
- `stronger_scope_proof_needed` (`reply-from-target-lane`, `delegate-proof`, `group-wide-acknowledgment`, `same-product-per-recipient-proof`, `explicit-audience-statement`, `none`, `unknown`)
- `created_at`

### Acknowledgment scope receipt

A durable receipt proving that one imported acknowledgment was classified for scope/delegation truth against one expected target or audience.

Suggested fields:

- `ack_scope_receipt_id`
- `artifact_family_ref`
- `target_scope_ref`
- `ack_source_ref`
- `from_scope_claim_ceiling`
- `to_scope_claim_ceiling`
- `actor_relation_to_target`
- `represented_scope_kind`
- `scope_exactness`
- `delegation_evidence_kind`
- `supporting_refs[]`
- `created_at`

## Interface sections

Any client rendering imported acknowledgment truth for one artifact family and one expected target should preserve this order:

1. **Reply actor and visible lane**
2. **Relation to expected target scope**
3. **Delegation and represented scope**
4. **Current scope ceiling**
5. **Exact object binding companion**
6. **Receipts and next honest action**

### 1) Reply actor and visible lane

Show:

- the raw actor if known
- the visible sender or mailbox lane the acknowledgment appeared through
- whether the reply came from an individual mailbox, shared mailbox, group/thread lane, ticket system, or same-product seat

This section answers:

**who visibly replied, and through what lane?**

### 2) Relation to expected target scope

Show:

- whether the actor is the exact expected target seat
- whether the actor appears to be only one member of a group/audience target
- whether the actor appears to be a delegate or operator for the target lane
- whether the relationship is merely same-domain or otherwise ambiguous

This section answers:

**how tightly does this actor match the target we originally meant?**

### 3) Delegation and represented scope

Show:

- what evidence, if any, proves that the actor may speak through the target lane
- whether the represented scope is only the actor, the mailbox lane, one audience member, or the whole audience
- whether the current classification depends on manual judgment instead of structural proof

This section exists because reply-lane exactness and audience coverage are different truths.

### 4) Current scope ceiling

Show one visible ceiling:

- `actor responded`
- `target lane responded`
- `one audience member responded`
- `target audience response probable`
- `target audience response exact`
- `unknown`

This ceiling may combine with object-binding exactness from `259`, but it must remain a separate answer.

### 5) Exact object binding companion

Link the companion answer from `259`:

- what exact object was acknowledged
- how exact that binding is
- whether the reply is object-exact but still only actor-scoped
- whether stronger audience proof is still missing even when object proof is strong

This section answers:

**exactly what object was acknowledged, and for how much of the target scope does that matter?**

### 6) Receipts and next honest action

Show:

- acknowledgment-scope receipts
- linked acknowledgment-binding rows/receipts
- linked disclosure, correction, and issued-head rows
- next honest action (`keep actor-only`, `classify delegate proof`, `treat as one-member response`, `request explicit audience acknowledgment`, `other`)

## Rules

### Rule 1 — one actor is not the whole audience

A reply from one person inside a group-, alias-, or support-lane target may prove useful response.
It must not, by itself, prove that the whole target audience or organization acknowledged the object.

### Rule 2 — visible lane and raw actor are different truths

A message may visibly arrive from a shared mailbox or group lane while still being authored by one operator.
Conversely, one actor may reply personally inside a thread that originally targeted a mailbox or audience lane.
The surface must preserve both truths when available.

### Rule 3 — delegate proof is stronger than same-domain guesswork

`same company`, `same domain`, or `looks related` may justify investigation.
They must not automatically justify `target lane responded` or `target audience acknowledged`.

### Rule 4 — object exactness and scope exactness are orthogonal

A reply may be exact about the correction notice or replacement artifact while still being only actor-scoped.
Likewise, a lane-exact reply may still be vague about which exact object it acknowledged.
Neither truth may silently overwrite the other.

### Rule 5 — audience-wide acknowledgment needs audience-wide proof

If the target was a list, group, role mailbox, or broader audience, one actor's response should default to `one audience member responded` unless stronger evidence proves the lane or the whole audience acknowledged.

### Rule 6 — manual promotion must preserve the weaker raw facts

Operators may classify a reply as delegate-backed or audience-representative when outside evidence justifies it.
That promotion must preserve the original actor, lane, and weaker structural evidence rather than rewriting history.

## CLI sketch

```text
anonsync ack scope show --family <artifact-family> --target <target>
anonsync ack scope import --family <artifact-family> --target <target> --from <source>
anonsync ack scope classify --ack <ack-source> --relation delegate-of-target-lane
anonsync ack scope receipt show <receipt>
```

## Example states

- `support@vendor.example receives a correction; Alice replies from alice@vendor.example in the same thread quoting the exact correction notice` → object binding may be exact, but scope remains `actor responded` or `one audience member responded` until stronger delegate/lane proof exists
- `reply arrives from the shared mailbox itself with proved send-as / target-lane evidence` → scope may rise to `target lane responded`
- `one Google Group member replies inside a group thread` → useful actor/member response, but not whole-group acknowledgment
- `same-product successor observation imported per exact recipient` → stronger scope proof may exist for one exact seat without proving audience-wide adoption
- `operator manually records that the ticket agent is authorized to speak for the target support lane` → scope may rise to `target lane responded`, while preserving the manual-classified evidence source

## Anti-goals

This spec does not:

- create a generic CRM, helpdesk, or delegated-identity product
- infer organization-wide acknowledgment from one same-domain reply
- replace exact-object binding from `259`
- claim that one actor's response proves every audience member adopted or understood the change

## Companion surfaces

- `261-imported-acknowledgment-authorship-automation-classification-and-human-proof-interface-spec.md`

- `242-fact-authorship-buckets-lane-exactness-and-non-inference-interface-spec.md`
- `257-shareable-artifact-disclosure-queue-issued-head-and-current-surface-interface-spec.md`
- `258-issued-artifact-correction-notice-supersession-and-residual-reliance-interface-spec.md`
- `259-imported-recipient-acknowledgment-binding-exactness-and-claim-ceiling-interface-spec.md`
