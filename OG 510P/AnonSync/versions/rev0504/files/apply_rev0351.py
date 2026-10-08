from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / 'docs'

files = {
'1246-resilio-detachment-revocation-roster-residue-and-visibility-fragmentation-evaluation.md': r'''# Resilio detachment, revocation, roster-residue, and visibility fragmentation evaluation

## What current official docs still make clear

Another current Resilio pass strengthens the archive's clone-veto line rather than weakening it.

Current official docs still say several things that are operationally real and worth borrowing:

- clearing an offline device from **My Devices** does not unlink it; it only hides the record, and if that device comes back online it reappears
- unlinking a device is a local action that severs its links to other peers, and the docs explicitly say you cannot remotely unlink other devices
- disconnecting a folder is a one-device detachment: the folder remains in the file system, placeholders may be removed, and the folder can later be reconnected
- removing a folder is broader for linked devices, but the same content may still exist on remote devices that are not linked to your personal identity
- peer-level `Disconnect` in **User Management** revokes access for that selected peer going forward, but the bytes already synchronized to that peer stay in the folder
- uninstall guidance says unlinking and removing shares first is optional but otherwise the dead installation may continue showing up as an offline peer or device record; uninstall also leaves filesystem content and `.sync`/Archive residue unless cleared manually
- linking two devices that already have different certificates can cause one device to lose its certificate and have Advanced folders removed from the app without ordinary filesystem deletion, except on iOS where those Advanced folders are deleted from the file system

That is real candor.
It is useful product truth.

## What still should not be cloned

The operator is still asked to reconstruct several materially different questions from several different pages:

1. **did I only hide a record, or did I really sever future trust?**
2. **did I only stop future updates, or did I also remove bytes already present?**
3. **is this detachment local-only, linked-family-wide, or still ineffective against unlinked remote peers?**
4. **can this record come back on its own later?**
5. **what residue remains in storage, rosters, and remote possession after this action?**

Current Resilio docs still spread those answers across identity, folder management, user management, and uninstall guidance.

So a user can learn all the pieces and still not get one stable product answer to:

> after I hide, disconnect, remove, revoke, unlink, or uninstall, who still has access, what bytes still exist, which records can reappear, and what stronger cleanup sentence is still blocked?

That page-contract gap is exactly why AnonSync should not clone the behavior.

## Why this matters for AnonSync

AnonSync should borrow four habits directly:

- **say openly whether an action changes only visibility, future authority, byte residency, or all three**
- **say openly whether a remote record can reappear without another explicit approval step**
- **say openly when revocation stops future convergence but cannot retract already-landed bytes**
- **say openly when uninstall or unlink leaves roster or storage residue behind**

But AnonSync should reject five weaker habits:

- `Hide`, `Disconnect`, `Remove`, `Unlink`, and `Uninstall` actions that do not emit one effective detachment sentence
- revocation language that hides the difference between future-update suspension and byte retraction
- linked-family removal language that hides surviving unlinked remote peers
- cleanup flows that treat roster residue and storage residue as the same thing
- stale-record actions that suppress clutter while sounding stronger than the evidence allows

## Replacement pages added for this seam

This revision therefore adds six narrower replacement pages:

- `1247` — Detachment and revocation contract sheet
- `1248` — Offline roster visibility review
- `1249` — Access revocation proof
- `1250` — Installation clearance review
- `1251` — Detachment lineage receipt

These pages keep the Resilio candor and reject the scattered-detachment-contract problem.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that `hide`, `disconnect`, `remove`, `unlink`, `peer disconnect`, and `uninstall` are different truths; refuse any interface contract where the operator must reconstruct visibility change, future-update cutoff, byte residue, roster afterlife, and remote survivor scope from several separate help articles instead of one explicit detachment object.
''',
'1247-detachment-and-revocation-contract-sheet-page-action-class-authority-scope-and-residue-interface-spec.md': r'''# Detachment and revocation contract sheet page: action class, authority scope, and residue interface spec

## Purpose

The archive already has pages for seat posture, reachability provenance, operator attestation, and presence.
What it still lacked was one ordinary page for the narrower question:

> when an operator clicks hide, disconnect, remove, unlink, revoke, or uninstall, what exactly changes in authority, visibility, byte residency, and roster residue?

Current official Resilio docs make this seam concrete.
They separately describe hiding offline devices, disconnecting folders, removing folders from linked devices, peer-level revocation, self-unlinking, and uninstall cleanup residue.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Detachment and revocation contract sheet** whenever an action materially changes a relationship between a seat, a subject, and a roster record.

The sheet exists to answer six things in one place:

1. what detachment or revocation class is being performed
2. who has authority to perform it
3. what future updates or approvals it actually cuts off
4. what bytes or placeholders remain after the action
5. what roster or storage residue survives
6. what stronger sentence remains blocked

## Fixed page order

1. **Detachment header**
2. **Authority and scope card**
3. **Future-update boundary card**
4. **Residue card**
5. **Reappearance / reactivation card**
6. **Commit rail and blocked stronger sentence**

### 1) Detachment header

Show at minimum:

- `detachment_contract_id`
- actor handle
- subject ref or peer ref
- action class
- scope (`record-only`, `single-seat`, `selected-peer`, `linked-family`, `installation`, `identity`, `unknown`)
- strongest safe sentence
- stronger blocked sentence
- freshness of latest roster and byte observations

Supported action classes must include:

- `hide-roster-record`
- `disconnect-local-subject`
- `revoke-selected-peer-updates`
- `remove-linked-family-subject`
- `unlink-local-seat-from-identity`
- `uninstall-runtime`
- `certificate-takeover-rebind`

Example safe sentence:

- `Selected peer is cut off from future updates, but previously landed bytes remain outside this action's reach.`

### 2) Authority and scope card

Separate explicitly:

- who can perform the action
- what object is targeted
- whether the action is local-only or propagating
- whether it operates through identity membership, folder membership, or installation presence
- whether offline peers are still affected later

The operator must be able to answer:

> whose authority is this, and over what boundary does it actually apply?

### 3) Future-update boundary card

Show one row for each affected class:

- future metadata announcements
- future byte transfer
- future approval rights
- future appearance in linked-device rosters
- future automatic reconnect / rediscovery

Each row must show:

- `continues`
- `suspended`
- `revoked`
- `unknown`

The operator must be able to answer:

> what stops happening after this action, and what still can happen?

### 4) Residue card

Separate these residue classes explicitly:

- ordinary local bytes
- placeholder residue
- archive/service residue
- peer-list / device-list record residue
- remote-byte survivor scope
- identity / certificate residue

Each row must show whether the residue is preserved, removed, hidden, or not yet observed.

The operator must be able to answer:

> what is still around after the action, even if the UI looks cleaner?

### 5) Reappearance / reactivation card

This card must show whether the object can come back and how:

- cleared record reappears when the same device goes online again
- disconnected folder reconnects to the same or a new path
- removed linked-family folder survives on unlinked remote peers
- unlinked or uninstalled seat may remain as stale roster evidence elsewhere
- certificate takeover may replace app-visible objects without proving byte deletion

The operator must be able to answer:

> can this come back, and does that require a new explicit grant?

### 6) Commit rail and blocked stronger sentence

Allowed examples:

- `Hide stale roster record`
- `Disconnect local subject only`
- `Revoke selected peer from future updates`
- `Remove from linked family`
- `Unlink local seat`
- `Begin uninstall with residue review`
- `Export detachment receipt`

Blocked examples:

- `No one has the bytes anymore.`
- `This peer can never reappear.`
- `All access everywhere is revoked.`
- `Uninstall cleared every trace.`

## What this page prevents

Without this page, the product quietly conflates decluttering, future-update suspension, byte removal, and trust severance.
AnonSync must instead publish one effective detachment sentence with one visible claim ceiling.
''',
'1248-offline-roster-visibility-review-page-hide-clear-reappear-and-observation-ceiling-interface-spec.md': r'''# Offline roster visibility review page: hide, clear, reappear, and observation ceiling interface spec

This page exists so `offline`, `hidden`, and `gone` stop pretending to mean the same thing.
The operator often wants a cleaner roster, but that is not the same as unlinking a seat or proving it no longer matters.

## Operator question

> did we actually sever this relationship, or did we only suppress its record from view until it shows up again?

## When this page must appear

Render whenever the product is about to:

- hide or clear an offline peer or device record
- infer that a silent seat is irrelevant now
- promise that the roster is clean after uninstall or unlink
- down-rank an old peer observation
- merge multiple stale records into one visible summary

## Fixed page order

1. **Current record verdict**
2. **Observation basis**
3. **Reappearance triggers**
4. **Roster-trust ceiling**
5. **Blocked stronger sentence**

## 1) Current record verdict

Show one verdict:

- `offline record remains visible`
- `offline record hidden from ordinary view`
- `record removed from this roster scope`
- `record lineage unresolved`
- `record may still persist on remote rosters`

The operator must be able to answer: **what happened to the record, not just the device?**

## 2) Observation basis

Possible observation classes include:

- last successful online witness
- roster-only stale record
- uninstall cleanup declaration
- self-unlink witness
- remote revocation witness
- no recent corroboration

Each row must show freshness, scope, and whether it supports only decluttering or an actual trust change.

## 3) Reappearance triggers

Show possible return paths such as:

- same device comes online again
- same identity resumes announcements
- stale record imported from another linked seat
- manual reconnect or relink
- unresolved duplicate-seat / successor-seat ambiguity

Each trigger row must show whether it needs new approval, old standing approval, or unknown approval basis.

## 4) Roster-trust ceiling

Publish separate ceilings for:

- visual absence
- identity severance
- byte irrelevance
- permission irrelevance
- historical evidence retention

Examples:

- a hidden record may still have standing approval history
- a removed linked-family record may still correspond to a remote peer with local bytes
- a roster that looks clean may still be missing cross-seat corroboration

## 5) Blocked stronger sentence

Allowed examples:

- `This offline record was hidden from view only.`
- `No recent witness proves the device still participates.`
- `The record can reappear if the same device resumes announcements.`

Blocked examples:

- `The device no longer exists.`
- `This relationship is fully severed everywhere.`
- `The absence of a row proves the absence of a peer.`

## Main actions

Examples:

- `Hide clutter only`
- `Escalate to unlink / revoke review`
- `Compare remote rosters`
- `Export roster-visibility receipt`
''',
'1249-access-revocation-proof-page-disconnect-unlink-remove-and-future-update-boundary-interface-spec.md': r'''# Access revocation proof page: disconnect, unlink, remove, and future-update boundary interface spec

This page exists so `disconnected`, `revoked`, `removed`, and `unlinked` stop laundering different consequences through one action verb.
A serious operator needs to know not just that a relationship changed, but **which future rights ended and which already-landed state survived**.

## Operator question

> whose future access or convergence was actually cut off, and what bytes or rights were already beyond the reach of this action?

## When this page must appear

Render whenever the product is about to:

- revoke a selected peer from a subject
- disconnect a subject from one seat
- remove a subject from linked-family management
- unlink a seat from an identity
- describe why an apparently removed peer still has data
- describe why a future update stopped while local bytes stayed present

## Fixed page order

1. **Revocation verdict**
2. **Rights matrix**
3. **Survivor matrix**
4. **Propagation boundary**
5. **Blocked stronger sentence**

## 1) Revocation verdict

Show one verdict:

- `future updates suspended for selected peer`
- `local seat detached from subject`
- `linked-family management removed`
- `local seat unlinked from identity`
- `revocation claim unproved`

The operator must be able to answer: **what future channel was cut, and for whom?**

## 2) Rights matrix

Separate these rights explicitly:

- receive future metadata
- receive future bytes
- publish future mutations
- onward-share or approve
- appear in linked-device family
- reconnect without fresh grant

Each right must show:

- `still allowed`
- `stopped by this action`
- `outside action scope`
- `unknown`

## 3) Survivor matrix

Separate these survivor classes explicitly:

- bytes already present on remote peer
- local placeholders and directory names
- archive/service history
- standing approval memory
- remote independent copies outside linked family

This matrix exists so the operator can see the difference between **future flow cutoff** and **historical survivor residue**.

## 4) Propagation boundary

Show where the action does and does not travel:

- only this seat
- selected remote peer only
- all seats in linked family
- unlinked remote peers excluded
- filesystem bytes out of scope
- remote deletion out of scope unless separately issued

## 5) Blocked stronger sentence

Allowed examples:

- `Selected peer will not receive future updates for this subject.`
- `Local seat is detached, but the subject still exists on other linked seats.`
- `Previously synchronized bytes remain outside the scope of this revocation.`

Blocked examples:

- `No remote copy remains.`
- `Every approval everywhere was revoked.`
- `This subject is gone from the ecosystem.`

## Main actions

Examples:

- `Confirm revocation boundary`
- `Inspect survivor scope`
- `Escalate to destructive removal review`
- `Export revocation proof`
''',
'1250-installation-clearance-review-page-uninstall-storage-residue-and-peer-record-afterlife-interface-spec.md': r'''# Installation clearance review page: uninstall, storage residue, and peer-record afterlife interface spec

This page exists so `uninstalled` stops pretending to mean `forgotten`, `deleted`, or `cleaned up everywhere`.
For a sync product, removing the program binary is only one slice of the lifecycle.

## Operator question

> after uninstall or teardown, what survives in storage, in rosters, in archives, and in remote memory of this seat?

## When this page must appear

Render whenever the product is about to:

- uninstall or purge an installation
- retire a service runtime
- claim that a seat is gone
- guide manual deletion of storage roots or service residue
- explain why a dead installation still appears offline elsewhere

## Fixed page order

1. **Clearance verdict**
2. **Program vs state split**
3. **Storage residue inventory**
4. **Roster afterlife review**
5. **Blocked stronger sentence**

## 1) Clearance verdict

Show one verdict:

- `program removed only`
- `program removed and local state retained`
- `program removed and local state purged`
- `installation retired but peer records may persist`
- `clearance claim incomplete`

The operator must be able to answer: **what was actually cleared?**

## 2) Program vs state split

Separate these classes explicitly:

- executable / package files
- settings / storage roots
- `.sync` and archive/service residue
- shell / service helper residue
- local synced folder bytes
- mobile platform device-file exceptions

The operator must be able to answer:

> what disappeared with uninstall, and what required a separate cleanup step?

## 3) Storage residue inventory

For each residue row show:

- path or object class
- still present / manually removed / unknown
- contains ordinary data, metadata, archive versions, or service state
- safe-to-delete basis or missing proof

## 4) Roster afterlife review

Show how the retired seat may still survive elsewhere:

- linked-device list still shows offline record
- peer list still has stale row until cleanup or timeout-equivalent review
- remote seats may still remember approvals or historic presence
- remote bytes and archives remain outside uninstall scope

## 5) Blocked stronger sentence

Allowed examples:

- `The application was removed, but synced folders remain in the file system.`
- `Archive residue still existed until manually cleared.`
- `Other peers may still display this seat as offline until roster cleanup.`

Blocked examples:

- `Uninstall erased all traces.`
- `No remote seat remembers this installation.`
- `All synchronized data was removed.`

## Main actions

Examples:

- `Review leftover state paths`
- `Review stale roster records`
- `Confirm manual archive clearance`
- `Export installation-clearance receipt`
''',
'1251-detachment-lineage-receipt-page-action-authority-residue-and-blocked-stronger-sentences-interface-spec.md': r'''# Detachment lineage receipt page: action, authority, residue, and blocked stronger sentences interface spec

This receipt exists so a later operator can open one object and answer five questions without re-reading several prose articles:

1. **what detachment or revocation action happened**
2. **who had authority to do it**
3. **what future channels were cut off**
4. **what residue survived in bytes, rosters, or storage**
5. **what stronger sentence the product refused to make**

## Required receipt fields

- `receipt_id`
- `issued_at`
- `actor_handle`
- `action_class`
- `scope_class`
- `authority_basis`
- `target_subject_refs`
- `target_peer_refs`
- `future_update_boundary`
- `byte_survivor_scope`
- `roster_residue_scope`
- `storage_residue_scope`
- `reappearance_triggers`
- `blocked_stronger_sentence`
- `followup_review_refs`

## Example safe sentences

- `Offline roster row was hidden only; standing relationship evidence may still survive.`
- `Selected peer was cut off from future updates, but already synchronized bytes remained outside the action boundary.`
- `Program uninstall removed the runtime while leaving filesystem and archive residue for separate review.`

## Example blocked stronger sentences

- `This seat is gone everywhere.`
- `No one can reattach without new approval.`
- `All data and records were removed.`

## Why this receipt matters

Detachment actions are easy to overclaim because the UI often gets cleaner before the world gets smaller.
AnonSync must therefore leave a durable receipt that preserves the difference between:

- decluttering and severance
- future-update cutoff and byte retraction
- linked-family removal and ecosystem-wide disappearance
- uninstalling software and clearing all state
''',
}

