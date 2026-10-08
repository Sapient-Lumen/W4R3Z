from pathlib import Path

root = Path('.')
docs = root / 'docs'

new_docs = {
    '874-resilio-permission-family-delegation-and-revocation-fragmentation-evaluation.md': '''# Resilio permission-family, delegation, and revocation fragmentation evaluation

## Why this pass exists

The archive already had strong work on artifact families, intake, approval, epoch rotation, residency promises, destructive healing, and maintenance semantics.
What it still lacked was one explicit evaluation of a narrower but highly consequential seam:

> when an operator asks `who can do what, can they delegate it onward, can I change that later, and what still remains after revocation?`, how many different present-day Resilio contracts do they have to remember?

Current official Resilio docs are still useful because they are candid about the real differences.
They still openly say that:

- **Advanced** folders have `Read Only`, `Read & Write`, and `Owner`, while only Owners can share onward, change permissions, and revoke access
- **Standard** folders do not have an Owner concept, any peer can share the key it has, and on-the-fly permission changes are not possible without removing and re-adding the share with a new key
- linked devices under one identity all act as **Owners**, so `my own seats` and `someone I granted access to` are not the same authority plane
- revoking a peer stops **future updates**, but files already synchronized remain in that peer's folder
- Read Only is not merely `can't upload`; changed files suspend further synchronization for that peer unless overwrite-heal policy is separately enabled
- a **local share** cannot be granted Owner, cannot exceed the permission of its source, may need re-sharing to change permissions, and can automatically lower if the remote Owner lowers the source seat
- source removal or disconnect can remove the derivative local share as a consequence of source continuity loss

That is good candor.
It is also strong evidence that AnonSync should not clone the exact contract.

## What current Resilio still gets right

### 1) Permission is not one flat yes/no bit

Resilio is right that `can view`, `can write`, `can delegate`, and `can administer later` are different powers.

### 2) Revocation is not magic deletion

Resilio is also right that revoking future updates is not the same as reaching back and erasing material that already arrived.
That retained-material truth matters.

### 3) Derived seats can have narrower authority than their source

Resilio is right that a local derivative share should not silently exceed its source authority.
A copied projection can be narrower than the upstream seat.

## Why AnonSync still should not clone it

### 1) The answer depends too much on artifact family folklore

Current Resilio still makes one ordinary operator question depend on remembering whether the subject is:

- Standard or Advanced
- one of my linked devices or another person's identity
- a directly shared seat or a derivative local share
- a live peer policy or a new key issuance problem

Those are real distinctions, but the product should own them in one policy grammar rather than forcing article archaeology.

### 2) Live policy and artifact replacement are still too entangled

In Advanced folders, some permission changes are live policy mutation.
In Standard folders, permission change means remove and re-add with a new key.
That is not a detail.
That is a first-class difference between `edit the rule` and `mint a successor artifact`.
A serious product should preview that difference before the operator clicks anything.

### 3) Revocation still sounds stronger than it is

`Disconnect` and revoke language in current docs can be read quickly as if access was simply removed.
But the same docs still say already synchronized files remain on the peer.
So the real answer is:

> future updates stop, retained bytes stay, and later cleanup or successor policy is a separate matter.

That deserves a dedicated revocation-impact object, not just a peer-row verb.

### 4) Linked-own-device semantics are still too easy to confuse with granted rights

Current docs still say linked devices under one identity act as Owners.
That may be useful, but it means `my second seat` and `external owner-like collaborator` are not interchangeable governance stories.
AnonSync should never hide that difference behind one generic `owner` row.

### 5) Local derivatives still inherit awkwardly rather than legibly

Current local-share docs still show a derivative that cannot exceed source permissions, can be auto-lowered by source changes, may require re-share to change access, and disappears when the source disappears.
Useful truth, but too much of it still lives in caveat prose.
A derivative seat should publish its narrowing and dependence explicitly.

## Hard decisions now locked for AnonSync

1. **Authority policy is a first-class object.** Operators should not have to infer policy from artifact family alone.
2. **Live mutation and reissue are different verbs.** The product must say whether a requested change edits an existing policy or requires successor issuance.
3. **Revocation always publishes retained-material truth.** `Stops future updates` and `already-held bytes remain` must stay adjacent.
4. **Own-seat linkage and granted external rights stay separate.** Internal seat-family expansion is not the same workflow as granting another principal.
5. **Derivative seats can only narrow, never silently widen.** Any downstream or local derivative must publish the source ceiling and its own stricter floor.
6. **Every policy action emits a receipt.** Later operators should not have to reconstruct whether a change was live, reissued, downgraded, or merely announced.

## Replacement page family justified by this pass

This pass therefore justifies five more product-owned surfaces:

- **Authority contract**
- **Permission change preview**
- **Delegation boundary review**
- **Revocation impact**
- **Authority policy receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right that read, write, delegate, owner-like administration, revocation, linked-seat ownership, and derivative-local narrowing are genuinely different truths. But it still makes the operator reconstruct those truths from folder family, identity family, derivative-share caveats, and key-vs-policy semantics. AnonSync should keep the candor and refuse the fragmented permission contract.
''',
    '875-authority-contract-page-grant-class-delegability-and-retained-material-interface-spec.md': '''# Authority contract page: grant class, delegability, and retained-material truth interface spec

## Purpose

This page answers one ordinary question:

> what authority does this seat actually hold right now, what stronger authority does it not hold, and what happens to already-held material if we change or revoke it later?

The page exists because operators should not need to inspect folder family, peer lineage, or local-derivative caveats just to understand one seat's contract.

## Core decision

Every live seat that can read, write, delegate, or be revoked must render one first-class **Authority contract** page.
That page owns:

- grant class
- delegation ceiling
- mutation path
- retained-material truth
- derivative dependence
- strongest safe sentence

## Fixed page order

1. seat strip
2. grant class card
3. delegation card
4. mutation path card
5. retained-material card
6. derivative dependence card
7. receipt / lineage rail

### 1) Seat strip

Show:

- seat label
- principal or seat family
- current grant class
- origin family
- strongest next-safe action

Grant classes must include at minimum:

- `observe-only`
- `write-without-delegate`
- `delegate-within-ceiling`
- `owner-like-admin`
- `derived-local-narrowing`
- `linked-own-seat`
- `revoked-future-updates`

### 2) Grant class card

Publish:

- what this seat may presently do
- what it may not do
- whether the grant is live policy or the residue of an artifact that has already been consumed
- whether the seat is native, imported, linked, derived, downgraded, or superseded

### 3) Delegation card

Show clearly:

- may this seat invite or issue onward authority?
- if yes, what ceiling may it delegate?
- if no, what nearby stronger seat would be required?
- whether downstream delegation is direct, approval-gated, or forbidden

### 4) Mutation path card

The page must say which verb family applies for change:

- `edit existing live policy`
- `issue successor artifact`
- `remove and reconnect`
- `lower only`
- `blocked`

This card exists to stop operators from assuming every permission change is a live edit.

### 5) Retained-material card

This card publishes the revocation truth in one sentence family:

- what future motion stops if revoked or downgraded
- what already-held material remains local to the seat
- whether prior copies remain usable, merely inspectable, or administratively orphaned
- whether cleanup or reclamation is a separate later workflow

### 6) Derivative dependence card

Publish:

- whether this seat depends on a source seat or parent line
- whether it can exceed, match, or only narrow source authority
- what source changes auto-lower or invalidate it
- whether source removal disconnects or destroys this seat

### 7) Receipt / lineage rail

Show linked change receipt, downgrade receipt, revocation receipt, or successor receipt when available.

## Rules

### Rule 1 — grant class must not be inferred from iconography alone

A pencil, shield, chain, or linked-device badge is not enough.
The contract page must state the actual authority.

### Rule 2 — delegability must be explicit

`can write` and `can delegate` are different powers and must never collapse into one label.

### Rule 3 — retained material must stay adjacent to revocation meaning

Never let `revoke access` sound like remote deletion unless that stronger effect is actually true.

### Rule 4 — derivative seats publish their narrowing

A local or downstream derivative must always state what stronger source authority it depends on and what stronger action it cannot do.

## Acceptance criteria

A later operator can:

- tell what this seat can do now
- tell whether it may delegate onward
- tell whether a requested change is live mutation or reissue
- tell what bytes remain after revocation or downgrade
- reopen the right workflow from this page without reading support prose
''',
    '876-permission-change-preview-page-live-policy-artifact-reset-and-required-reissue-interface-spec.md': '''# Permission change preview page: live policy edit, artifact reset, and required reissue interface spec

## Purpose

This page answers one ordinary question:

> if I try to change this seat's authority, am I editing a live policy, minting a successor, forcing reconnection, or only lowering a derivative?

The page exists because permission change is not one universal verb.

## Core decision

Any action that changes a seat's authority must pass through a **Permission change preview** page before commit.
The preview owns:

- requested change
- mechanism class
- continuity effect
- downstream seat effect
- reauthentication / reacceptance burden
- strongest safe sentence after change

## Fixed page order

1. requested change strip
2. mechanism class card
3. continuity effect card
4. downstream impact card
5. operator burden card
6. commit boundary card

### 1) Requested change strip

Show:

- current grant class
- requested grant class
- target principal or seat family
- whether this is upgrade, downgrade, revoke, or transform
- strongest next-safe action

### 2) Mechanism class card

One of the following must be chosen explicitly:

- `live policy edit`
- `successor issuance required`
- `remove and reconnect required`
- `lower derivative only`
- `not possible`

This card must explain why.

### 3) Continuity effect card

Publish whether the requested change:

- preserves the same seat lineage
- narrows the existing seat
- creates a new successor while old continuity may persist elsewhere
- requires the subject to reconnect or reaccept
- produces an epoch boundary or policy fork

### 4) Downstream impact card

Show effects on:

- derivatives
- delegates
- linked own seats
- retained approvals or remembered trust
- existing receipts

A change that would silently auto-lower or invalidate downstream seats must say so before commit.

### 5) Operator burden card

Show any required new work:

- reissue invite
- reclaim stale artifact
n- request fresh acceptance
- rotate related derivatives
- publish new receipt

### 6) Commit boundary card

The preview ends with one of these clear outcomes:

- `change now`
- `issue successor instead`
- `downgrade only`
- `review delegation first`
- `blocked`

## Rules

### Rule 1 — preview the mechanism, not just the target label

`Make Read Only` or `Make Writer` is not enough.
The operator must know whether the system is editing policy or replacing authority.

### Rule 2 — lineage impact must be explicit

A change that forks continuity or requires reacceptance cannot look like a minor toggle.

### Rule 3 — downstream effects must publish before commit

The page must show derivative lowering, delegate invalidation, or receipt supersession before the operator confirms.

## Acceptance criteria

A later operator can:

- tell how the change is actually implemented
- tell whether the prior seat survives, narrows, or is superseded
- tell which downstream seats and receipts are affected
- avoid mistaking artifact reissue for live policy mutation
'''.replace('\nn-','\n-'),
    '877-delegation-boundary-review-page-owner-capability-local-derivative-and-downstream-seats-interface-spec.md': '''# Delegation boundary review page: owner capability, local derivative narrowing, and downstream seat limits interface spec

## Purpose

This page answers one ordinary question:

> who may grant onward authority from here, how far may that authority travel, and which seats are structurally prevented from widening the line?

The page exists because delegation is not the same thing as write access and because derivatives should never silently look owner-like.

## Core decision

Every place where onward sharing, downstream seat creation, or derivative-local expansion is possible must render a **Delegation boundary review** page.

## Fixed page order

1. delegation strip
2. issuer qualification card
3. downstream ceiling card
4. derivative narrowing card
5. prohibited widening card
6. receipt / challenge rail

### 1) Delegation strip

Show:

- issuing seat
- source subject
- current delegation grade
- requested downstream action
- strongest next-safe action

### 2) Issuer qualification card

Publish whether the current seat is:

- not allowed to delegate
- allowed to delegate within fixed limits
- owner-like for this subject only
- linked-own-seat rather than external issuer
- derivative and therefore narrowing-only

### 3) Downstream ceiling card

Show the highest authority the issuer may create downstream.
Examples:

- may create observer only
- may create writer but not admin
- may create sibling derivative only
- may create no downstream seats

### 4) Derivative narrowing card

If a downstream seat is derivative or local, publish:

- source ceiling
- derivative floor
- auto-lowering triggers
- source-removal consequence
- whether the derivative survives only as residue after source loss

### 5) Prohibited widening card

List stronger forbidden moves explicitly.
Examples:

- derivative cannot become owner-like
- non-admin writer cannot mint delegate-capable seats
- linked own seats cannot be confused with third-party grants

### 6) Receipt / challenge rail

Link to existing delegation receipt, challenge, revocation impact, or successor warning.

## Rules

### Rule 1 — write is not delegate

The review must separate mutation of subject bytes from authority to invite or widen.

### Rule 2 — derivatives can only narrow

A derivative-local seat must never appear to widen or equal the source unless that is actually true and explicitly published.

### Rule 3 — own-seat linkage is not third-party delegation

The grammar for `add my own seat` must remain distinct from the grammar for `grant another principal authority`.

## Acceptance criteria

A later operator can:

- tell whether the current seat may grant anything downstream
- tell the maximum downstream authority it may create
- tell why a derivative cannot widen beyond its source
- distinguish own-seat expansion from external delegation
''',
    '878-revocation-impact-page-future-updates-retained-bytes-and-successor-paths-interface-spec.md': '''# Revocation impact page: future updates, retained bytes, and successor paths interface spec

## Purpose

This page answers one ordinary question:

> if I revoke, disconnect, or downgrade this seat, what future motion stops, what already-arrived material remains, and what later cleanup or successor path is still separate?

The page exists because `revoke access` often sounds stronger than the product can honestly guarantee.

## Core decision

Every revoke, disconnect, or future-update cutoff action must pass through a first-class **Revocation impact** page.

## Fixed page order

1. revocation strip
2. future-motion cutoff card
3. retained-material card
4. downstream residue card
5. successor / cleanup paths card
6. revocation receipt rail

### 1) Revocation strip

Show:

- seat being changed
- current grant class
- requested resulting state
- strongest next-safe action

### 2) Future-motion cutoff card

Publish exactly what stops:

- future reads
- future writes back
- future arrivals
- future delegation
- admin mutation rights

### 3) Retained-material card

Publish exactly what remains after cutoff:

- bytes already present
- metadata or names already present
- local derivatives already present
- receipts or attestations already held

This card must also say what stronger erasure claim is forbidden.

### 4) Downstream residue card

Show whether revoking this seat affects:

- downstream derivatives
- already-issued artifacts
- linked sibling seats
- preserved local exports
- orphaned but still-held data

### 5) Successor / cleanup paths card

Show separate follow-on paths, such as:

- reclaim later by successor issuance
- request local cleanup proof
- preserve retained residue as evidence only
- no automatic remote deletion claim available

### 6) Revocation receipt rail

The page must emit and link a durable receipt containing:

- cutoff time
- rights removed
- rights retained
- retained-material warning
- follow-on path ceiling

## Rules

### Rule 1 — revoke must not imply erase unless erase is truly owned

`future updates stop` and `existing local bytes remain` must be publishable together.

### Rule 2 — retained residue is not silent

If local bytes, exports, or derivatives survive, the review must say so before commit.

### Rule 3 — successor paths stay separate from revocation itself

The product must not imply that downgrade, reconnect, remote cleanup, and successor issuance are one action.

## Acceptance criteria

A later operator can:

- tell what rights stopped at revocation time
- tell what material still remains with the former seat
- tell what downstream residues still exist
- tell which later cleanup or successor path would still be needed
''',
    '879-authority-policy-receipt-page-live-grant-floor-retained-material-and-reissue-boundary-interface-spec.md': '''# Authority policy receipt page: live grant floor, retained material, and reissue boundary interface spec

## Purpose

This receipt preserves the policy truth that later operators usually misremember:

> what authority was actually in force, what floor remained after the last change, and whether the result came from live mutation, derivative narrowing, revocation, or successor reissue.

## Core decision

Every meaningful authority action must emit an **Authority policy receipt**.
That includes:

- initial grant
- upgrade
- downgrade
- revocation
- derivative creation
- successor reissue

## Fixed receipt fields

1. receipt header
2. effective grant section
3. mechanism section
4. retained-material section
5. derivative / downstream section
6. reopen boundary

### 1) Receipt header

Show:

- receipt type
- subject
- affected seat or seat family
- issuance time
- actor / authority basis

### 2) Effective grant section

Publish:

- resulting live grant floor
- stronger denied interpretations
- current delegability status
- whether the seat is linked, external, or derivative

### 3) Mechanism section

Publish one mechanism class:

- live policy edit
- derivative narrowing
- revocation of future updates
- successor reissue
- blocked / no-op

### 4) Retained-material section

Publish:

- what remains with the affected seat
- what no longer updates
- whether automatic cleanup was not performed
- strongest safe sentence after the change

### 5) Derivative / downstream section

Publish:

- derivatives affected
- delegates affected
- receipts superseded
- successor artifacts created or required

### 6) Reopen boundary

Publish the next conditions that would invalidate or supersede this receipt.
Examples:

- successor artifact accepted
- source seat removed
- derivative auto-lowered again
- retained-material cleanup attested separately

## Rules

### Rule 1 — receipt must preserve mechanism truth

Later operators should not need to guess whether a change was a live policy mutation or a reissue event.

### Rule 2 — receipt must preserve retained-material truth

A revocation receipt that omits surviving bytes is incomplete.

### Rule 3 — receipt must preserve authority floor, not aspirational ceiling

The stored result is the actual live floor after the action, not the original requested ambition.

## Acceptance criteria

A later operator can reopen the receipt and tell:

- the resulting authority floor
- whether delegation still survived
- what material remained after the action
- whether the change was live mutation or successor reissue
- what future event would supersede the receipt
'''
}

