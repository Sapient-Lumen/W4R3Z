from pathlib import Path
import re

root = Path('/tmp/anonsync_work')

def read(path):
    return (root / path).read_text()

def write(path, text):
    (root / path).write_text(text)

# New doc 88
DOC88 = '''# Share authority epoch and stale-capability rotation spec

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
n- which peers have observed the new epoch and which are still unknown/offline
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
'''

write('docs/88-share-authority-epoch-and-stale-capability-rotation-spec.md', DOC88)

# 00-status
status = read('docs/00-status.md')
status = status.replace('`rev0073`', '`rev0074`')
status = status.replace('spend more time on interface specs rather than letting `disconnect`, `remove`, or `revoke` over-promise copy recall\n- keep Linux-first, overlay-first, and least-privilege assumptions intact unless evidence truly breaks them\n- keep turning support-lore seams into explicit product contracts\n- make sure the archive has a better reason not to clone current Resilio revocation/removal behavior as though stopping future updates were close enough to recalling already-delivered bytes\n- make sure future authority, retained copies, and stronger recall claims stay visibly separate',
'spend more time on interface specs rather than letting support-lore differences about key changes, share class, or re-share ritual stay implicit\n- keep Linux-first, overlay-first, and least-privilege assumptions intact unless evidence truly breaks them\n- keep turning support-lore seams into explicit product contracts\n- make sure the archive has a better reason not to clone current Resilio authority-rotation behavior as though issuing new authority means the old boundary stopped mattering everywhere at once\n- make sure future grant changes, old capability residue, mixed-epoch migration, and derivative/local-share fallout stay visibly separate')
status = status.replace('The archive now contains:\n\n- a deeper Resilio-derived warning that current revoke/disconnect/remove language still leaves retained-copy truth scattered across user-management, linked-device, and encrypted-backup articles\n- a dedicated **revocation, recall, and retained-copy attestation spec** that says what a real operator surface must show before revoking future updates, narrowing authority, preserving an encrypted backup, or requesting stronger recall\n- stronger interface and daemon/API requirements so retained-replica postures, recall reviews, and recall receipts become explicit public objects rather than support-lore side effects\n- stronger workbench and pattern-language rules so operators can see which peers still retain bytes, whether those bytes still matter for recovery, and what observation blocks any stronger claim\n- additional canonical flows for revoking future updates honestly and for preserving encrypted backup value without pretending ordinary removal erased bytes\n- roadmap, ADR, status, open-question, and README updates so future revisions keep retained-copy honesty explicit whenever access changes or replica retirement appears',
'The archive now contains:\n\n- a deeper Resilio-derived warning that current key-backed versus certificate-backed share behavior still leaves authority rotation truth scattered across folder-class, key-flow, and local-share articles\n- a dedicated **share authority epoch and stale-capability rotation spec** that says what a real operator surface must show before issuing new share authority, narrowing old authority, upgrading share class, or rebuilding derivative/local-share state\n- stronger interface and daemon/API requirements so share-authority epochs, rotation reviews, and rotation receipts become explicit public objects rather than support-lore side effects\n- stronger workbench and pattern-language rules so operators can see which old authority material still exists, which peers or offers still reference it, and what observation is required before claiming clean convergence\n- additional canonical flows for rotating a key-backed share without pretending the old swarm vanished and for upgrading authority class without pretending derivative/local-share migration is automatic\n- roadmap, ADR, status, open-question, and README updates so future revisions keep epoch truth explicit whenever reissue, rotation, or share-class changes appear')
status = status.replace('`rev0073` proved that performance and compatibility posture needed one explicit semantic-runtime contract rather than speed-oriented folklore.\n\n`rev0074` applies the same discipline one layer closer to everyday trust language itself:\n\n> a serious Linux-first workbench still is not specified tightly enough if the archive can define exits, authority mutation, recovery, and semantic downgrade honestly, yet still leave one ordinary operator question loose: when I revoke or remove a peer, what copies still remain, what can that peer still do with them, and what is the strongest honest recall claim I can make right now?\n\nThat changes the archive in six specific ways:\n\n- retained-copy truth now renders as its own reviewed contract instead of hiding behind `disconnect` or `remove`\n- linked-surface cleanup can no longer masquerade as universal recall\n- encrypted backup usefulness now has one explicit place to say whether preserved keys, database continuity, or read-only posture still matter\n- workbench and CLI now have one explicit place to compare future authority change against already-retained byte reality\n- the Resilio comparison now lands a sharper non-clone argument: the weak seam is not merely awkward wording, but the lack of one honest reviewed contract for retained-copy and recall claims\n- future access and exit work now has a narrower quality bar whenever revocation, backup preservation, or remote deletion are in scope',
'`rev0074` proved that revoke/remove language needed one explicit retained-copy contract rather than optimistic copy-recall wording.\n\n`rev0075` applies the same discipline one layer closer to share-authority evolution itself:\n\n> a serious Linux-first workbench still is not specified tightly enough if the archive can define exits, authority mutation, recall, and compromise honestly, yet still leave one ordinary operator question loose: when I issue new authority for a share, who still sits on the old authority, what old swarm or derivative state can still live, and what is the strongest honest convergence claim I can make right now?\n\nThat changes the archive in six specific ways:\n\n- share authority now renders as epoch-bearing public state instead of hiding behind `new key`, `re-share`, or `changed permissions` ritual\n- Standard/key-backed and Advanced/certificate-backed differences can no longer masquerade as implementation trivia when they materially change rotation or migration truth\n- mixed-epoch migration now has one explicit place to say whether old peers or artifacts still work, are quarantined, or are merely unknown/offline\n- workbench and CLI now have one explicit place to compare newly issued authority against stale capability residue and derivative/local-share fallout\n- the Resilio comparison now lands a sharper non-clone argument: the weak seam is not merely old terminology, but the lack of one honest reviewed contract for share-authority epoch change and convergence\n- future access, compromise, and share-class work now has a narrower quality bar whenever rotation, reissue, or old-capability retirement is in scope')
status = status.replace('- how much low-risk recall or retained-copy attestation may stay compressed before the product starts hiding meaningful byte-retention fallout behind harmless-looking revoke/remove affordances', '- how much low-risk recall or retained-copy attestation may stay compressed before the product starts hiding meaningful byte-retention fallout behind harmless-looking revoke/remove affordances\n- how much low-risk epoch rotation may stay compressed before the product starts hiding meaningful stale-capability fallout behind harmless-looking key-change, re-share, or share-upgrade affordances')
status = status.replace('- `docs/87-revocation-recall-and-retained-copy-attestation-spec.md`', '- `docs/88-share-authority-epoch-and-stale-capability-rotation-spec.md`')
status = status.replace('- `README.md`\n- `docs/00-status.md`\n- `docs/10-resilio-sync-evaluation.md`\n- `docs/30-interface-spec.md`\n- `docs/31-daemon-api-spec.md`\n- `docs/32-interface-flows.md`\n- `docs/38-operator-workbench-interface-spec.md`\n- `docs/39-interface-pattern-language.md`\n- `docs/40-architecture-decisions.md`\n- `docs/50-roadmap.md`\n- `docs/64-critical-open-questions.md`\n- `docs/87-revocation-recall-and-retained-copy-attestation-spec.md`', '- `README.md`\n- `docs/00-status.md`\n- `docs/10-resilio-sync-evaluation.md`\n- `docs/30-interface-spec.md`\n- `docs/31-daemon-api-spec.md`\n- `docs/32-interface-flows.md`\n- `docs/38-operator-workbench-interface-spec.md`\n- `docs/39-interface-pattern-language.md`\n- `docs/40-architecture-decisions.md`\n- `docs/50-roadmap.md`\n- `docs/64-critical-open-questions.md`\n- `docs/88-share-authority-epoch-and-stale-capability-rotation-spec.md`')
write('docs/00-status.md', status)

