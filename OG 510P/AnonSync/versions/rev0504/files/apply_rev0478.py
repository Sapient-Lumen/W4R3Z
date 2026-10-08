from pathlib import Path

root = Path('.')
docs = root / 'docs'

new_files = {
    '2008-resilio-remedy-hardening-attestation-successor-controller-roster-delegated-authority-and-shadow-controller-fragmentation-evaluation.md': '''# Resilio remedy hardening attestation successor controller roster, delegated authority, and shadow-controller fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for acknowledging several ingredients of authority inside the surviving world, even if they do not yet elevate them into one typed controller-roster verdict.
That is useful.

The strongest present ingredients are:

- current `User Management` docs still say only users with Owner permission can invite new users to a folder and revoke access rights from other peers, and that when you share across your own devices linked to one identity all of your devices act as Owners
- current `Sync Private Identity & Linking My Devices` docs still say all folders automatically become available on all linked devices, approvals for new peers can be issued from any linked device where the folder is present, and a remote user may choose to auto-approve all your linked devices for future sharing
- current `Sync functionality in detail` docs still say folder list is common across linked devices and that you can approve connections from any of your linked devices instead of only the original sharer
- current `Comprehensive guide to syncing (Desktop-Desktop)` docs still say linked-device mode gives every folder automatic full read-write access while manual sharing is the lane where explicit per-folder privileges are chosen
- current `How to create a Read Only folder while syncing across linked devices?` docs still say linked-device sync gives Owner permission by default and that achieving read-only on a linked device requires a Standard-folder manual-key detour
- current `Sharing a folder locally` docs still say local shares cannot receive Owner permission, inherit only the source permission level, cannot have their access level changed through user management, and must be removed and re-shared for some permission changes
- current `Folder Types and Management` docs still say Owner, Read & Write, Read Only, selective, full, pending, and disconnected states are materially distinct folder behaviors rather than one flat control state

## Where the current contract still fragments

The problem is not that Resilio hides the ingredients.
The problem is that it still does not produce one first-class, case-scoped **successor controller roster and delegated-authority discipline** object.

Today an operator can often infer only weaker truths such as:

- the predecessor world is retired for the named slice, so the successor world is now the only legitimate world-level controller
- all linked devices under one identity can act as Owners, but the actual live controller roster is implicit rather than enumerated
- a remote approval can widen into future auto-approval across linked devices, but the authority expansion is not surfaced as a bounded delegation event
- local shares cannot be Owners, yet they still form local derivative control surfaces that can survive until manually re-shared or reconnected
- some folders live under manual per-folder privilege choices while linked-device mode bypasses per-folder narrowing by granting automatic world-wide ownership inside that identity family
- read-only outcomes sometimes require architectural detours rather than being expressible as a simple narrowing inside the existing controller set

Those are useful clues.
They are not the same as an explicit answer to `who inside the surviving world may currently write, delete, share, approve, revoke, or further delegate; which of those controllers were intentionally designated; and is the live controller set still narrow enough that one accountable actor can honestly speak for it?`

## Why that matters for AnonSync

AnonSync needs a stronger sentence than `the predecessor is retired` and stronger still than `the successor is exclusive controller for the named slice`.
It needs to support claims such as:

- the predecessor is retired, but the successor world still has too many live Owners for a single-accountable-controller sentence
- world-level exclusivity is true, yet authority minimization failed because every linked device can still approve or extend trust
- the controller set is intentionally narrow for one object family, while another family still inherits broad linked-device ownership by default
- a shadow controller exists through auto-approval memory, copied trust handles, or a still-live delegated owner that the interface must keep visible
- the strongest honest sentence is `exclusive surviving world, controller roster still broad and delegation-heavy`, not because the old world persists but because successor-side authority is itself fragmented

AnonSync therefore needs first-class objects for **controller roster, designation basis, delegation chain, auto-expansion policy, shadow-controller exposure, local derivative surfaces, revocation path, minimum-accountable-controller claim, and blocked stronger single-controller sentence** rather than leaving operators to reconstruct controller truth from Owner semantics, linked-device defaults, approval conveniences, manual read-only detours, and local-share caveats.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `who inside the surviving world can really act right now, and is that controller set intentionally narrow enough to deserve a strong accountability sentence?` — only by making the operator combine several partially overlapping mechanics:

- Owner permission semantics and revocation rights
- linked-device automatic Owner expansion
- any-device approval for present folders
- future auto-approval across linked devices
- linked-device automatic full read-write access
- manual Standard-folder detours to achieve one read-only outcome
- local-share inheritance and non-Owner limitations
- folder-state distinctions that change practical control surfaces

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **successor controller roster and delegated-authority discipline** directly.
Its interface family should let the product separate at least these truths:

- successor exclusive world, live controller roster unreviewed
- controller roster enumerated, designation basis mixed
- controller roster broad by linked-family default
- controller roster intentionally narrowed for named slice only
- delegated owner chain present
- auto-expanding approval memory present
- shadow controller suspected through derivative or local surfaces
- single accountable controller blocked
- bounded controller quorum achieved for named slice only
- broader unique-controller claim blocked

That is why this revision adds five more first-class pages:
**Remedy-hardening-attestation-successor-controller-roster contract sheet**, **successor-controller-roster review**, **successor-controller-roster proof**, **successor-controller-roster timeline**, and **successor-controller-roster lineage receipt**.
''',
    '2009-remedy-hardening-attestation-successor-controller-roster-contract-sheet-page-controller-set-delegation-budget-and-shadow-authority-interface-spec.md': '''# Remedy-hardening-attestation successor controller roster contract sheet page — controller set, delegation budget, and shadow authority

## Purpose

This page is the compact contract for deciding whether a successor world that is already legitimate, discoverable, and exclusive at the world boundary is also governed by a live controller set that is narrow, accountable, intentionally designated, and not silently widened by convenience defaults.
It exists so the product can distinguish `exclusive successor world`, `broad linked-family ownership`, `delegated controller chain`, `shadow controller exposure`, `bounded controller quorum`, and `single-accountable-controller sentence blocked`.

## Core fields

- successor-controller-roster identifier
- source predecessor-authority-retirement receipt identifier
- successor-world identifier
- governed slice identifier
- controller rulebook version
- intended accountable-controller model
- live controller roster
- controller roster completeness class
- designation basis per controller
- controller authority class per controller
- controller surface set per controller
- delegation chain inventory
- delegation depth budget
- delegation expiry or review horizon
- auto-expansion policy status
- linked-family expansion status
- approval-memory expansion status
- derivative local-surface authority status
- shadow-controller suspicion set
- controller minimization status
- quorum requirement if any
- minimum accountable-controller claim class
- highest currently safe public sentence
- strongest blocked stronger sentence
- next fact that upgrades roster standing now
- next fact that collapses roster standing now

## Controller authority classes

The page must model at least these distinct classes:

- controller roster unreviewed
- controller can read only
- controller can write or delete
- controller can share or invite
- controller can approve or admit new dependents
- controller can revoke or lower permissions
- controller can further delegate
- controller can only act through derived local surface
- controller present but surface unknown
- controller disabled for named slice only
- controller removed from roster
- shadow controller suspected

## Designation basis types

The page must preserve at least these distinct bases:

- explicitly designated human operator
- linked-family default expansion
- inherited world-level ownership
- delegated from another controller
- local derivative surface
- approval-memory carry-forward
- copied-handle or stale-trust carryover
- unresolved historical designation

## Controller-minimization classes

The page must support at least these classes:

- minimization unreviewed
- roster broad by architecture
- roster broad by convenience setting
- roster narrowed intentionally for named slice only
- delegation chain longer than policy budget
- shadow-controller risk present
- bounded controller quorum achieved
- single accountable controller achieved for named slice only
- broader stronger controller sentence blocked

## Required page panels

### 1. Controller roster board

Show:

- every currently live controller candidate
- whether each controller is direct, delegated, derived, or shadow
- which surfaces each controller can still touch
- whether the roster is believed complete or partial

### 2. Expansion board

Show:

- whether linked-family defaults automatically widen ownership
- whether approvals can be issued from multiple devices or seats
- whether prior approvals auto-extend to future controller instances
- whether local derivatives create practical control surfaces outside the obvious roster

### 3. Minimization board

Show:

- the intended minimal controller model
- actual live controller count or quorum class
- which controllers could be removed without breaking duty
- whether convenience defaults are inflating authority
- which stronger accountability sentence remains blocked

### 4. Shadow-authority board

Show:

- controllers not formally designated but still practically able to act
- stale or copied trust handles that preserve authority memory
- local or derivative surfaces that may shadow direct authority
- unresolved historical controllers that must stay visible

## Hard rules

The contract sheet must never let:

- `exclusive successor control` impersonate `single accountable controller`
- linked-family ownership hide inside one human label
- auto-approval memory hide inside `already trusted`
- local derivative surfaces hide behind `not propagated remotely`
- partial roster visibility impersonate controller minimization
''',
    '2010-remedy-hardening-attestation-successor-controller-roster-review-page-is-the-successor-worlds-live-authority-set-narrow-accountable-and-intentionally-delegated-interface-spec.md': '''# Remedy-hardening-attestation successor controller roster review page — is the successor world's live authority set narrow, accountable, and intentionally delegated?

## Purpose

This page is the operator-facing review for deciding whether the surviving world's live controller set is actually narrow enough and explicit enough to support strong accountability sentences.
It exists so the product can separate `exclusive surviving world` from `broad surviving owner swarm`.

## Required review questions

The review must force explicit answers to at least these questions:

1. **Who can still act right now inside the successor world?**
2. **Which of those controllers were explicitly designated versus inherited by architecture or convenience?**
3. **Can any controller approve, share, or delegate further without a fresh case review?**
4. **Can any prior approval or linked-family rule auto-expand the controller set later?**
5. **Do any local or derivative surfaces create practical shadow controllers?**
6. **Is the live roster narrow enough to support a bounded-controller or single-controller sentence for the named slice?**

## Mandatory review sections

### 1. Live-controller roster

Show:

- every known controller candidate
- their direct versus delegated status
- whether their presence is explicit, inherited, or merely inferred
- the exact surfaces each one can still touch

### 2. Delegation-chain review

Show:

- who delegated to whom
- whether delegation was intentional or architectural default
- whether any delegation exceeds policy depth or breadth budget
- whether delegated controllers can themselves delegate again

### 3. Auto-expansion review

Show:

- linked-family auto-owner expansion
- approval-from-any-device behavior
- remembered approvals that widen future trust automatically
- any paths by which new controller instances appear without explicit review

### 4. Shadow-controller review

Show:

- local derivative surfaces
n- copied or stale trust handles
- controller-like surfaces that are not visible in the main roster
- unresolved or historical controllers that still require active caution

### 5. Sentence chooser

The review must output one and only one primary sentence class such as:

- exclusive successor world, controller roster unreviewed
- exclusive successor world, broad linked-family controller roster
- controller roster enumerated, delegation chain unresolved
- controller roster intentionally narrowed for named slice only
- shadow-controller risk present, stronger accountability blocked
- bounded controller quorum achieved for named slice only
- single accountable controller achieved for named slice only
- broader unique-controller sentence blocked

## Hard rules

The review must never let an operator hide:

- broad linked-device ownership behind one identity label
- approval-from-any-device behind `still one owner`
- future auto-approval behind `already approved once`
- local derivative authority behind `not a remote peer`
- incomplete roster evidence behind `probably only these controllers`
'''.replace('\nn-','\n-'),
    '2011-remedy-hardening-attestation-successor-controller-roster-proof-page-controller-chain-delegation-scope-and-shadow-authority-ceiling-interface-spec.md': '''# Remedy-hardening-attestation successor controller roster proof page — controller chain, delegation scope, and shadow-authority ceiling

## Purpose

This page is the proof-facing object for showing who inside the successor world can still act and what ceiling therefore applies to any stronger `narrow accountable controller` sentence.
It exists so the product can preserve actual controller evidence instead of collapsing world-level exclusivity into overclaims about accountable operation.

## Required proof bundles

Every proof page must preserve these bundles:

### 1. Source-basis bundle

- source predecessor-authority-retirement receipt
- successor world identifier
- governed slice identifier
- governing controller rulebook version

### 2. Roster-evidence bundle

- evidence for each known live controller
- evidence for absent but historically possible controllers
- evidence for roster completeness or incompleteness
- evidence for each controller's action surfaces

### 3. Delegation bundle

- explicit designation events
- delegated authority grants
- inherited linked-family ownership evidence
- approval-memory or future-auto-approval evidence
- further-delegation capability evidence

### 4. Derivative and shadow bundle

- local derivative authority surfaces
- copied or stale trust-handle authority traces
- shadow-controller suspicion evidence
- unresolved historical controller exposure

### 5. Ceiling bundle

- highest justified accountability sentence
- specific missing fact that blocks stronger minimization
- contradictory evidence that would collapse current roster standing

## Proof outputs

The page must output at least:

- live controller roster assessment
- delegation-depth assessment
- auto-expansion exposure assessment
- shadow-controller assessment
- accountable-controller claim class
- blocked stronger sentence

## Strong proof classes

The page must distinguish at least these proof classes:

- no reliable controller roster evidence
- roster partially known only
- direct controllers known, delegated chain unresolved
- broad architectural controller set proved
- named-slice controller roster intentionally narrowed only
- bounded quorum proved for named slice only
- single accountable controller proved for named slice only
- broader unique-controller claim not proved

## Contradiction triggers

The proof page must visibly downgrade if any of these appear:

- every linked device acts as Owner
- approval can be issued from multiple devices with folder presence
- remembered approval widens future trust automatically
- manual read-only outcome requires leaving the current ownership model
- local derivatives preserve practical control surfaces outside the obvious roster
- any stale or copied trust handle keeps controller admission power alive

## Hard rules

The proof page must never let:

- world-level exclusivity impersonate controller minimization
- explicit designation of one controller erase inherited authority held by others
- lack of remote propagation impersonate absence of local shadow authority
- current roster visibility impersonate proof that no automatic expansion exists
- named-slice narrowing impersonate universal single-controller control
''',
    '2012-remedy-hardening-attestation-successor-controller-roster-timeline-page-designate-delegate-expand-restrict-and-revoke-controller-events-interface-spec.md': '''# Remedy-hardening-attestation successor controller roster timeline page — designate, delegate, expand, restrict, and revoke controller events

## Purpose

This page is the time-ordered event view for how the successor world's controller set is supposed to narrow, stay narrow, or silently widen after predecessor retirement.
It exists so the product can separate `exclusive surviving world`, `controller set expanded by convenience`, `controller set intentionally narrowed`, and `single-accountable-controller standing achieved`.

## Required event types

The timeline must preserve at least these event types:

- predecessor retirement receipt issued
- successor controller roster review opened
- controller explicitly designated
- linked-family ownership expansion observed
- approval-from-any-device surface exercised
- future auto-approval remembered
- delegated owner granted
- delegated controller revoked
- controller surface narrowed
- local derivative surface created
- local derivative surface removed
- manual read-only detour introduced
- shadow-controller suspicion raised
- controller quorum ratified
- single accountable controller confirmed for named slice only
- stronger accountability claim blocked or downgraded

## Mandatory timeline questions

The page must answer in order:

1. **When did the successor become the only legitimate world-level controller?**
2. **When was the live controller roster first enumerated?**
3. **When did convenience defaults widen the roster beyond deliberate designation?**
4. **When, if ever, was the roster intentionally narrowed for the named slice?**
5. **When were shadow-controller concerns introduced or cleared?**
6. **When, if ever, did the strongest honest sentence become `single accountable controller for named slice only`?**

## Event rendering rules

- Every event must show whether it expands, preserves, narrows, or clouds controller accountability.
- Every event must show whether it is direct, delegated, architectural, or shadow in effect.
- Every event must show whether it affects named slice only or broader world scope.
- Contradiction events must remain visible even after later repair.

## Hard rules

The timeline must never let:

- `predecessor retired` erase later controller expansion inside the successor world
- `one owner designated` erase linked-family automatic ownership
- `delegation revoked` erase remembered approval expansion
- `local only` erase practical shadow authority
- `controller narrowed` erase blocked stronger universal sentences
''',
    '2013-remedy-hardening-attestation-successor-controller-roster-lineage-receipt-page-controller-set-delegation-state-and-blocked-single-controller-sentences-interface-spec.md': '''# Remedy-hardening-attestation successor controller roster lineage receipt page — controller set, delegation state, and blocked single-controller sentences

## Purpose

This page is the compact receipt a product can carry forward after reviewing who inside the successor world may still act.
It exists so downstream users can quote one durable object instead of reconstructing controller accountability from owner defaults, linked-device approval behavior, and local-derivative caveats.

## Receipt body

Every successor-controller-roster receipt must contain:

- receipt identifier
- successor-controller-roster case identifier
- source predecessor-authority-retirement receipt identifier
- successor world identifier
- governed slice identifier
- current controller-roster completeness class
- current live controller count or quorum class
- current delegation-depth class
- current auto-expansion exposure state
- current shadow-controller state
- current controller-minimization class
- highest honest public sentence
- strongest blocked stronger sentence
- specific contradiction set that blocks the stronger sentence
- next evidence needed for upgrade
- downgrade trigger set
- receipt issue time
- receipt expiry or mandatory re-review horizon

## Allowed highest honest public sentences

The receipt may expose sentences such as:

- successor exclusive world, controller roster not yet reviewed
- broad linked-family controller roster active
- controller roster enumerated, delegation still broad
- named-slice controller roster intentionally narrowed only
- shadow-controller risk present, stronger accountability blocked
- bounded controller quorum achieved for named slice only
- single accountable controller achieved for named slice only
- broader stronger single-controller claim blocked

## Forbidden upgrades

The receipt must never allow:

- `single accountable controller` without a visible slice or scope
- `controller roster minimized` when architectural auto-expansion remains live
- `no shadow controller risk` when derivative surfaces remain unresolved
- `one owner` when other linked devices still act as Owners
- `delegation closed` when remembered approvals or further delegation remain possible

## Receipt downgrade triggers

The receipt must automatically become stale or downgraded when:

- a new linked device inherits Owner-like authority automatically
- any controller uses an approval or share surface outside the reviewed narrow roster
- remembered approval expands trust to a new controller instance
- a derivative local surface creates fresh practical control
- an unresolved or historical controller reappears as live
- new evidence shows the roster was incomplete or the delegation chain was longer than stated
'''
}