for name, content in new_docs.items():
    (docs / name).write_text(content.strip() + '\n', encoding='utf-8')


def prepend(path_str: str, text: str):
    path = root / path_str
    old = path.read_text(encoding='utf-8')
    path.write_text(text.strip() + '\n\n' + old, encoding='utf-8')


def append(path_str: str, text: str):
    path = root / path_str
    old = path.read_text(encoding='utf-8')
    path.write_text(old.rstrip() + '\n\n' + text.strip() + '\n', encoding='utf-8')

readme_add = '''## Revision addendum — authority policy, delegation boundaries, and retained-material revocation truth

This revision continues directly from `rev0288` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **Standard vs Advanced folder permissions, Owner vs non-Owner delegation, linked-device Owner semantics, on-the-fly vs reissue-based permission change, one-way sync breakage, and local-share narrowing / auto-lowering rules**.
2. Tightens the non-clone line again: borrow Resilio's candor that read, write, delegate, revoke, and derivative-local narrowing are materially different truths; refuse any contract where the operator still has to reconstruct those truths from folder family, identity family, and share caveats.
3. Adds one new **Resilio evaluation** document focused on why the present-day Resilio permission / delegation / revocation answer is still too fragmented to clone even though the underlying truths are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: authority contract, permission change preview, delegation boundary review, revocation impact, and authority policy receipt.
5. Makes one hard product decision explicit: **authority policy is a first-class object**. The operator should not have to infer the live contract from artifact family alone.
6. Makes another hard product decision explicit: **live mutation and reissue are different verbs**. The product must say whether a requested permission change edits an existing policy or requires successor issuance / reconnection.
7. Makes a third hard product decision explicit: **revocation always publishes retained-material truth**. `Future updates stop` and `already-held bytes remain` must stay adjacent.
8. Packages the result as another continuation archive whose new tranche makes the `grant class / delegation boundary / revocation residue` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present permission contract**

This time the reason is especially clear around **Standard vs Advanced folder semantics, linked-device ownership, revocation residue, and local-derivative narrowing**.
Current official materials simultaneously show that:

- `Sync functionality in detail` and `User Management` still say `Owner` can share, change permissions, and revoke access, while revoking cuts off future updates but does not remove already synchronized files.
- `What's the difference between Standard and Advanced folders?` still says Standard folders do not have an Owner concept, any peer can share the key it has, and changing permissions is not on-the-fly there because the share must be removed and re-added with a new key.
- `How to create a Read Only folder while syncing across linked devices?` and `Is one-way synchronization possible?` still say linked devices under one identity act as Owners, so achieving a read-only linked-device posture requires stepping out of the linked-device grammar and using a Standard-folder key instead.
- `Sharing a folder locally` still says a local derivative cannot receive Owner, cannot exceed source permissions, may need re-sharing to change access, and auto-lowers if the source seat is downgraded.

That candor is useful.
The policy contract is the problem.
AnonSync should not clone a world where the operator still has to reconstruct, from several docs and share families, whether a seat may delegate, whether a permission change is live or requires reissue, what revocation actually leaves behind, and whether a local derivative is merely narrower or already orphaned.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful truths are real, but the present-day permission contract still hides too much governance inside folder-family distinctions, linked-seat exceptions, and derivative-share caveats instead of owning authority policy as one stable page family.**

## New documents in rev0289

- `874` Resilio permission family, delegation, and revocation fragmentation evaluation
- `875` Authority contract page
- `876` Permission change preview page
- `877` Delegation boundary review page
- `878` Revocation impact page
- `879` Authority policy receipt page
'''