# README updates
readme = read('README.md')
readme = readme.replace('rev0074', 'rev0075', 1)
readme = readme.replace('2026.03.17.18.31', '2026.03.17.18.41', 1)
readme = readme.replace('recallproofretentionanchor', 'epochproofrotationharbor', 1)
readme = re.sub(r'This revision continues directly from `rev0073` and does seven things:\n\n1\.[\s\S]*?7\. Refreshes the \*\*evaluation\*\*, \*\*ADRs\*\*, \*\*roadmap\*\*, \*\*open questions\*\*, \*\*status\*\*, and \*\*reading order\*\* so future revisions keep retained-copy honesty explicit whenever access changes or replica retirement is in play\.',
'''This revision continues directly from `rev0074` and does seven things:\n\n1. Re-checks **Resilio Sync** again with extra emphasis on the share-authority rotation seam: current docs still distinguish key-backed, certificate-backed, and derivative/local-share behavior, but mostly through scattered support language rather than one operator contract.\n2. Sharpens the **non-clone rationale** into a stricter rule: AnonSync should not let `rotate`, `re-share`, or `change permissions` imply that old authority stopped mattering everywhere at once when the strongest honest claim is only `new epoch issued`.\n3. Adds a dedicated **share authority epoch and stale-capability rotation spec** so the archive now says what a real operator surface must literally show before issuing new share authority, upgrading share class, retiring old capability material, or rebuilding derivative/local-share state.\n4. Extends the **interface and daemon/API contract** with explicit share-authority epochs, rotation reviews, and rotation receipts rather than leaving mixed-epoch truth in peer memory and troubleshooting notes.\n5. Extends the **workbench/interface pattern language** so operators can see which old authority material still exists, which peers or offers still reference it, and what observation would be required for any stronger convergence claim.\n6. Adds additional **canonical interface flows** for rotating a key-backed share without pretending the old swarm vanished and for upgrading authority class without pretending derivative/local-share migration is automatic.\n7. Refreshes the **evaluation**, **ADRs**, **roadmap**, **open questions**, **status**, and **reading order** so future revisions keep epoch truth explicit whenever reissue, rotation, or share-class change is in play.''', readme, count=1)
readme = readme.replace('- a first-class retained-replica / recall / attestation surface so operators can tell who still holds bytes, whether those bytes are plaintext or encrypted-only, and whether any stronger recall claim has actually been observed\n', '- a first-class retained-replica / recall / attestation surface so operators can tell who still holds bytes, whether those bytes are plaintext or encrypted-only, and whether any stronger recall claim has actually been observed\n- a first-class share-authority epoch / rotation / stale-capability surface so operators can tell which authority generation is current, which older capability material still exists, whether mixed-epoch drift remains, and what derivative/local-share migration still blocks clean convergence\n')
readme = readme.replace('- `docs/87-revocation-recall-and-retained-copy-attestation-spec.md` — fixed recall-review anatomy for requested boundary change, current byte/authority reality, retained-copy findings, recall posture, and recall receipts\n', '- `docs/87-revocation-recall-and-retained-copy-attestation-spec.md` — fixed recall-review anatomy for requested boundary change, current byte/authority reality, retained-copy findings, recall posture, and recall receipts\n- `docs/88-share-authority-epoch-and-stale-capability-rotation-spec.md` — fixed epoch-rotation review anatomy for requested boundary change, current epoch map, stale-capability fallout, derivative migration, convergence posture, and rotation receipts\n')
readme = readme.replace('then `87-revocation-recall-and-retained-copy-attestation-spec.md`, then `41-report-and-intervention-language.md`', 'then `87-revocation-recall-and-retained-copy-attestation-spec.md`, then `88-share-authority-epoch-and-stale-capability-rotation-spec.md`, then `41-report-and-intervention-language.md`')
write('README.md', readme)

