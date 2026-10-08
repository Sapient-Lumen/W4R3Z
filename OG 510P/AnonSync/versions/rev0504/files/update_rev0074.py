from pathlib import Path
import re

root = Path('/mnt/data/anonsync_rev0073_work')

def read(path):
    return (root / path).read_text()

def write(path, text):
    (root / path).write_text(text)

# --- new doc 87 ---
doc87 = """# Revocation, recall, and retained-copy attestation spec

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
"""
write('docs/87-revocation-recall-and-retained-copy-attestation-spec.md', doc87)

# --- README ---
readme = read('README.md')
readme = readme.replace('- Revision: `rev0073`', '- Revision: `rev0074`')
readme = readme.replace('- Timestamp: `2026.03.17.18.25` (America/New_York)', '- Timestamp: `2026.03.17.18.31` (America/New_York)')
readme = readme.replace('- Codename: `speedproofsemanticguard`', '- Codename: `recallproofretentionanchor`')
readme = re.sub(r"## What changed in this revision\n\nThis revision continues directly from `rev0072` and does seven things:\n\n1\.[\s\S]*?7\.[^\n]*\n", "## What changed in this revision\n\nThis revision continues directly from `rev0073` and does seven things:\n\n1. Re-checks **Resilio Sync** again with extra emphasis on the `disconnect/remove/revoke` seam: current docs still distinguish future-update revocation from already-delivered bytes, but mostly through scattered support language rather than one operator contract.\n2. Sharpens the **non-clone rationale** into a stricter rule: AnonSync should not let `remove`, `disconnect`, or `revoke` imply copy recall when the strongest honest claim is only `future updates stopped`.\n3. Adds a dedicated **revocation, recall, and retained-copy attestation spec** so the archive now says what a real operator surface must literally show before narrowing authority, retiring linked presence, preserving encrypted backups, or requesting stronger recall.\n4. Extends the **interface and daemon/API contract** with explicit retained-replica postures, recall reviews, and recall receipts rather than leaving retained-copy truth in peer memory and troubleshooting notes.\n5. Extends the **workbench/interface pattern language** so operators can see which peers still retain bytes, whether those bytes still matter for recovery, and what observation would be required for any stronger claim.\n6. Adds additional **canonical interface flows** for revoking future updates honestly and for preserving an encrypted backup without pretending that bytes were recalled or erased.\n7. Refreshes the **evaluation**, **ADRs**, **roadmap**, **open questions**, **status**, and **reading order** so future revisions keep retained-copy honesty explicit whenever access changes or replica retirement is in play.\n", readme, count=1)
anchor = '- a first-class semantic-runtime / optimization / fallback surface so operators can tell when a `performance` or `compatibility` change really weakens freshness, rename continuity, diff behavior, or verification guarantees\n'
readme = readme.replace(anchor, anchor + '- a first-class retained-replica / recall / attestation surface so operators can tell who still holds bytes, whether those bytes are plaintext or encrypted-only, and whether any stronger recall claim has actually been observed\n')
readme = readme.replace('- `docs/86-semantic-fallback-and-optimization-review-spec.md` — fixed semantic-optimization review anatomy for requested profile, guarantees at risk, detection/verification posture, degraded-target findings, and optimization receipts\n', '- `docs/86-semantic-fallback-and-optimization-review-spec.md` — fixed semantic-optimization review anatomy for requested profile, guarantees at risk, detection/verification posture, degraded-target findings, and optimization receipts\n- `docs/87-revocation-recall-and-retained-copy-attestation-spec.md` — fixed recall-review anatomy for requested boundary change, current byte/authority reality, retained-copy findings, recall posture, and recall receipts\n')
readme = readme.replace('then `85-share-annex-and-live-data-separation-spec.md`, then `86-semantic-fallback-and-optimization-review-spec.md`, then `41-report-and-intervention-language.md`', 'then `85-share-annex-and-live-data-separation-spec.md`, then `86-semantic-fallback-and-optimization-review-spec.md`, then `87-revocation-recall-and-retained-copy-attestation-spec.md`, then `41-report-and-intervention-language.md`')
write('README.md', readme)