for name, content in new_files.items():
    (docs / name).write_text(content + '\n', encoding='utf-8')

readme_add = '''\n\n## Revision addendum after rev0477 — remedy hardening attestation successor controller roster, delegated authority, and shadow-controller discipline\n\nThis continuation archive advances the doctrine by tightening another concrete non-clone seam around **who inside the surviving world may still act after the predecessor is retired, and whether `exclusive successor control` really means one accountable controller set or instead hides a broad, convenience-expanded swarm of owners, approvers, and shadow controllers**.\nIt does eight things in one tranche:\n\n1. Continues the archive after rev0477 with a new page family centered on what happens *after* predecessor authority is retired but *before* the product should pretend the surviving controller set is narrow, intentional, and accountable.\n2. Tightens the non-clone line again: borrow Resilio's candor about Owner permissions, all linked devices acting as Owners, approval from any linked device with folder presence, remembered approval that can widen future trust, linked-device automatic full read-write access, manual Standard-folder detours for one read-only result, and local-share caveats; refuse any contract where the operator still has to reconstruct `who inside the successor world can actually act now?` from scattered ownership and convenience surfaces.\n3. Adds one new **Resilio evaluation** document focused on why current remedy-hardening-attestation-successor-controller-roster truth is still too fragmented to clone even though the ingredients are useful.\n4. Adds five new **interface specs** for successor-controller-roster contract sheet, review, proof, timeline, and lineage receipt.\n5. Makes one hard product decision explicit: **exclusive successor control is weaker than accountable controller minimization.**\n6. Makes another hard product decision explicit: **one surviving world is weaker than one deliberately bounded controller set inside that world.**\n7. Makes a third hard product decision explicit: **linked-family convenience, approval memory, and derivative local surfaces are authority expansion events and may not hide inside a single human label or an optimistic `still one owner` sentence.**\n8. Packages the result as another continuation archive whose new tranche makes the `controller roster / designation basis / delegation depth / auto-expansion / shadow controller / minimization / receipt` seam explicit in the reading order and page family.\n\nNew docs in this tranche:\n\n- `2008-resilio-remedy-hardening-attestation-successor-controller-roster-delegated-authority-and-shadow-controller-fragmentation-evaluation.md`\n- `2009-remedy-hardening-attestation-successor-controller-roster-contract-sheet-page-controller-set-delegation-budget-and-shadow-authority-interface-spec.md`\n- `2010-remedy-hardening-attestation-successor-controller-roster-review-page-is-the-successor-worlds-live-authority-set-narrow-accountable-and-intentionally-delegated-interface-spec.md`\n- `2011-remedy-hardening-attestation-successor-controller-roster-proof-page-controller-chain-delegation-scope-and-shadow-authority-ceiling-interface-spec.md`\n- `2012-remedy-hardening-attestation-successor-controller-roster-timeline-page-designate-delegate-expand-restrict-and-revoke-controller-events-interface-spec.md`\n- `2013-remedy-hardening-attestation-successor-controller-roster-lineage-receipt-page-controller-set-delegation-state-and-blocked-single-controller-sentences-interface-spec.md`\n'''