# evaluation add section
_eval = read('docs/10-resilio-sync-evaluation.md')
insert_after = """### Requirement 68 — non-trivial revocation and removal changes must share one reviewed retained-copy and recall contract\n\nIf the operator still has to combine disconnect notes, linked-device scope, encrypted-backup caveats, and peer memory to answer `who still has bytes from this share and what exactly did my revoke/remove action prove?`, the product has not actually exposed its recall truth.\n\nAnonSync should instead publish one public model with explicit retained-replica postures, explicit recall reviews, explicit byte-retention verdicts, explicit recovery-usefulness findings, and durable receipts that preserve the difference between future authority stop, retained-copy attestation, delete request, and observed stronger recall.\n"""
add_eval = """\n\n### 16ag) Authority rotation still splits trust epochs too quietly\n\nResilio's current docs expose one more seam that is easy to underestimate because the verbs look ordinary.\n`What's the difference between Standard and Advanced folders?` says Standard folders use randomly generated keys while Advanced folders use PKI/certificates, that Standard peers can share the key they have without the same bounded owner model, that on-the-fly permission changes are not possible for Standard folders, and that changing permissions means removing and re-adding the share with a new key. The same page says Standard folders cannot be converted into Advanced without removing and re-adding them.\n`Key structure and flow` then says a key change on one peer is not distributed automatically and that peers with the old key continue syncing with each other while no longer syncing with the peer who changed the key.\n`Sharing a folder locally` adds that some local-share permission changes also require remove-and-re-share ritual, that local-share access can be lowered by a remote owner, and that reconnecting a source share does not automatically reconnect the derived local share.\n\nThat is useful support knowledge.\nIt is not yet one public authority-rotation contract.\n\nThe practical consequence is that several different truths still blur together:\n\n- new authority was issued\n- old authority still exists and may still work\n- some peers moved to the new boundary while others remain on the old one\n- some derivatives or local shares must be rebuilt rather than mutated in place\n- some old portable artifacts or copied keys now point at superseded authority\n- the strongest honest claim may be only `mixed epoch`, not `everyone now uses the new boundary`\n\nIf the operator still has to remember that one share class supports live mutation, another requires re-share ritual, and a rotated key may leave an older peer set quietly syncing among itself, the interface is not explicit enough.\n\nAnonSync should instead publish one public authority-epoch model with:\n\n- explicit share-authority epochs and stale-capability postures\n- one reviewed epoch-rotation case whenever share authority material or share class changes non-trivially\n- one explicit difference between `new epoch issued`, `old epoch quarantined`, `mixed epoch`, and `observed new epoch only`\n- explicit derivative/local-share migration findings so reissue and rebuild obligations cannot masquerade as surprising exceptions\n- durable rotation receipts proving what authority became current, what stale material remained, and what convergence still depends on later observation\n\n### Requirement 69 — non-trivial share-authority changes must share one reviewed epoch-rotation and stale-capability contract\n\nIf the operator still has to combine folder-class caveats, key-flow notes, local-share exceptions, and re-share ritual to answer `which authority generation is actually current, what old capability still exists, and did the swarm converge to the new boundary yet?`, the product has not actually exposed its authority-rotation truth.\n\nAnonSync should instead publish one public model with explicit share-authority epochs, explicit rotation reviews, explicit stale-capability findings, explicit derivative migration findings, explicit convergence verdicts, and durable receipts that preserve the difference between newly issued authority, mixed-epoch migration, quarantined old authority, and observed clean convergence.\n"""
_eval = _eval.replace(insert_after, insert_after + add_eval)
_eval = _eval.replace('and explicit share-layout contracts that keep ordinary live files, managed control bytes, rollback/history retention, metadata-carry sidecars, and temp-transfer residue visibly separate instead of leaving the operator to learn `.sync`, `.sync/Archive`, `.sync/Streams`, and `.!sync` as cleanup folklore.', 'and explicit share-layout contracts that keep ordinary live files, managed control bytes, rollback/history retention, metadata-carry sidecars, and temp-transfer residue visibly separate instead of leaving the operator to learn `.sync`, `.sync/Archive`, `.sync/Streams`, and `.!sync` as cleanup folklore, and explicit authority-epoch contracts that keep newly issued share authority, stale capability residue, derivative/local-share migration, and mixed-epoch convergence visible instead of leaving key rotation, share upgrade, and re-share fallout to folder-class archaeology.')
write('docs/10-resilio-sync-evaluation.md', _eval)