# --- status rewrite for coherence ---
status = """# Status

## Scope of this revision

This revision is an in-place continuation of `rev0073`, driven by the current request:

- continue research and tighten the archive without letting it sprawl
- evaluate Resilio Sync further with enough care that the non-clone case stays evidence-based
- spend more time on interface specs rather than letting `disconnect`, `remove`, or `revoke` over-promise copy recall
- keep Linux-first, overlay-first, and least-privilege assumptions intact unless evidence truly breaks them
- keep turning support-lore seams into explicit product contracts
- make sure the archive has a better reason not to clone current Resilio revocation/removal behavior as though stopping future updates were close enough to recalling already-delivered bytes
- make sure future authority, retained copies, and stronger recall claims stay visibly separate

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- a deeper Resilio-derived warning that current revoke/disconnect/remove language still leaves retained-copy truth scattered across user-management, linked-device, and encrypted-backup articles
- a dedicated **revocation, recall, and retained-copy attestation spec** that says what a real operator surface must show before revoking future updates, narrowing authority, preserving an encrypted backup, or requesting stronger recall
- stronger interface and daemon/API requirements so retained-replica postures, recall reviews, and recall receipts become explicit public objects rather than support-lore side effects
- stronger workbench and pattern-language rules so operators can see which peers still retain bytes, whether those bytes still matter for recovery, and what observation blocks any stronger claim
- additional canonical flows for revoking future updates honestly and for preserving encrypted backup value without pretending ordinary removal erased bytes
- roadmap, ADR, status, open-question, and README updates so future revisions keep retained-copy honesty explicit whenever access changes or replica retirement appears

## The main shift

`rev0073` proved that performance and compatibility posture needed one explicit semantic-runtime contract rather than speed-oriented folklore.

`rev0074` applies the same discipline one layer closer to everyday trust language itself:

> a serious Linux-first workbench still is not specified tightly enough if the archive can define exits, authority mutation, recovery, and semantic downgrade honestly, yet still leave one ordinary operator question loose: when I revoke or remove a peer, what copies still remain, what can that peer still do with them, and what is the strongest honest recall claim I can make right now?

That changes the archive in six specific ways:

- retained-copy truth now renders as its own reviewed contract instead of hiding behind `disconnect` or `remove`
- linked-surface cleanup can no longer masquerade as universal recall
- encrypted backup usefulness now has one explicit place to say whether preserved keys, database continuity, or read-only posture still matter
- workbench and CLI now have one explicit place to compare future authority change against already-retained byte reality
- the Resilio comparison now lands a sharper non-clone argument: the weak seam is not merely awkward wording, but the lack of one honest reviewed contract for retained-copy and recall claims
- future access and exit work now has a narrower quality bar whenever revocation, backup preservation, or remote deletion are in scope

## What still remains unresolved

This revision intentionally does **not** overclaim closure on several important questions:

- how much of transport identity and overlay publication should be device-wide, share-scoped, or policy-scoped
- how strong disclosure-narrowing guarantees should be before the product becomes noisy or dishonest about residue
- how aggressive the default review queue should be before it becomes noisy
- how much UI simplification is safe without recreating the hidden coupling the archive is trying to escape
- how much one-click automation an exit surface should allow before it starts hiding scope, residue, or follow-up obligations
- how aggressive default compromise freezes should be before the product starts turning suspicion into disruptive magic
- when long-offline or clock-uncertain peers should be allowed to resume writable participation without first-class re-entry review
- when remote delete or overwrite waves should always force destructive-replay review instead of ordinary sync progress
- when non-trivial conflicts should always force full reviewed adjudication instead of a safely compressed resolution path
- when same-host derivations should always force full local-derivation review instead of a safely compressed path
- when live authority changes should always force full authority-mutation review instead of a safely compressed access-change path
- when nested, overlapping, or root-boundary-sensitive topology changes should always force full topology review instead of a safely compressed path
- when writer contention, burst-save delay, or mixed external-writer risk should always force full contention review instead of a safely compressed path
- when RAM pressure, watcher ceilings, indexing cost, or path blockers should always force full capacity-fit review instead of a safely compressed path
- when discovered state, recovery material, or reviewed control exposure should always force full bring-up review instead of a safely compressed startup path
- how broad one reviewed mutation grant may be in v1 before explicit authority becomes either too reusable or too noisy
- when an obviously same-lineage local target may use a safely compressed custody review versus always opening the full ownership-and-lineage sheet
- how much low-risk cross-channel continuation may stay compressed before channel-parity honesty becomes either noisy or too magical
- how much low-risk runtime-seat switching may stay compressed before state continuity, path reachability, and freshness honesty become either noisy or too magical
- how much low-risk relabeling may stay compressed before the product starts hiding meaningful authority replacement or same-person continuity fallout behind harmless-looking naming affordances
- how much low-risk layout cleanup or annex migration may stay compressed before the product starts hiding meaningful data/control separation fallout behind harmless-looking hidden-file cleanup affordances
- how much low-risk semantic optimization may stay compressed before the product starts hiding meaningful guarantee weakening behind harmless-looking speed or compatibility affordances
- how much low-risk recall or retained-copy attestation may stay compressed before the product starts hiding meaningful byte-retention fallout behind harmless-looking revoke/remove affordances

## Files added in this revision

- `docs/87-revocation-recall-and-retained-copy-attestation-spec.md`

## Files updated in this revision

- `README.md`
- `docs/00-status.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/30-interface-spec.md`
- `docs/31-daemon-api-spec.md`
- `docs/32-interface-flows.md`
- `docs/38-operator-workbench-interface-spec.md`
- `docs/39-interface-pattern-language.md`
- `docs/40-architecture-decisions.md`
- `docs/50-roadmap.md`
- `docs/64-critical-open-questions.md`
- `docs/87-revocation-recall-and-retained-copy-attestation-spec.md`
"""
write('docs/00-status.md', status)