status_add = '''## Latest addendum — authority policy, delegation boundaries, and retained-material revocation truth after rev0288

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **permission answers still depend too much on folder family, identity family, and derivative-share class**
- **changing authority is still sometimes a live policy edit and sometimes a reissue / reconnect event, and current Resilio makes the operator remember which is which**
- **revocation still mostly means future-update cutoff plus retained local bytes, not clean erasure**

Hard decisions made in this tranche:

1. **Authority policy is a first-class object.** AnonSync never makes the operator infer the live contract from artifact family alone.
2. **Live mutation and reissue are different verbs.** A permission change preview must say whether the result comes from editing policy, issuing a successor, reconnecting, or merely lowering a derivative.
3. **Revocation always publishes retained-material truth.** `Future updates stop` and `already-held bytes remain` stay adjacent.
4. **Own-seat linkage and granted external rights stay separate.** `Add my own seat` is never flattened into `grant another principal authority`.
5. **Derivative seats can only narrow, never silently widen.** Local or downstream derivatives must publish source ceiling, current floor, and auto-lowering triggers.

That yields five more ordinary product-owned pages:

- **Authority contract page**
- **Permission change preview page**
- **Delegation boundary review page**
- **Revocation impact page**
- **Authority policy receipt page**

This tranche closes a real gap between the earlier artifact/intake work and the ordinary question `what authority is really live here right now, how can it change, and what still remains after I cut it off?`.
'''

