# Share authority epoch and stale-capability rotation spec

The archive already has capability-offer grammar, authority-mutation review, compromise response, retained-copy honesty, and successor continuity.
This document answers a narrower seam those abstractions still leave too loose:

> what must a real operator surface literally show when authority material changes for a share, so AnonSync never implies that `rotated`, `re-shared`, or `changed permissions` means everyone cleanly moved to the new trust boundary at once?

This is the authority-epoch companion to `52-capability-offer-and-claim-artifact-spec.md`, the grant-boundary companion to `74-authority-mutation-and-grant-boundary-review-spec.md`, the compromise-side companion to `69-compromise-containment-and-trust-rotation-interface-spec.md`, and the retained-copy companion to `87-revocation-recall-and-retained-copy-attestation-spec.md`.

## Why this needs its own spec

Resilio's current docs still make this seam unusually clear.
`What's the difference between Standard and Advanced folders?` says Standard folders use randomly generated keys while Advanced folders use PKI and certificates, that Standard peers can share the key they have without the same bounded owner model, that on-the-fly permission changes are not possible for Standard folders, that changing permissions requires remove-and-re-add with a new key, and that Standard folders cannot be converted into Advanced without removing and re-adding them.
`Key structure and flow` then says a key change on one peer is not distributed automatically and peers with the old key continue syncing with each other while no longer syncing with the changed peer.
`Sharing a folder locally` adds that some local-share permission changes also require remove-and-re-share ritual, that local-share access can be lowered by a remote owner, and that disconnecting/removing the source share removes the local share while reconnecting the source does not reconnect the local share automatically.

That is useful support knowledge.
It is not yet one public rotation contract.

The practical consequence is that several different truths still blur together too easily:

- a new authority boundary was created
- old authority material still exists and may still work elsewhere
- some peers moved to the new epoch while others did not
- some derivative/local-share surfaces must be rebuilt rather than mutated in place
- some portable offers, remembered approvals, or stale keys now point at superseded authority
- the operator still has a mixed-epoch swarm rather than one converged trust boundary

If the operator still has to remember that one share class supports live grant changes, another requires re-share ritual, and a rotated key may leave an older peer set quietly syncing among itself, the interface is not explicit enough.

## Core rule

AnonSync should treat any non-trivial change to share authority material as an **authority epoch** transition.
That means the product should keep these truths separate at all times:

- new authority issued
- stale authority still redeemable somewhere
- old and new epochs coexist
- some peers or derivatives are intentionally stranded
- convergence to the new epoch is observed, partial, pending, or impossible

The product may compress low-risk cases.
It may not let `rotate`, `change access`, `re-share`, `replace key`, or `upgrade share type` imply clean convergence unless the epoch map actually says so.

## Vocabulary

### Authority epoch

One durable generation of share authority material.
An epoch may be certificate-backed, key-backed, or another supported authority class, but it must have a stable handle, provenance, and validity window.

### Stale-capability posture

A durable statement about older authority material that still exists after a newer epoch is issued.
Examples: `still-redeemable`, `observed-retired`, `stranded-peer-only`, `artifact-only`, `unknown-offline`.

### Epoch rotation review

A reviewed case where the operator changes share authority material, share class, grant boundary, or rotation-sensitive derivative state and wants the product to say what old authority remains, who still depends on it, and what convergence would mean.

### Convergence verdict

The strongest honest statement the product can currently make about epoch transition progress.
Examples: `not-started`, `new-epoch-issued`, `mixed-epoch`, `old-epoch-quarantined`, `observed-new-epoch-only`, `unknown-offline`.

### Rotation receipt

A durable record proving which epoch became current, what stale authority remained, which peers/derivatives migrated, and what convergence was or was not observed.

## Fixed review order

Every non-trivial epoch-rotation or share-authority replacement case should render the same sections in the same order:

1. **Requested boundary change**
2. **Current epoch map**
3. **Stale-capability fallout**
4. **Derivative and migration obligations**
5. **Convergence and observation posture**
6. **Receipt promise**

### 1) Requested boundary change

This section should show:

- share and current authority class in scope
- whether the operator is rotating a key/certificate boundary, narrowing grants, reissuing offers, upgrading share class, or inspecting only
- whether the requested result is `issue-new-epoch`, `retire-old-epoch`, `quarantine-old-epoch`, `upgrade-authority-class`, or `inspect-only`
- whether retained-copy or compromise follow-up is also in scope, or merely adjacent

The operator must be able to answer: **what boundary is changing, and are we really changing authority material rather than only UI labels or per-peer grants?**

### 2) Current epoch map

This section should show:

- current epoch handle and prior known epoch handles
- authority class for each epoch (`key-backed`, `certificate-backed`, `derived-local`, `encrypted-derivative`, `unknown-legacy`)
- which peers, derivatives, or portable artifacts still reference each epoch
- whether older epochs are still capable of syncing, only capable of claim, or already retired

The operator must be able to answer: **how many authority generations exist right now, and who still sits on each one?**

### 3) Stale-capability fallout

This section should show:

- whether old portable offers, copied keys, saved links, or remembered approvals still matter
- whether any Standard/key-style epoch can still form a live older swarm after new issuance
- whether any stale authority is intentionally tolerated during migration or must be quarantined now
- which peers will become stranded, downgraded, or explicitly unsupported if old epoch retirement proceeds