# --- evaluation ---
eval_text = read('docs/10-resilio-sync-evaluation.md')
insert_eval = """
### 16af) Revocation and removal still over-promise recall too easily

Resilio's current docs expose one more seam that is easy to underestimate because the verbs sound ordinary.
`User Management` says `Disconnect` revokes future updates for the selected peer, but all files that have already been synchronized remain in that folder.
`Disconnecting and Removing Folders` says removing a folder from linked devices stops showing it on the linked identity set, yet it may still remain on remote devices that are not linked to that identity.
`Sync Private Identity & Linking My Devices` says linked devices get universal access and that linked devices effectively act as owners of the personal constellation's shares.
`Encrypted folders` says encrypted backup peers keep encrypted bytes, always force `Overwrite any changed files`, cannot use Selective Sync, may still help reseed only if the right keys were preserved and database continuity remains intact, and cannot restore deleted files from encrypted Archive back to others because they are read-only and follow the delete state.

That is useful support knowledge.
It is not yet one public recall contract.

The practical consequence is that several different claims still blur together:

- future updates stopped
n- authority narrowed
- hidden from my linked surfaces
- retained bytes still exist somewhere else
- preserved encrypted backup still matters for recovery
- stronger remote delete or copy-recall claim was actually observed

If the operator still has to remember that `removed` may only mean `no longer shown here`, that `revoked` may still mean `bytes remain`, and that a retained encrypted replica may still be the last useful reseed path even after ordinary access was narrowed, the interface is not explicit enough.

AnonSync should instead publish one public retained-copy model with:

- explicit retained-replica posture for each peer or peer set
- one reviewed recall case whenever future authority and already-retained bytes both matter
- one explicit difference between `future updates stopped`, `retained copy attested`, `remote delete requested`, and `remote delete observed`
- explicit recovery-usefulness findings so encrypted backup or read-only retained storage cannot masquerade as ordinary collaborators or ordinary erasure
- durable recall receipts proving what changed now and what stronger claim still depends on later peer observation

### Requirement 68 — non-trivial revocation and removal changes must share one reviewed retained-copy and recall contract

If the operator still has to combine disconnect notes, linked-device scope, encrypted-backup caveats, and peer memory to answer `who still has bytes from this share and what exactly did my revoke/remove action prove?`, the product has not actually exposed its recall truth.

AnonSync should instead publish one public model with explicit retained-replica postures, explicit recall reviews, explicit byte-retention verdicts, explicit recovery-usefulness findings, and durable receipts that preserve the difference between future authority stop, retained-copy attestation, delete request, and observed stronger recall.

"""
eval_text = eval_text.replace('\n## Final judgment\n', '\n' + insert_eval + '## Final judgment\n')
eval_text = eval_text.replace('\nn- authority narrowed\n', '\n- authority narrowed\n')
write('docs/10-resilio-sync-evaluation.md', eval_text)

