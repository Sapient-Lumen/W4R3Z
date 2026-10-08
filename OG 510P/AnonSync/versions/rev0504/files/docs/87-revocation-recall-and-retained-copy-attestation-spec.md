# Revocation, recall, and retained-copy attestation spec

The archive already has exit grammar, authority mutation review, disclosure residue, successor continuity, and share-layout separation.
This document answers a narrower seam those abstractions still leave too loose:

> what must a real operator surface literally show when someone says `disconnect`, `remove`, `revoke`, `narrow access`, or `retire this replica`, so AnonSync never implies that stopping future sync is the same thing as recalling already-delivered bytes?

This is the retained-copy companion to `63-subject-exit-and-residue-clearance-spec.md`, the authority companion to `74-authority-mutation-and-grant-boundary-review-spec.md`, the share-governance companion to `61-personal-constellation-and-authority-domain-spec.md`, the preservation companion to `56-recovery-material-and-continuity-bundle-spec.md`, and the history/rollback companion to `48-history-conflict-and-rollback-provenance-spec.md`.

## Why this needs its own spec

Resilio's current docs still make this seam easy to miss.
`User Management` says `Disconnect` revokes future updates for the selected peer but all files synchronized so far remain in that folder.
`Disconnecting and Removing Folders` says removing a folder from linked devices stops showing it on the linked identity set, yet the folder may still remain on remote devices not linked to that identity.
`Sync Private Identity & Linking My Devices` says linked devices get universal access and that all devices linked to one identity act as Owners.
`Encrypted folders` says encrypted backup peers keep bytes in encrypted form, always force `Overwrite any changed files`, cannot use Selective Sync, can only help restore if the right keys were saved and the original database continuity was preserved, and cannot restore deleted files from encrypted Archive back to others because they are read-only and follow the delete state.

That is useful support knowledge.
It is not yet one honest recall contract.

The practical consequence is that several operator meanings collapse together too easily:

- stop this peer from receiving future updates
- narrow this peer from write to read-only
- remove this share from my linked devices
- ask whether already-delivered copies still exist somewhere else
- know whether a retained encrypted backup can still help recovery later
- know whether the product is merely hiding a replica or actually proving copy recall

If the operator still has to infer that `revoked` may still mean `bytes remain`, that `removed from my devices` says nothing about other non-linked peers, or that an encrypted backup may still be the only reseed path even after ordinary access was narrowed, the interface is not explicit enough.

## Core rule

AnonSync should keep **future authority** and **already-retained bytes** separate at all times.
A boundary change may truthfully do one or more of these things:

- stop future updates
- narrow write or owner authority
- remove visibility from one local or linked surface
- attest that retained copies still exist on specific peers
- request or schedule remote deletion
- admit that no trustworthy recall proof exists yet

The product may not let any `remove`, `disconnect`, `revoke`, or `retire` verb imply byte recall unless there is explicit retained-copy evidence and an explicit recall verdict.

## Vocabulary

### Retained replica posture

A durable statement of what a known or inferred peer currently retains for a share and what that peer can still do with those bytes.

### Future-update posture

Whether a peer is still entitled to receive new changes.
Examples: `active`, `frozen`, `revoked-pending-observation`, `revoked-observed`, `unknown`.

### Recall verdict

The strongest honest statement the product can currently make about already-delivered bytes.
Examples: `not-requested`, `retained-copy-confirmed`, `future-updates-stopped`, `remote-delete-requested`, `remote-delete-observed`, `unknown-offline`.

### Retention attestation

A durable proof object saying that a peer kept bytes, kept only encrypted bytes, kept metadata only, or is currently unverified.

### Replica recall review

A reviewed case where the operator changes authority or share membership and wants the product to say, explicitly, what happens to retained copies.

### Recall receipt

A durable record proving what future authority changed, what retained-copy reality remained, and what still depends on remote observation or later follow-up.

## Fixed review order

Every non-trivial replica-recall or retained-copy review should render the same sections in the same order:

1. **Requested boundary change**
2. **Current authority and byte reality**
3. **Retained-copy and recovery findings**
4. **Recall and observation posture**
5. **Admissible actions**
6. **Receipt promise**