status_add = '''\n\n## rev0478 — successor controller roster, delegated authority, and shadow-controller discipline\n\nThis revision advances the doctrine after predecessor-authority retirement by making a further hard separation: **exclusive surviving-world control is still weaker than a narrow, accountable, intentionally designated controller set inside that surviving world**.\n\nWhat changed in this revision:\n\n- added a new Resilio evaluation focused on successor-side controller sprawl, delegated authority, and shadow-controller risk\n- added five new interface-spec pages for controller-roster contract sheet, review, proof, timeline, and lineage receipt\n- froze a harder product line: `exclusive successor control` may not impersonate `single accountable controller`\n- elevated linked-family ownership expansion, approval memory, and local derivative authority into first-class expansion events instead of convenience details\n- pushed the interface spec toward explicit controller rosters, designation basis, delegation depth, auto-expansion exposure, minimization class, and blocked stronger accountability sentences\n\nNew docs in this revision:\n\n- `2008-resilio-remedy-hardening-attestation-successor-controller-roster-delegated-authority-and-shadow-controller-fragmentation-evaluation.md`\n- `2009-remedy-hardening-attestation-successor-controller-roster-contract-sheet-page-controller-set-delegation-budget-and-shadow-authority-interface-spec.md`\n- `2010-remedy-hardening-attestation-successor-controller-roster-review-page-is-the-successor-worlds-live-authority-set-narrow-accountable-and-intentionally-delegated-interface-spec.md`\n- `2011-remedy-hardening-attestation-successor-controller-roster-proof-page-controller-chain-delegation-scope-and-shadow-authority-ceiling-interface-spec.md`\n- `2012-remedy-hardening-attestation-successor-controller-roster-timeline-page-designate-delegate-expand-restrict-and-revoke-controller-events-interface-spec.md`\n- `2013-remedy-hardening-attestation-successor-controller-roster-lineage-receipt-page-controller-set-delegation-state-and-blocked-single-controller-sentences-interface-spec.md`\n'''