# --- interface spec ---
iface = read('docs/30-interface-spec.md')
insert_iface = """
### Retained replica posture

A durable statement of what a peer currently retains for a share and what that peer can still do with those bytes.
This exists so operators do not have to guess whether `revoked`, `removed`, and `recalled` meant the same thing.

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

A reviewed case for changing future authority while staying honest about already-retained bytes.
This exists so disconnect, revoke, remove, encrypted-backup preservation, and remote-delete requests do not collapse into one comforting but misleading `remove` story.

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

A durable record proving what future authority changed and what retained-copy claim was honestly supported.

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

"""
iface = iface.replace('### Conflict item\n', insert_iface + '### Conflict item\n')
# add CLI section if anchor present
iface = iface.replace('Inspect and mutate semantic-impacting optimization posture without pretending that performance tuning and guarantee weakening are the same thing.\n', 'Inspect and mutate semantic-impacting optimization posture without pretending that performance tuning and guarantee weakening are the same thing.\n\n### Replica recall and retained-copy review\n\n```text\nanonsync replicas list --share shr_01J...\nanonsync replicas show rrp_01J...\nanonsync recall prepare --share shr_01J... --peer peer:dev_01J... --change revoke-future-updates --bytes attest-existing-copies --plan\nanonsync recall prepare --share shr_01J... --peer-set linked:family --change retire-linked-presence --bytes future-stop-only --plan\nanonsync recall show rcr_01J...\nanonsync recall apply rcr_01J...\nanonsync recall receipt show rcrp_01J...\n```\n\nInspect and mutate retained-copy posture without pretending that revoking future participation and recalling already-delivered bytes are the same thing.\n')
write('docs/30-interface-spec.md', iface)

# --- daemon api ---
daemon = read('docs/31-daemon-api-spec.md')
insert_daemon_top = """
### Replica retention and recall

```text
GET  /v1/replica-retention/postures
GET  /v1/replica-retention/postures/{retained_replica_posture_id}
POST /v1/replica-retention/reviews
GET  /v1/replica-retention/reviews/{replica_recall_review_id}
POST /v1/replica-retention/reviews/{replica_recall_review_id}/apply
GET  /v1/replica-retention/receipts
GET  /v1/replica-retention/receipts/{replica_recall_receipt_id}
```

These resources exist so clients can answer one ordinary operator question without disconnect/remove folklore:

- which peers still retain bytes for this share and in what form
- whether future updates stopped, retained copies were merely attested, or stronger delete/recall observation actually exists
- whether an encrypted or read-only retained replica still matters for reseed or disaster recovery
- which follow-up still depends on peer observation or an explicit remote-delete request

"""
daemon = daemon.replace('### Access\n', insert_daemon_top + '### Access\n', 1)
insert_daemon_detail = """
### Replica retention and recall reviews

```text
GET  /v1/replica-retention/postures
GET  /v1/replica-retention/postures/{retained_replica_posture_id}
POST /v1/replica-retention/reviews
GET  /v1/replica-retention/reviews/{replica_recall_review_id}
POST /v1/replica-retention/reviews/{replica_recall_review_id}/apply
GET  /v1/replica-retention/receipts
GET  /v1/replica-retention/receipts/{replica_recall_receipt_id}
```

A retained-replica-posture response should answer at least:

- peer or peer-set scope
- current authority posture and future-update posture
- retained byte posture (plaintext, encrypted-only, metadata-only, or unknown)
- whether the retained replica still matters for restore or reseed
- strongest honest recall verdict currently supported

A recall-review response should answer at least:

- requested boundary change and requested byte outcome
- which peers still retain bytes after apply
- whether the product is only proving future-stop or also requesting stronger recall/delete
- which recovery dependencies or preserved backup assumptions would still remain
- which observation or follow-up is still required for a stronger claim

Case creation should be preferred whenever an operator-visible action says `remove`, `disconnect`, `revoke`, or `retire` and already-retained bytes still matter.
Ordinary exit, authority-mutation, and disclosure endpoints may reference these resources, but they should not silently replace them when retained-copy truth is the main question.

"""
daemon = daemon.replace('### Access control and session boundaries\n', insert_daemon_detail + '### Access control and session boundaries\n')
write('docs/31-daemon-api-spec.md', daemon)