# interface spec insert objects and CLI section
iface = read('docs/30-interface-spec.md')
obj_insert_after = """### Replica recall receipt\n\nA durable record proving what future authority changed and what retained-copy claim was honestly supported.\n\nFields:\n\n- `replica_recall_receipt_id`\n- `review_ref`\n- `share_ref`\n- `peer_summary`\n- `future_update_summary`\n- `retained_copy_summary`\n- `recovery_dependency_summary`\n- `observation_summary`\n- `actor_ref`\n- `created_at`\n- `provenance_ref` nullable\n"""
obj_add = """\n\n### Share authority epoch\n\nA durable record of one generation of share authority material.\nThis exists so operators do not have to guess whether `rotated`, `re-shared`, `upgraded`, and `changed permissions` all describe the same trust reality.\n\nFields:\n\n- `share_authority_epoch_id`\n- `share_ref`\n- `epoch_handle`\n- `authority_class` (`key-backed`, `certificate-backed`, `derived-local`, `encrypted-derivative`, `unknown-legacy`)\n- `status` (`current`, `superseded`, `quarantined`, `retired-observed`, `unknown-offline`)\n- `issued_from_epoch_ref` nullable\n- `peer_refs[]`\n- `offer_refs[]`\n- `derivative_refs[]`\n- `grant_refs[]`\n- `stale_capability_posture` (`none-known`, `artifact-only`, `still-redeemable`, `live-peer-set`, `unknown-offline`)\n- `convergence_verdict` (`not-started`, `new-epoch-issued`, `mixed-epoch`, `old-epoch-quarantined`, `observed-new-epoch-only`, `unknown-offline`)\n- `issued_at`\n- `last_observed_at` nullable\n- `provenance_ref` nullable\n\n### Epoch rotation review\n\nA reviewed case for changing share authority material or share class without lying about old capability residue or mixed-epoch drift.\nThis exists so `rotate`, `re-share`, and `upgrade share` do not collapse into a reassuring but incomplete one-liner.\n\nFields:\n\n- `epoch_rotation_review_id`\n- `share_ref`\n- `current_epoch_ref`\n- `prior_epoch_refs[]`\n- `requested_change_class` (`rotate-authority-material`, `narrow-share-authority`, `upgrade-share-class`, `reissue-derived-scope`, `inspect-only`)\n- `requested_outcome` (`issue-new-epoch`, `retire-old-epoch`, `quarantine-old-epoch`, `upgrade-authority-class`, `inspect-only`)\n- `stale_capability_findings[]`\n- `derivative_migration_findings[]`\n- `convergence_requirements[]`\n- `follow_on_review_refs[]`\n- `action_options[]`\n- `epoch_rotation_report_ref`\n- `generated_at`\n- `expires_at` nullable\n\n### Epoch rotation receipt\n\nA durable record proving which authority epoch became current, what older capability residue remained, and what convergence was actually observed.\n\nFields:\n\n- `epoch_rotation_receipt_id`\n- `review_ref`\n- `share_ref`\n- `current_epoch_summary`\n- `superseded_epoch_summary`\n- `stale_capability_summary`\n- `derivative_migration_summary`\n- `convergence_summary`\n- `actor_ref`\n- `created_at`\n- `provenance_ref` nullable\n"""
iface = iface.replace(obj_insert_after, obj_insert_after + obj_add)
cli_insert_after = """### Replica recall and retained-copy review\n\n```text\nanonsync recall prepare --share shr_01J... --peer peer:dev_01J... --change revoke-future-updates --bytes attest-existing-copies --plan\nanonsync recall prepare --share shr_01J... --peer-set linked:family --change retire-linked-presence --bytes future-stop-only --plan\nanonsync recall show rcr_01J...\nanonsync recall apply rcr_01J...\nanonsync recall receipt show rcrp_01J...\n```\n\nInspect and mutate retained-copy posture without pretending that revoking future participation and recalling already-delivered bytes are the same thing.\n"""
cli_add = """\n\n### Share authority epochs and rotation\n\n```text\nanonsync epochs list --share shr_01J...\nanonsync epochs show sae_01J...\nanonsync rotate prepare --share shr_01J... --change rotate-authority-material --outcome issue-new-epoch --plan\nanonsync rotate prepare --share shr_01J... --change upgrade-share-class --outcome upgrade-authority-class --plan\nanonsync rotate show err_01J...\nanonsync rotate apply err_01J...\nanonsync rotate receipt show errc_01J...\n```\n\nInspect and mutate share authority without pretending that newly issued authority, stale capability residue, derivative migration, and clean convergence are the same thing.\n"""
iface = iface.replace(cli_insert_after, cli_insert_after + cli_add)
write('docs/30-interface-spec.md', iface)