append('docs/10-resilio-sync-evaluation.md', '''## Revision addendum — evaluation after rev0288: borrow permission candor, reject artifact-family policy folklore

Another current Resilio pass improves the evaluation in one more narrow place.

### Borrow

Keep borrowing these traits:

- admitting that read, write, delegate, and revoke are materially different powers
- admitting that linked-own-device seats and externally granted seats are not the same authority plane
- admitting that revocation usually cuts off future updates rather than magically erasing already-held material
- admitting that derivative-local seats can be narrower than their source and can auto-lower when the source is downgraded

### Refuse to clone

Do not clone these traits:

- making operators infer policy from Standard vs Advanced vs linked-device vs local-share family
- treating `change permission` as one universal verb when some cases are live edits and others require reissue or reconnection
- letting `revoke access` sound stronger than `future updates stop while already-synced bytes remain`
- leaving no stable page that says whether a derivative seat can delegate, auto-lowers, or dies with source continuity

### Stronger replacement

AnonSync should publish five first-class surfaces instead:

- **Authority contract**
- **Permission change preview**
- **Delegation boundary review**
- **Revocation impact**
- **Authority policy receipt**

The governing rule is simple:

> if the product is strong enough to say `this seat can read, write, delegate, or is revoked`, it must first own whether that truth comes from live policy, successor issuance, linked-own-seat semantics, or derivative narrowing, and what retained material survives any cutoff.
''')