# --- interface flows ---
flows = read('docs/32-interface-flows.md')
flows += """

## Flow 129 — revoke future updates while honestly attesting that retained copies remain

Problem: a contractor laptop should stop receiving future changes to a share immediately, but the operator also wants the product to stay honest that the laptop already has materialized bytes and no remote-delete observation has occurred.

```text
$ anonsync replicas list --share designs
Peer: dev_contractor
Authority: write
Bytes: materialized
Future updates: active
Recall verdict: not-requested

$ anonsync recall prepare --share designs --peer dev_contractor --change revoke-future-updates --bytes attest-existing-copies --plan
Replica recall review: rcr_01PG...

Requested boundary change:
  action: revoke future updates
  byte outcome: attest existing copies

Current authority and byte reality:
  authority: write
  bytes: materialized
  recovery usefulness: ordinary collaborator, not required backup

Retained-copy and recovery findings:
  retained copies remain: yes
  remote delete requested: no
  stronger recall proof: none yet

Recall and observation posture:
  future updates -> will become revoked-pending-observation
  retained copy verdict -> retained-copy-confirmed

Admissible actions:
  - revoke future updates with retained-copy attestation
  - request remote delete as a separate follow-up
  - defer until quiet window if a receipt should include recent settlement proof

Receipt promise:
  rcrp_01PH... will prove future updates stopped and retained copies remained in scope

$ anonsync recall apply rcr_01PG...
Applied.
Receipt: rcrp_01PH...
```

What this proves:

- revoke and recall are rendered as different truths
- the operator sees that bytes remain even though future participation stops
- the receipt preserves the strongest honest claim instead of marketing `remove` as erasure

## Flow 130 — preserve an encrypted backup without pretending ordinary removal erased bytes

Problem: an encrypted backup peer should be removed from ordinary participation in a share migration, but the operator also needs to keep clear that encrypted bytes still exist there and may still matter for reseed if continuity material is preserved.

```text
$ anonsync replicas show enc_backup_1
Replica posture: rrp_01PI...
Authority: encrypted-readonly
Bytes: encrypted-materialized
Future updates: active
Recovery contribution: can-reseed-with-continuity-material
Recall verdict: not-requested

$ anonsync recall prepare --share ledger --peer enc_backup_1 --change narrow-authority --bytes retain-existing-copies --plan
Replica recall review: rcr_01PJ...

Requested boundary change:
  action: narrow authority / retire from ordinary participation
  byte outcome: retain existing copies

Current authority and byte reality:
  authority: encrypted-readonly
  bytes: encrypted-materialized
  recovery usefulness: can reseed if preserved continuity material remains available

Retained-copy and recovery findings:
  encrypted bytes remain: yes
  local decrypt capability on backup peer: no
  continuity dependency: preserved keys and compatible database lineage still required

Recall and observation posture:
  future updates -> frozen after apply
  retained storage verdict -> retained-copy-confirmed
  remote delete -> not requested

Admissible actions:
  - preserve encrypted backup and freeze future updates
  - replace backup first, then request stronger cleanup later
  - block if operator expectation is `erase all copies now`

Receipt promise:
  rcrp_01PK... will prove future participation changed while encrypted retained storage remained intentionally preserved
```

What this proves:

- backup preservation and byte recall are kept visibly separate
- the product exposes when an encrypted retained replica still matters for disaster recovery
- CLI and richer surfaces can tell the same honest story without drift
"""
write('docs/32-interface-flows.md', flows)