The operator must be able to answer: **what old authority still exists, and what harm or drift could it still cause?**

### 4) Derivative and migration obligations

This section should show:

- whether local derivations, local shares, or dependent grants can mutate in place or require remove-and-recreate style migration
- whether a share-class upgrade implies data continuity with authority discontinuity
- whether derivative visibility, local placeholders, or downstream access must be rebuilt against the new epoch
- which migration work can stay compressed and which must split into follow-on reviewed actions

The operator must be able to answer: **what has to be rebuilt, reissued, or re-adopted rather than magically preserved?**

### 5) Convergence and observation posture

This section should show:

- convergence verdict for the rotation
- which peers have observed the new epoch and which are still unknown/offline
- whether old epoch use is blocked, merely discouraged, or still live until remote observation catches up
- whether the strongest honest statement is `new epoch issued` or the stronger `old epoch no longer observed anywhere relevant`

The operator must be able to answer: **did we only create the new boundary, or did the swarm actually converge to it?**

### 6) Receipt promise

This section should show:

- which rotation receipt will exist after apply, defer, or refusal
- what it will later prove about current epoch, stale-capability posture, derivative migration, and convergence state
- whether later quarantine, recall, or compromise follow-up is still required for a stronger claim
- where later audit survives if the action resumes from another channel

The operator must be able to answer: **what later evidence will prove we issued a new epoch, retired the old one, or merely started a mixed-epoch migration?**

## Public objects

### Share authority epoch

Fields:

- `share_authority_epoch_id`
- `share_ref`
- `epoch_handle`
- `authority_class` (`key-backed`, `certificate-backed`, `derived-local`, `encrypted-derivative`, `unknown-legacy`)
- `status` (`current`, `superseded`, `quarantined`, `retired-observed`, `unknown-offline`)
- `issued_from_epoch_ref` nullable
- `peer_refs[]`
- `offer_refs[]`
- `derivative_refs[]`
- `grant_refs[]`
- `stale_capability_posture` (`none-known`, `artifact-only`, `still-redeemable`, `live-peer-set`, `unknown-offline`)
- `convergence_verdict` (`not-started`, `new-epoch-issued`, `mixed-epoch`, `old-epoch-quarantined`, `observed-new-epoch-only`, `unknown-offline`)
- `issued_at`
- `last_observed_at` nullable
- `provenance_ref` nullable

### Epoch rotation review

Fields:

- `epoch_rotation_review_id`
- `share_ref`
- `current_epoch_ref`
- `prior_epoch_refs[]`
- `requested_change_class` (`rotate-authority-material`, `narrow-share-authority`, `upgrade-share-class`, `reissue-derived-scope`, `inspect-only`)
- `requested_outcome` (`issue-new-epoch`, `retire-old-epoch`, `quarantine-old-epoch`, `upgrade-authority-class`, `inspect-only`)
- `stale_capability_findings[]`
- `derivative_migration_findings[]`
- `convergence_requirements[]`
- `follow_on_review_refs[]`
- `action_options[]`
- `epoch_rotation_report_ref`
- `generated_at`
- `expires_at` nullable

### Epoch rotation receipt

Fields:

- `epoch_rotation_receipt_id`
- `review_ref`
- `share_ref`
- `current_epoch_summary`
- `superseded_epoch_summary`
- `stale_capability_summary`
- `derivative_migration_summary`
- `convergence_summary`
- `actor_ref`
- `created_at`
- `provenance_ref` nullable

## Public rules

1. **Issuing new authority is not the same as converging on it.**
   The product must never let `rotated` imply that old peers or copied artifacts stopped working unless the epoch map actually proves retirement.

2. **Folder/share class differences must become explicit epoch facts, not buried folklore.**
   If one authority class supports live mutation while another requires reissue/re-adopt ritual, the rotation surface must show that before apply.

3. **Old capability material stays visible until retired or explicitly tolerated.**
   A copied key, saved offer, derivative share, or offline peer cannot disappear from the story just because the operator issued something newer.

4. **Derivative/local-share fallout must stay explicit.**
   If a dependent local projection or derivative cannot mutate in place, the product should say that it must be rebuilt against the new epoch instead of presenting failed `change access` attempts as surprising exceptions.

5. **Convergence requires observation.**
   Offline or unknown peers keep the strongest honest claim below `observed-new-epoch-only`.

6. **Rotation may trigger but not replace other reviews.**
   Compromise, recall, successor, or authority-mutation follow-up may be attached, but the epoch review must still preserve its own boundary-change meaning.

## CLI surface

```text
anonsync epochs list --share shr_01J...
anonsync epochs show sae_01J...
anonsync rotate prepare --share shr_01J... --change rotate-authority-material --outcome issue-new-epoch --plan
anonsync rotate prepare --share shr_01J... --change upgrade-share-class --outcome upgrade-authority-class --plan
anonsync rotate show err_01J...
anonsync rotate apply err_01J...
anonsync rotate receipt show errc_01J...
```

The group should answer:

- which authority epoch is current now
- which older epoch handles, offers, or peers still remain in scope
- whether the result is clean convergence, mixed-epoch migration, or only newly-issued authority
- which derivative/local-share or downstream migration work still remains
- which receipt later proves the real transition rather than the optimistic one-liner