append('docs/11-resilio-borrow-line-and-non-clone-scorecard.md', '''## Revision addendum — scorecard after rev0288: borrow permission candor, reject family-dependent policy answers

Another current Resilio pass improves the scorecard in one more narrow place.

### Borrow

Keep borrowing these traits:

- admitting that owner-like delegation is a stronger class than ordinary write access
- admitting that linked own devices and granted peers are different authority stories
- admitting that revocation does not imply erasure of already-held material
- admitting that derivative local seats should not exceed source authority and may auto-lower with it

### Refuse to clone

Do not clone these traits:

- making the ordinary policy answer depend on whether the seat came from a Standard key, Advanced certificate path, linked-device identity, or local derivative caveat
- blurring live permission mutation with remove-and-reissue successor flow
- letting `revoke` overclaim when retained bytes, exports, or derivatives still survive
- leaving no durable receipt of the resulting authority floor and reissue boundary

### Stronger replacement

AnonSync should publish five first-class surfaces instead:

- **Authority contract**
- **Permission change preview**
- **Delegation boundary review**
- **Revocation impact**
- **Authority policy receipt**

The governing rule is simple:

> if the product is strong enough to say `this seat may act` or `this seat may no longer act`, it must first own the live authority floor, delegation ceiling, retained-material truth, and whether the result came from policy mutation or successor reissue.
''')