# --- workbench ---
wb = read('docs/38-operator-workbench-interface-spec.md')
insert_wb = """
## Retained copies and recall surface

The workbench should expose one dedicated surface whenever an operator changes access and also needs to know what already-delivered bytes still exist.
This page is not merely share membership hygiene.
It is where the product proves that `revoked`, `removed`, and `recalled` are not synonyms.

The page should show at least:

- known peers or peer sets retaining bytes for the share
- current authority posture and future-update posture for each one
- byte posture (`materialized`, `encrypted-only`, `metadata-only`, `unknown`)
- recovery usefulness and any continuity-material dependency
- current recall verdict and outstanding observation requirements
- recent recall receipts and retention attestations

Its primary actions should be:

- inspect retained replica posture
- prepare revoke-future-updates with retained-copy attestation
- prepare request-remote-delete as a stronger, separate action
- preserve encrypted backup while freezing ordinary participation
- inspect why a stronger recall claim is blocked or still unobserved

No action on this page should collapse into a generic `Remove`, `Disconnect`, or `Revoke` button without a report, plan, or receipt when retained-copy meaning is in scope.

"""
wb = wb.replace('## Identity and naming continuity page\n', insert_wb + '## Identity and naming continuity page\n')
write('docs/38-operator-workbench-interface-spec.md', wb)

# --- pattern language ---
pat = read('docs/39-interface-pattern-language.md')
insert_pat = """
## Pattern 22n — revocation and recall need one fixed retained-copy grammar

Every non-trivial recall review should render, in this order:

1. requested boundary change
2. current authority and byte reality
3. retained-copy and recovery findings
4. recall and observation posture
5. admissible actions
6. receipt promise

This matters because a product can define good exit, authority, and recovery objects on paper and still regress in practice if one client says `Removed` while another reveals that the peer still has bytes, or if one channel preserves encrypted backup truth while another implies ordinary erasure.
Headless and GUI surfaces need one retained-copy grammar, not one remove button and one support article.

"""
pat = pat.replace('## Pattern 23 — dangerous verbs should inherit the reviewed intent label\n', insert_pat + '## Pattern 23 — dangerous verbs should inherit the reviewed intent label\n')
pat = pat.replace('A reviewed share-layout case should not end with a generic `Show hidden files`, `Open Archive`, or `Clean temp files` button if the real action is `Migrate managed bytes to annex`, `Preserve legacy layout and inspect only`, or `Apply reviewed cleanup of metadata-carry residue`.\n', 'A reviewed share-layout case should not end with a generic `Show hidden files`, `Open Archive`, or `Clean temp files` button if the real action is `Migrate managed bytes to annex`, `Preserve legacy layout and inspect only`, or `Apply reviewed cleanup of metadata-carry residue`.\nA reviewed recall case should not end with a generic `Remove`, `Disconnect`, or `Revoke` button if the real action is `Stop future updates and attest retained copies`, `Preserve encrypted backup and freeze future updates`, or `Request remote delete and await observation`.\n')
write('docs/39-interface-pattern-language.md', pat)