eval_add = '''\n\n## Revision addendum after rev0477 — why remedy hardening attestation successor controller roster, delegated authority, and shadow-controller discipline now sit on the non-clone side\n\nCurrent official Resilio docs are still admirably candid that `the predecessor is retired`, `the successor world is now the only legitimate world`, `all your devices are linked`, `someone can approve from any convenient place`, and `there is still one owner in spirit` are not one flat controller-accountability truth.\n`User Management` still says only Owners can invite new users and revoke access rights from other peers, and that when you share across your own linked devices all of your devices act as Owners.\n`Sync Private Identity & Linking My Devices` still says all folders automatically become available on all linked devices, approvals can be issued from any device where the folder is present, and a remote user may choose to automatically approve all of your linked devices for future sharing.\n`Sync functionality in detail` still says linked devices share one common folder list and that approvals can be made from any linked device instead of only the original sharer.\n`Comprehensive guide to syncing (Desktop-Desktop)` still says linked-device mode gives automatic full read-write access while manual sharing is the lane where privileges are chosen per folder.\n`How to create a Read Only folder while syncing across linked devices?` still says linked-device syncing gives Owner permission by default and that a read-only result on a linked device requires a Standard-folder manual-key detour.\n`Sharing a folder locally` still says local shares cannot receive Owner permission, inherit only the source permission level, cannot have their access level changed through user management, and may need remove-and-re-share for permission changes.\n`Folder Types and Management` still says Owner, Read & Write, Read Only, pending, disconnected, selective, and full states are materially different operating states rather than one flat ownership status.\n\nThis is strong controller-ingredient candor.\nIt is also exactly why AnonSync should not clone the present contract.\nOne ordinary answer to `who inside the surviving world can actually act now, who may further delegate, and is the live controller set narrow enough that one accountable actor can honestly speak for it?` still depends on combining Owner semantics, linked-device defaults, any-device approvals, future auto-approval memory, manual read-only detours, local-share caveats, and folder-state lore.\n\nSo this tranche freezes a stronger replacement line: **controller roster, designation basis, delegation chain, auto-expansion exposure, derivative local authority, shadow-controller suspicion, controller minimization class, and blocked stronger single-controller sentence become separate modeled truths.**\n\nThat is why this revision adds five more first-class pages: **Remedy-hardening-attestation-successor-controller-roster contract sheet**, **successor-controller-roster review**, **successor-controller-roster proof**, **successor-controller-roster timeline**, and **successor-controller-roster lineage receipt**.\n'''