append('docs/39-interface-pattern-language.md', '''## Revision addendum — new pattern: policy lives above artifact family

Pattern name: **Policy before transport family**

Use when:

- the same operator question gets different answers depending on artifact or seat family
- some changes are live policy edits while others require reissue or reconnect
- the operator could otherwise mistake family taxonomy for the actual contract

Rules:

- publish the live authority floor before naming the artifact family
- publish whether change is mutation or reissue before offering the action verb
- keep retained-material truth adjacent to revoke/downgrade verbs
- never let derivative-local seats impersonate source-level delegation

## Revision addendum — new pattern: revoke is not erase

Pattern name: **Cutoff truth beside residue truth**

Use when:

- future motion can be stopped
- already-held bytes or derivatives may still survive
- the operator might overread `remove access` as global disappearance

Rules:

- pair future-update cutoff with retained-material truth on the same surface
- list stronger forbidden cleanup claims explicitly
- make successor or cleanup paths separate follow-on objects
- require a receipt that preserves the resulting authority floor and surviving residue
''')

append('docs/40-architecture-decisions.md', '''## Revision addendum — architecture decision after rev0288: authority policy is a first-class object

The archive now needs one more explicit architecture rule:

- live authority must compile into a first-class policy object rather than being reconstructed from artifact family, seat origin, and help-text caveats

At minimum the system should preserve:

- affected principal or seat family
- resulting authority floor
- delegation ceiling
- mechanism class (`live edit`, `derivative narrowing`, `revocation`, `successor reissue`)
- retained-material truth after cutoff or downgrade
- source-dependence and auto-lowering triggers for derivatives
- receipt lineage and supersession boundary

A seat may still arrive through many carriers, but its ongoing policy must not be trapped inside the carrier family once accepted.
''')