### 1) Requested boundary change

This section should show:

- share and peer/peer-set in scope
- whether the operator is revoking future updates, narrowing authority, removing linked presence, requesting remote delete, or inspecting only
- whether the requested byte outcome is `retain`, `attest`, `request delete`, or `prove nothing beyond future stop`
- whether the change is local-only, linked-constellation-scoped, or directed at independently trusted peers

The operator must be able to answer: **am I just stopping future sync, or am I also trying to say something about already-delivered copies?**

### 2) Current authority and byte reality

This section should show:

- current peer authority (`owner`, `write`, `read-only`, `encrypted-readonly`, `unknown`)
- current byte posture (`materialized`, `metadata-only`, `encrypted-materialized`, `unknown`)
- whether the peer is linked to the same personal constellation or is a separate grantee
- whether the peer currently contributes restore, reseed, or only retained storage

The operator must be able to answer: **what does this peer already have, and what can it still do before I change anything?**

### 3) Retained-copy and recovery findings

This section should show:

- whether retained bytes are expected to remain after apply
- whether those bytes are plaintext, encrypted-only, metadata-only, or unknown
- whether local recovery still depends on that retained replica
- whether preserved keys, database continuity, or other support material are required for future recovery from that replica
- whether the action would strand the last useful backup path or merely narrow an ordinary collaborator

The operator must be able to answer: **if I do this, what copies will still exist and how useful are they later?**

### 4) Recall and observation posture

This section should show:

- whether remote delete is impossible, unrequested, requested, pending peer observation, or observed
- whether offline peers still make the strongest honest statement only `future updates stopped`
- whether linked-surface removal says nothing about non-linked peers that already received the share
- whether a peer is hidden, detached, revoked, delete-requested, or actually observed to have stopped participating

The operator must be able to answer: **what do I know now, what am I only asking for, and what still depends on peers I have not yet observed?**

### 5) Admissible actions

This section should show:

- whether the honest action is revoke future updates only, narrow to read-only, preserve an encrypted backup, request remote delete, or block because the operator is confusing visibility cleanup with copy recall
- which shortcuts are forbidden because they would market `remove` as stronger than it really is
- whether the product can offer a safely compressed path because only future authority changes and the byte claim is intentionally minimal
- what follow-up remains if later recall or backup replacement is still desired

The operator must be able to answer: **what can I honestly do right now without lying about retained copies?**

### 6) Receipt promise

This section should show:

- which recall receipt or retention attestation will exist after apply, defer, or refusal
- what it will later prove about future authority, retained copies, recovery usefulness, and unresolved observation
- whether later remote delete observation or backup replacement is still required for a stronger claim
- where later audit survives if the action resumes from another channel

The operator must be able to answer: **what later evidence will prove that I stopped future sync, preserved a backup, or truly observed stronger recall?**

## Public objects

### Retained replica posture

Fields:

- `retained_replica_posture_id`
- `share_ref`
- `peer_ref` nullable
- `replica_scope` (`linked-constellation`, `direct-grantee`, `encrypted-backup`, `local-derivation`, `unknown-offline`)
- `authority_posture` (`owner`, `write`, `read-only`, `encrypted-readonly`, `revoked-future`, `unknown`)
- `byte_presence_posture` (`materialized`, `metadata-only`, `encrypted-materialized`, `unknown`)
- `future_update_posture` (`active`, `frozen`, `revoked-pending-observation`, `revoked-observed`, `unknown`)
- `recovery_contribution_posture` (`can-upload`, `can-reseed-with-continuity-material`, `retained-storage-only`, `cannot-contribute`, `unknown`)
- `recall_verdict` (`not-requested`, `retained-copy-confirmed`, `future-updates-stopped`, `remote-delete-requested`, `remote-delete-observed`, `unknown-offline`)
- `residue_findings[]`
- `last_verified_at`
- `provenance_ref` nullable

### Replica recall review

Fields:

- `replica_recall_review_id`
- `share_ref`
- `peer_refs[]`
- `current_retained_replica_posture_refs[]`
- `requested_boundary_change` (`revoke-future-updates`, `narrow-authority`, `retire-linked-presence`, `request-copy-recall`, `inspect-only`)
- `requested_byte_outcome` (`retain-existing-copies`, `attest-existing-copies`, `request-remote-delete`, `future-stop-only`, `unknown`)
- `authority_findings[]`
- `retention_findings[]`
- `recovery_findings[]`
- `observation_requirements[]`
- `action_options[]`
- `replica_recall_report_ref`
- `generated_at`
- `expires_at` nullable

### Replica recall receipt

Fields:

- `replica_recall_receipt_id`
- `review_ref`
- `share_ref`
- `peer_summary`
- `future_update_summary`
- `retained_copy_summary`
- `recovery_dependency_summary`
- `observation_summary`
- `actor_ref`
- `created_at`
- `provenance_ref` nullable

## Public rules

1. **Stop future updates is not copy recall.**
   The product must never let `disconnect`, `revoke`, or `remove` imply remote erasure unless a stronger recall verdict exists.

2. **Linked-surface removal is not universal recall.**
   A share disappearing from the linked identity set must not pretend to say anything about other already-granted peers.

3. **Authority narrowing is not byte narrowing.**
   Moving a peer from owner or write to read-only must still say what bytes remain and whether the peer can still serve as a recovery source.

4. **Encrypted backup truth must stay explicit.**
   A peer may keep encrypted bytes, be unable to decrypt them locally, still matter for reseed, and still be a weak source for ordinary restore. The surface must show that without making the operator read backup folklore.

5. **Offline peers keep recall unresolved.**
   If the product has not observed the remote peer after a recall or revoke request, the receipt should say so plainly.

6. **Remote delete is a different action family.**
   Requesting deletion of already-delivered bytes should not be silently bundled into ordinary authority revocation.

7. **Existing exit, authority, and disclosure verbs may remain, but they should compile to this contract whenever retained-copy meaning is in scope.**

## CLI surface

```text
anonsync replicas list --share shr_01J...
anonsync replicas show rrp_01J...
anonsync recall prepare --share shr_01J... --peer peer:dev_01J... --change revoke-future-updates --bytes attest-existing-copies --plan
anonsync recall prepare --share shr_01J... --peer-set linked:family --change retire-linked-presence --bytes future-stop-only --plan
anonsync recall prepare --share shr_01J... --peer peer:enc_01J... --change narrow-authority --bytes retain-existing-copies --plan
anonsync recall show rcr_01J...
anonsync recall apply rcr_01J...
anonsync recall receipt show rcrp_01J...
```

The group should answer:

- what authority changed now
- which peers still retain bytes and in what form
- whether any retained replica still matters for recovery or reseed
- whether recall stronger than `future updates stopped` is currently proven, merely requested, or still unknown
- which receipt later proves the honest outcome

## Workbench expectations

The workbench should expose one **Retained Copies & Recall** surface.
It should not replace share detail or exit pages, but it should unify one practical question across them:

> who still has bytes from this share, what can they still do with them, and what exactly do we mean when we say we revoked or removed access?

The page should group peers by:

- `active and trusted`
- `future updates stopped, retained copy remains`
- `encrypted backup / retained storage`
- `remote delete requested / awaiting observation`
- `unknown / offline`

A detail drawer should always show:

- **Current authority**
- **Retained byte posture**
- **Recovery usefulness**
- **Recall truth right now**
- **What stronger claim would still require**
- **Which receipt proves the last reviewed action**

## Report language additions

Recall workflows should reuse the common report model with two families:

- `replica-retention-report` — what bytes and authority posture currently exist for a peer or peer set
- `recall-review-report` — what future authority changes now, what retained copies remain, and what observation still blocks a stronger claim

## Why this matters

A careful sync product should be as honest about retained copies as it is about route exposure, recovery state, or exit residue.
If the product can already separate visibility, authority, layout, settlement, and rollback but still lets `disconnect` or `remove` quietly over-promise recall, then one of the most dangerous everyday verbs remains underspecified.

A mature AnonSync surface should let an operator move from `I need this peer to stop participating` to `what copies still remain?` to `does that peer still matter for recovery?` to `am I requesting delete or only proving future stop?` to `what receipt proves the strongest honest claim?` without support-article archaeology or comforting but misleading removal language.