# daemon api
api = read('docs/31-daemon-api-spec.md')
api_insert_after = """### Replica retention and recall\n\n```text\nGET  /v1/replica-retention/postures\nGET  /v1/replica-retention/postures/{retained_replica_posture_id}\nPOST /v1/replica-retention/reviews\nGET  /v1/replica-retention/reviews/{replica_recall_review_id}\nPOST /v1/replica-retention/reviews/{replica_recall_review_id}/apply\nGET  /v1/replica-retention/receipts\nGET  /v1/replica-retention/receipts/{replica_recall_receipt_id}\n```\n\nThese resources exist so clients can answer one ordinary operator question without disconnect/remove folklore:\n\n- which peers still retain bytes for this share and in what form\n- whether future updates stopped, retained copies were merely attested, or stronger delete/recall observation actually exists\n- whether an encrypted or read-only retained replica still matters for reseed or disaster recovery\n- which follow-up still depends on peer observation or an explicit remote-delete request\n"""
api_add = """\n\n### Share authority epochs and rotation\n\n```text\nGET  /v1/authority-epochs\nGET  /v1/authority-epochs/{share_authority_epoch_id}\nPOST /v1/authority-rotation/reviews\nGET  /v1/authority-rotation/reviews/{epoch_rotation_review_id}\nPOST /v1/authority-rotation/reviews/{epoch_rotation_review_id}/apply\nGET  /v1/authority-rotation/receipts\nGET  /v1/authority-rotation/receipts/{epoch_rotation_receipt_id}\n```\n\nThese resources exist so clients can answer one ordinary operator question without key-change/re-share folklore:\n\n- which authority epoch is current for this share and which older epoch handles still remain in scope\n- whether old capability material is artifact-only residue, still redeemable, or still backing a live older peer set\n- which derivative/local-share or downstream migration obligations still block clean convergence\n- whether the strongest honest statement is merely `new epoch issued` or the stronger `observed new epoch only`\n"""
api = api.replace(api_insert_after, api_insert_after + api_add)
write('docs/31-daemon-api-spec.md', api)