roadmap_add = '''## Revision addendum — roadmap after rev0288: authority policy and revocation-residue tranche

Near-term work newly justified by this pass:

1. Add authority-policy objects for grant floor, delegation ceiling, retained-material truth, and source-dependence.
2. Build permission-change preview before any upgrade, downgrade, revoke, or derivative-seat action is allowed to masquerade as one generic toggle.
3. Add delegation-boundary review so linked-own-seat expansion, external delegation, and derivative-local narrowing stop sharing one vague `share` grammar.
4. Emit revocation-impact receipts that preserve future-update cutoff, surviving local material, and follow-on cleanup / successor ceilings.
5. Connect those receipts into artifact intake, rotation, maintenance, residency, local-share, and destructive-heal surfaces so authority memory does not fall back to folder-family folklore.

Added this tranche to the roadmap:

- `874` Resilio permission family, delegation, and revocation fragmentation evaluation
- `875` Authority contract page
- `876` Permission change preview page
- `877` Delegation boundary review page
- `878` Revocation impact page
- `879` Authority policy receipt page
'''
prepend('README.md', readme_add)
prepend('docs/00-status.md', status_add)
prepend('docs/50-roadmap.md', roadmap_add)
append('docs/sources.md', '''## Revision addendum — authority policy, delegation boundary, and revocation residue after rev0288

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about Standard-vs-Advanced permission semantics, Owner delegation, linked-device ownership, read-only breakage and overwrite-heal posture, derivative-local share narrowing, and revocation residue.
The new questions were:

> where do current official docs most clearly show that `who can do what here?` is still answered differently depending on folder family, identity family, and derivative-local class?

> where do those same current docs still show that `change permission`, `revoke`, and `share onward` are not one stable operator grammar today because some paths are live policy edits and others are remove-and-reissue or local-derivative caveats?

The most load-bearing source set for this pass was:

- Resilio's current `Sync functionality in detail` article, which still says Owner can share, change permissions, and revoke access, and that linked devices under one identity can approve from any linked device.
- Resilio's current `User Management` article, which still says linked devices under one identity act as Owners, that Read Only changes do not propagate and suspend further sync for changed files on that peer, and that disconnect cuts off future updates while already-synchronized files remain.
- Resilio's current `What's the difference between Standard and Advanced folders?` article, which still says Standard folders have no Owner concept, any peer can share the key it has, and permission changes there require removing and re-adding with a new key.
- Resilio's current `Sync Share Dialog (Desktop)` article, which still says only Owners can share Advanced folders, while Standard folders have no Owner level and keys do not use the approval mechanism.
- Resilio's current `How to create a Read Only folder while syncing across linked devices?` article, which still says linked-device sync makes all linked devices Owners and that achieving read-only there requires using a Standard-folder Read Only key instead.
- Resilio's current `Is one-way synchronization possible?` article, which still says Advanced folders do not support read-only synchronization across linked devices and that Read Only changes can stop synchronization for changed files unless overwrite-heal is enabled.
- Resilio's current `Sharing a folder locally` article, which still says local derivatives cannot receive Owner, cannot exceed source permissions, may need re-sharing to change access, auto-lower when the source seat is downgraded, and disappear when the source is removed or disconnected.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0289

- Sync functionality in detail  
  https://help.resilio.com/hc/en-us/articles/204754389-Sync-functionality-in-detail

- User Management  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- What's the difference between Standard and Advanced folders?  
  https://help.resilio.com/hc/en-us/articles/204754679-What-s-the-difference-between-Standard-and-Advanced-folders

- Sync Share Dialog (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- How to create a Read Only folder while syncing across linked devices?  
  https://help.resilio.com/hc/en-us/articles/206216565-How-to-create-a-Read-Only-folder-while-syncing-across-linked-devices

- Is one-way synchronization possible?  
  https://help.resilio.com/hc/en-us/articles/204754279-Is-one-way-synchronization-possible

- Sharing a folder locally  
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log
''')