status_addendum = r'''## Revision addendum — detachment, revocation, roster residue, and installation afterlife after rev0350

This tranche locks the next seam around **detachment and revocation truth**.
The key decisions now made explicit in the archive are:

- **detachment and revocation are first-class contract objects rather than scattered button labels**
- **hide-record, disconnect-local, revoke-selected-peer, remove-linked-family, unlink-seat, and uninstall-runtime are different truths**
- **future-update cutoff is weaker than byte retraction, and byte retraction is weaker than ecosystem disappearance**
- **roster cleanup is weaker than trust severance, and trust severance is weaker than remote survivor absence**
- **every serious detachment action needs one receipt that preserves authority basis, propagation boundary, byte/roster/storage residue, reappearance triggers, and the blocked stronger sentence**

New docs added in this tranche:

- `1246-resilio-detachment-revocation-roster-residue-and-visibility-fragmentation-evaluation.md`
- `1247-detachment-and-revocation-contract-sheet-page-action-class-authority-scope-and-residue-interface-spec.md`
- `1248-offline-roster-visibility-review-page-hide-clear-reappear-and-observation-ceiling-interface-spec.md`
- `1249-access-revocation-proof-page-disconnect-unlink-remove-and-future-update-boundary-interface-spec.md`
- `1250-installation-clearance-review-page-uninstall-storage-residue-and-peer-record-afterlife-interface-spec.md`
- `1251-detachment-lineage-receipt-page-action-authority-residue-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `hide`, `disconnect`, `remove`, `unlink`, and `uninstall` can no longer hide the difference between decluttering, revocation, and real severance
- roster review now surfaces when a record can reappear without a new grant instead of pretending that visual absence proves relationship absence
- revocation review now publishes the boundary between future-flow cutoff and already-landed bytes that remain outside the action
- uninstall review now keeps program removal, storage residue, archive residue, and stale peer records adjacent instead of scattering them across host and support prose
- later operators can open one receipt and see who acted, what boundary the action actually touched, what survived, and which stronger cleanup sentence the product still refused to make

'''

for name, content in files.items():
    (DOCS / name).write_text(content.strip() + '\n', encoding='utf-8')

status_path = DOCS / '00-status.md'
old = status_path.read_text(encoding='utf-8')
if not old.startswith(status_addendum):
    status_path.write_text(status_addendum + old, encoding='utf-8')