# flows append
flows = read('docs/32-interface-flows.md')
flows += """\n\n## Flow 131 — rotate a key-backed share without pretending the old swarm vanished\n\nProblem: a key-backed collaborator share needs a tighter boundary, so the operator issues new authority material. The product should show that this created a new epoch but does not yet prove that every old-key peer stopped syncing among itself.\n\n```text\n$ anonsync epochs list --share finance\nCurrent epoch: sae_01PL...\nAuthority class: key-backed\nConvergence verdict: observed-new-epoch-only not yet available\n\n$ anonsync rotate prepare --share finance --change rotate-authority-material --outcome issue-new-epoch --plan\nEpoch rotation review: err_01PM...\n\nRequested boundary change:\n  action: rotate share authority material\n  requested outcome: issue new epoch\n\nCurrent epoch map:\n  current epoch: sae_01PL... (key-backed)\n  prior epochs still known: none retired-observed\n  peers on current epoch: acct_desktop, acct_laptop, ext_bookkeeper\n\nStale-capability fallout:\n  old copied key may still exist after apply: yes\n  mixed-epoch risk after apply: yes until peers are re-admitted or observed retired\n  strongest immediate claim: new epoch issued\n\nDerivative and migration obligations:\n  local derivatives: none\n  downstream grants/offers to reissue: 2\n\nConvergence and observation posture:\n  post-apply verdict -> mixed-epoch\n  stronger verdict `observed-new-epoch-only` requires later peer observation\n\nReceipt promise:\n  errc_01PN... will prove new epoch issuance and mixed-epoch follow-up requirements\n\n$ anonsync rotate apply err_01PM...\nApplied.\nReceipt: errc_01PN...\n```\n\nWhat this proves:\n\n- issuing new authority and converging on it are rendered as different truths\n- the operator sees stale-capability residue before assuming the old swarm disappeared\n- the receipt preserves the honest mixed-epoch story instead of marketing `rotated` as complete retirement\n\n## Flow 132 — upgrade authority class without pretending derivative/local-share migration is automatic\n\nProblem: a share should move from a weaker/key-style boundary to a stronger/certificate-backed authority model, but the product also needs to show that some derivative/local-share state must be rebuilt or reissued rather than mutated in place.\n\n```text\n$ anonsync epochs show sae_01PQ...\nShare: media\nAuthority class: key-backed\nDerivatives referencing epoch: ldr_01PR...\nConvergence verdict: current\n\n$ anonsync rotate prepare --share media --change upgrade-share-class --outcome upgrade-authority-class --plan\nEpoch rotation review: err_01PS...\n\nRequested boundary change:\n  action: upgrade share authority class\n  requested outcome: certificate-backed current epoch\n\nCurrent epoch map:\n  current epoch: sae_01PQ... (key-backed)\n  proposed epoch class: certificate-backed\n\nStale-capability fallout:\n  legacy offers/keys become superseded after apply: yes\n  old artifact residue must remain visible until retired or expired: yes\n\nDerivative and migration obligations:\n  local derivative ldr_01PR... cannot mutate in place\n  required follow-on: reissue derivative against new epoch\n  local-share continuity: data path may remain, authority lineage changes\n\nConvergence and observation posture:\n  post-apply verdict -> new-epoch-issued\n  stronger verdict `observed-new-epoch-only` blocked by unfinished derivative migration\n\nReceipt promise:\n  errc_01PT... will prove authority-class upgrade and outstanding derivative migration\n```\n\nWhat this proves:\n\n- share-class upgrade and derivative migration are rendered as different actions\n- the product exposes when local-share fallout is a real boundary change rather than an implementation quirk\n- CLI and richer surfaces can tell the same honest epoch story without drift\n"""
write('docs/32-interface-flows.md', flows)