# --- ADR ---
adr = read('docs/40-architecture-decisions.md')
adr += """


## ADR-087 — Revoke/remove language needs one reviewed retained-copy and recall contract, not disconnect folklore

**Decision:** Non-trivial access narrowing, replica retirement, or share-removal work should compile to one reviewed retained-replica/recall model rather than depending on disconnect notes, linked-device scope, or encrypted-backup caveats as the operator contract.

**Why:** Current Resilio docs still let `Disconnect` mean `future updates stop while bytes remain`, let linked-device removal say nothing about non-linked peers that already have the share, and let encrypted backup usefulness depend on saved keys and database continuity while ordinary read-only/archive behavior tells a different story. AnonSync should keep future authority, retained bytes, recovery usefulness, and stronger recall claims explicit.

**Consequences:**

- retained-copy truth gains a stable review grammar and receipt model
- workbench and CLI both need explicit byte-retention and recall-verdict sections before revoke/remove-style actions can apply honestly
- linked-surface cleanup can no longer masquerade as universal recall
- future access, exit, and backup-preservation work must distinguish future-stop, retained-copy attestation, delete request, and observed stronger recall
"""
write('docs/40-architecture-decisions.md', adr)

# --- roadmap ---
roadmap = read('docs/50-roadmap.md')
roadmap = roadmap.replace('- semantic-runtime-contract, semantic-optimization-review, and semantic-optimization-receipt object model\n', '- semantic-runtime-contract, semantic-optimization-review, and semantic-optimization-receipt object model\n- retained-replica-posture, replica-recall-review, and replica-recall-receipt object model\n')
roadmap = roadmap.replace('- operators can tell when a requested optimization or compatibility change would actually weaken freshness, rename continuity, diff behavior, or verification guarantees\n', '- operators can tell when a requested optimization or compatibility change would actually weaken freshness, rename continuity, diff behavior, or verification guarantees\n- operators can tell which peers still retain bytes, whether those bytes still matter for recovery, and what stronger recall claim is or is not currently proven\n')
roadmap = roadmap.replace('- explicit semantic-runtime / optimization / fallback surfaces that keep meaning-changing acceleration or degraded-target acceptance from hiding behind `performance` language\n', '- explicit semantic-runtime / optimization / fallback surfaces that keep meaning-changing acceleration or degraded-target acceptance from hiding behind `performance` language\n- explicit retained-replica / recall / attestation surfaces that keep future authority stop, retained-copy truth, encrypted-backup usefulness, and stronger delete/recalI claims visibly separate\n')
write('docs/50-roadmap.md', roadmap.replace('recalI', 'recall'))

# --- open questions ---
openq = read('docs/64-critical-open-questions.md')
openq += """


## 55) How much low-risk recall or retained-copy attestation can stay compressed before recall honesty becomes either noisy or too magical?

The archive is now clearer that future authority stop, retained-copy reality, encrypted-backup usefulness, and stronger recall claims should use first-class retained-replica reviews and receipts, but one policy seam remains open:

- when should an obvious `future updates stop only` case stay inline versus always opening the full recall sheet
- whether some encrypted-backup preservation actions may stay one-step while any remote-delete request always forces full reviewed recall
- how much automatic observation update is safe before the product starts hiding meaningful uncertainty about what peers still retain
- when repeated revoke/remove churn should escalate into broader authority, exit, or stewardship review because the share is no longer in an ordinary operating posture

This matters because weak defaults recreate disconnect/remove folklore, while overly strict defaults could make harmless collaborator offboarding feel ceremonial instead of trustworthy.
"""
write('docs/64-critical-open-questions.md', openq)

# --- sources (keep but ensure relevant docs visible only once if missing) ---
sources = read('docs/sources.md')
for entry in [
    '- User Management\n  https://help.resilio.com/hc/en-us/articles/205471375-User-Management\n',
    '- Disconnecting and Removing Folders\n  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders\n',
    '- Sync Private Identity & Linking My Devices\n  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices\n',
    '- Encrypted folders  \n  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders\n',
]:
    if entry not in sources:
        sources += '\n' + entry
write('docs/sources.md', sources)

print('updated rev0074 files')