sources_add = '''\n\n## rev0478 source set — remedy hardening attestation successor controller roster, delegated authority, and shadow-controller discipline\n\nThe most load-bearing source set for this pass was:\n\n- Resilio's current `User Management` article, which still says only Owners can invite new users and revoke access rights from other peers, and that when you share across your own linked devices all of your devices act as Owners.\n- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says all folders automatically become available on all linked devices, approvals can be issued from any device where the folder is present, and a remote user may choose to automatically approve all your linked devices for future sharing.\n- Resilio's current `Sync functionality in detail` article, which still says linked devices share one common folder list and approvals can be made from any linked device instead of only the original sharer.\n- Resilio's current `Comprehensive guide to syncing (Desktop-Desktop)` article, which still says linked-device mode grants automatic full read-write access while manual sharing is the lane where explicit privileges are chosen per folder.\n- Resilio's current `How to create a Read Only folder while syncing across linked devices?` article, which still says linked-device syncing grants Owner permission by default and that read-only on a linked device requires a Standard-folder manual-key detour.\n- Resilio's current `Sharing a folder locally` article, which still says local shares cannot receive Owner permission, inherit only the source permission level, cannot have their access changed through user management, and may require remove-and-re-share to change permissions.\n- Resilio's current `Folder Types and Management` article, which still says Owner, Read & Write, Read Only, pending, disconnected, selective, and full states are materially different operating states.\n\nThose sources were enough to tighten the line again:\n\n- current Resilio still deserves credit for candid authority ingredients\n- but current Resilio still answers `who inside the surviving world can actually act now, and is that controller set narrow enough to deserve a strong accountability sentence?` too diffusely\n- AnonSync should therefore prefer explicit remedy-hardening-attestation-successor-controller-roster sheets, successor-controller-roster reviews, successor-controller-roster proofs, successor-controller-roster timelines, and durable successor-controller-roster lineage receipts over overloaded identity labels, owner defaults, convenience approvals, manual detours, and local-share caveats\n\nPrimary sources:\n\n- User Management\n  https://help.resilio.com/hc/en-us/articles/205471375-User-Management\n\n- Sync Private Identity & Linking My Devices\n  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices\n\n- Sync functionality in detail\n  https://help.resilio.com/hc/en-us/articles/204754389-Sync-functionality-in-detail\n\n- Comprehensive guide to syncing (Desktop-Desktop)\n  https://help.resilio.com/hc/en-us/articles/204754939-Comprehensive-guide-to-syncing-Desktop-Desktop\n\n- How to create a Read Only folder while syncing across linked devices?\n  https://help.resilio.com/hc/en-us/articles/206216565-How-to-create-a-Read-Only-folder-while-syncing-across-linked-devices\n\n- Sharing a folder locally\n  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally\n\n- Folder Types and Management\n  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management\n'''

for path, addition in [
    (root / 'README.md', readme_add),
    (docs / '00-status.md', status_add),
    (docs / '10-resilio-sync-evaluation.md', eval_add),
    (docs / 'sources.md', sources_add),
]:
    text = path.read_text(encoding='utf-8')
    if addition.strip() not in text:
        path.write_text(text.rstrip() + addition + '\n', encoding='utf-8')