# workbench add surface
wb = read('docs/38-operator-workbench-interface-spec.md')
wb_insert_after = """## Retained copies and recall surface\n\nThe workbench should expose one dedicated surface whenever an operator changes access and also needs to know what already-delivered bytes still exist.\nThis page is not merely share membership hygiene.\nIt is where the product proves that `revoked`, `removed`, and `recalled` are not synonyms.\n\nThe page should show at least:\n\n- known peers or peer sets retaining bytes for the share\n- current authority posture and future-update posture for each one\n- byte posture (`materialized`, `encrypted-only`, `metadata-only`, `unknown`)\n- recovery usefulness and any continuity-material dependency\n- current recall verdict and outstanding observation requirements\n- recent recall receipts and retention attestations\n\nIts primary actions should be:\n\n- inspect retained replica posture\n- prepare revoke-future-updates with retained-copy attestation\n- prepare request-remote-delete as a stronger, separate action\n- preserve encrypted backup while freezing ordinary participation\n- inspect why a stronger recall claim is blocked or still unobserved\n\nNo action on this page should collapse into a generic `Remove`, `Disconnect`, or `Revoke` button without a report, plan, or receipt when retained-copy meaning is in scope.\n"""
wb_add = """\n\n## Share authority epochs and rotation surface\n\nThe workbench should expose one dedicated surface whenever share authority material changes or is about to change.\nThis page is not merely about `new key` or `re-share`.\nIt is where the product proves that `new epoch issued`, `old authority still exists`, `mixed epoch`, and `clean convergence` are not synonyms.\n\nThe page should show at least:\n\n- current share-authority epoch and prior known epochs\n- authority class for each epoch and current status\n- peers, offers, and derivatives still referencing each epoch\n- stale-capability posture and convergence verdict\n- derivative/local-share migration obligations and follow-on reviews\n- recent rotation receipts and any blocked retirement/quarantine follow-up\n\nIts primary actions should be:\n\n- inspect current epoch map\n- prepare rotate-authority-material\n- prepare upgrade-share-class\n- inspect why stale capability cannot yet be retired\n- inspect which derivatives or downstream offers still need reissue\n\nNo action on this page should collapse into `Rotate`, `Re-share`, or `Upgrade` without a report, plan, or receipt when mixed-epoch or stale-capability meaning is in scope.\n"""
wb = wb.replace(wb_insert_after, wb_insert_after + wb_add)
write('docs/38-operator-workbench-interface-spec.md', wb)

# pattern add new pattern
pattern = read('docs/39-interface-pattern-language.md')
pattern += """\n\n## Pattern 22o — authority rotation needs one fixed epoch grammar\n\nEvery non-trivial epoch-rotation review should render, in this order:\n\n1. requested boundary change\n2. current epoch map\n3. stale-capability fallout\n4. derivative and migration obligations\n5. convergence and observation posture\n6. receipt promise\n\nHeadless and GUI surfaces need one epoch grammar, not one `Rotate key` button and one folder-class FAQ.\n\nThis matters because a product can define good offers, grants, compromise cases, and recall objects on paper and still regress in practice if one client offers a rich epoch sheet while another falls back to `re-share`, `use a new key`, or `upgrade share` folklore.\n\nA reviewed epoch-rotation case should not end with a generic `Rotate`, `Re-share`, or `Upgrade` button if the real action is `Issue new epoch but old capability remains`, `Quarantine old authority and wait for observation`, or `Upgrade authority class but rebuild derivative/local-share state separately`.\n"""
write('docs/39-interface-pattern-language.md', pattern)

# ADR add
adr = read('docs/40-architecture-decisions.md')
adr += """\n\n## ADR-088 — Share-authority change needs one reviewed epoch-rotation contract, not key/re-share folklore\n\n**Decision:** Non-trivial share-authority changes should compile to one reviewed authority-epoch model rather than depending on folder-class caveats, key-change notes, or derivative/local-share re-share ritual as the operator contract.\n\n**Why:** Current Resilio docs still let Standard/key-backed and Advanced/certificate-backed shares behave materially differently for permission mutation and reissue, still say key changes do not propagate automatically, and still require remove-and-re-share in some derivative/local-share cases. AnonSync should keep new authority issuance, stale capability residue, derivative migration, and mixed-epoch convergence explicit.\n\n**Implications:**\n\n- share authority gains stable epoch objects, rotation reviews, and rotation receipts\n- workbench and CLI both need explicit epoch maps, stale-capability findings, and convergence verdicts before rotation-style actions can apply honestly\n- derivative/local-share fallout can no longer masquerade as implementation trivia when it changes what must be rebuilt or reissued\n- future compromise, recall, and share-class work must distinguish new-epoch issuance from observed clean retirement of old authority\n"""
write('docs/40-architecture-decisions.md', adr)

# roadmap update
road = read('docs/50-roadmap.md')
road = road.replace('- retained-replica-posture, replica-recall-review, and replica-recall-receipt object model\n', '- retained-replica-posture, replica-recall-review, and replica-recall-receipt object model\n- share-authority-epoch, epoch-rotation-review, and epoch-rotation-receipt object model\n')
road = road.replace('- operators can tell which peers still retain bytes, whether those bytes still matter for recovery, and what stronger recall claim is or is not currently proven\n', '- operators can tell which peers still retain bytes, whether those bytes still matter for recovery, and what stronger recall claim is or is not currently proven\n- operators can tell which authority generation is current for a share, what older capability residue still remains, and whether the strongest honest statement is mixed-epoch migration or observed clean convergence\n')
road = road.replace('- explicit retained-replica / recall / attestation surfaces that keep future authority stop, retained-copy truth, encrypted-backup usefulness, and stronger delete/recall claims visibly separate\n', '- explicit retained-replica / recall / attestation surfaces that keep future authority stop, retained-copy truth, encrypted-backup usefulness, and stronger delete/recall claims visibly separate\n- explicit authority-epoch / rotation / stale-capability surfaces that keep newly issued share authority, old capability residue, derivative/local-share migration, and convergence truth visibly separate\n')
road = road.replace('- operators can inspect what a portable artifact actually offers before sending or consuming it, and can later prove consumption from claim receipts\n', '- operators can inspect what a portable artifact actually offers before sending or consuming it, and can later prove consumption from claim receipts\n- operators can rotate or upgrade share authority without guessing whether old capability material still exists or whether the swarm actually converged to the new boundary\n')
write('docs/50-roadmap.md', road)

# open questions add 56
openq = read('docs/64-critical-open-questions.md')
openq += """\n\n## 56) How much low-risk epoch rotation can stay compressed before authority-convergence honesty becomes either noisy or too magical?\n\nThe archive is now clearer that new share authority issuance, stale capability residue, derivative/local-share migration, and mixed-epoch convergence should use first-class epoch-rotation reviews and receipts, but one policy seam remains open:\n\n- when should an obvious same-class reissue stay inline versus always opening the full epoch sheet\n- whether any stale-capability residue should always force full review or whether artifact-only residue may stay lightly compressed\n- how much automatic derivative/local-share migration help is safe before the product starts hiding meaningful rebuild or reissue obligations\n- when repeated mixed-epoch drift should escalate into broader compromise, recall, or stewardship review because the share is no longer in an ordinary operating posture\n\nThis matters because weak defaults recreate key-change, re-share, and folder-class folklore, while overly strict defaults could make harmless bounded reissue feel ceremonial instead of trustworthy.\n"""
write('docs/64-critical-open-questions.md', openq)

# sources: no change needed maybe maintain. but add note if absent. ensure source titles present once maybe not.
# interface reading order and docs list already in README.

# append doc to sources list? optional no.

# README docs listing maybe enough.

# Add source if not present (guard)
sources = read('docs/sources.md')
if 'Sharing a folder locally' not in sources:
    sources += '\n- Sharing a folder locally\n  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally\n'
write('docs/sources.md', sources)
