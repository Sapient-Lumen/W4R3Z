from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / 'docs'

files = {
'1252-resilio-cohort-census-live-set-historical-roster-and-source-capability-fragmentation-evaluation.md': r'''# Resilio cohort-census, live-set, historical-roster, and source-capability fragmentation evaluation

## What current official docs still make clear

Another current Resilio pass strengthens the archive's clone-veto line rather than weakening it.

Current official docs still say several things that are operationally real and worth borrowing:

- the main desktop view's `X of Y peers` does **not** mean one thing: current docs still say `X` is the number of online peers while `Y` is the total number of peers including offline peers
- the troubleshooting article for unsynced files sharpens that again: current docs still say `Y` is the number of peers that have **ever been connected** to the share and that gray peers in the list are disconnected
- the same desktop-view docs still say a peer that stays offline for 7 days gets disconnected from the folder, and that this threshold is configurable in power-user settings
- current device-list docs still say `Hide this device` only clears an offline record from view; it does not unlink the device, and the device reappears if it ever comes back online
- current synchronization-mode docs still say a linked-device folder may be visible in `Disconnected` mode without taking local space, and current folder-management docs still say disconnected folders may not even have a local folder path
- current local-share docs still say a local share counts as a peer, but it only connects to self and only pulls from or uploads to the parenting folder; it does not directly sync with remote peers

That is real candor.
It is useful product truth.

## What still should not be cloned

The operator is still asked to reconstruct several materially different questions from several different pages:

1. **how many participants are actually reachable right now?**
2. **how many rows are only historical roster residue?**
3. **which rows can currently serve bytes versus merely appear in the count?**
4. **which rows are only self-derived local branches rather than independent remote coverage?**
5. **which rows were hidden for decluttering and can still return on their own later?**

Current Resilio docs still spread those answers across the main view, troubleshooting, identity cleanup, synchronization-mode, and local-share guidance.

So a user can learn all the pieces and still not get one stable product answer to:

> when the product says `3 of 7 peers`, who is actually live, who merely belongs to historical memory, who can currently provide bytes, who is only a self-derived local branch, and what stronger sentence about real redundancy is still blocked?

That page-contract gap is exactly why AnonSync should not clone the behavior.

## Why this matters for AnonSync

AnonSync should borrow five habits directly:

- **say openly whether a count is live, historical, visible, source-capable, or authority-capable**
- **say openly when local self-derived branches inflate the cohort without adding independent remote resilience**
- **say openly when a row is merely hidden from view rather than severed from trust**
- **say openly when auto-expiry moved a peer out of the live set without deleting historical evidence**
- **say openly when disconnected visibility still preserves a future reconnection lane but not current byte availability**

But AnonSync should reject five weaker habits:

- one `X of Y peers` counter that silently mixes reachability and historical membership
- peer lists that let self-only local branches look like independent redundancy
- gray/offline/disconnected rows that do not publish whether they are still eligible to return automatically
- roster cleanup actions that sound like reality cleanup rather than view cleanup
- source-availability claims derived from total peer count instead of current source-capable witness

## Replacement pages added for this seam

This revision therefore adds six narrower replacement pages:

- `1253` — Cohort census contract sheet
- `1254` — Roster membership review
- `1255` — Live capability proof
- `1256` — Cohort drift timeline
- `1257` — Cohort census lineage receipt

These pages keep the Resilio candor and reject the scattered-cohort-semantics problem.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that online peers, ever-seen peers, disconnected gray rows, hidden offline devices, disconnected linked folders, and self-only local branches are different truths; refuse any interface contract where the operator must reconstruct live reachability, real source coverage, and historical roster residue from several counters and help articles instead of one explicit cohort-census object.
''',
'1253-cohort-census-contract-sheet-page-live-set-historical-roster-source-subset-and-row-visibility-interface-spec.md': r'''# Cohort census contract sheet page: live set, historical roster, source subset, and row visibility interface spec

## Purpose

The archive already has pages for reachability provenance, presence, effective seat posture, detachment, and stale-peer debt.
What it still lacked was one ordinary page for the narrower question:

> when the interface shows a peer count or participant list, what exactly is being counted, who is merely historical, who can currently provide bytes, and what stronger redundancy sentence is still blocked?

Current official Resilio docs make this seam concrete.
They separately describe `X of Y peers`, ever-connected totals, disconnected gray rows, hidden offline devices, disconnected linked folders, and self-only local shares that still grow the peer count.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Cohort census contract sheet** whenever a subject publishes a participant count, a participant list, or any sentence implying coverage, redundancy, or collaborator presence.

The sheet exists to answer six things in one place:

1. what population is being counted
2. what subset is live right now
3. what subset is currently source-capable
4. what subset is authority-capable or mutation-capable
5. what rows are only visible or historical residue
6. what stronger cohort sentence remains blocked

## Fixed page order

1. **Cohort header**
2. **Population classes card**
3. **Current live-and-source card**
4. **Historical / hidden / detached residue card**
5. **Coverage and redundancy verdict card**
6. **Action rail and blocked stronger sentence**

### 1) Cohort header

Show at minimum:

- `cohort_census_id`
- subject ref
- last roster witness time
- strongest safe sentence
- blocked stronger sentence
- current row-visibility basis
- current counting basis version

Supported population classes must include:

- `live-reachable-set`
- `historical-roster`
- `visible-ui-rows`
- `source-capable-subset`
- `authority-capable-subset`
- `self-derived-local-branches`
- `unknown`

Example safe sentence:

- `7 roster members are known, but only 3 are live now and only 2 are currently witnessed as source-capable independent peers.`

### 2) Population classes card

Show explicit counts for at least:

- live reachable participants
- offline but still rostered participants
- auto-expired / disconnected participants
- hidden offline participants
- self-derived local branches
- disconnected visibility rows
- source-capable independent participants
- authority-capable participants

Every row must show:

- `count`
- `evidence freshness`
- `membership basis`
- `whether the class contributes to redundancy`

The operator must be able to answer:

> what universe is this number referring to?

### 3) Current live-and-source card

Separate these current truths explicitly:

- reachable now
- source-capable now
- mutation-capable now
- serve-eligible now
- only-visible-not-live
- unknown

Every row must show:

- witness source
- freshness
- whether the row is independent or self-derived
- whether the row can actually satisfy current fetches or repairs

The operator must be able to answer:

> who is not just counted, but actually useful right now?

### 4) Historical / hidden / detached residue card

Separate these residue classes explicitly:

- ever-seen roster members
- disconnected gray rows
- auto-expired rows
- hidden-for-declutter rows
- disconnected linked-folder visibility rows
- removed / severed rows that no longer belong in the cohort

Each row must show whether it can:

- reappear automatically
- reconnect without new grant
- provide bytes now
- count toward resilience claims

The operator must be able to answer:

> which rows are memory, not coverage?

### 5) Coverage and redundancy verdict card

This card must answer five separate questions:

1. do we currently have at least one source-capable peer?
2. do we currently have more than one **independent** source-capable peer?
3. is the apparent multiplicity only self-derived local fanout?
4. is the roster mostly historical residue rather than live availability?
5. what claim ceiling applies right now?

Supported verdicts must include:

- `single-source-live`
- `multi-source-independent-live`
- `live-but-self-derived-inflated`
- `historical-heavy-live-light`
- `no-live-source-witness`
- `unknown`

### 6) Action rail and blocked stronger sentence

Allowed examples:

- `Show live set only`
- `Show source-capable independent peers`
- `Reveal hidden roster rows`
- `Export cohort receipt`
- `Open drift timeline`

Blocked examples:

- `Claim safe redundancy` when only self-derived local branches inflate the count
- `Claim no remaining peer risk` when hidden or auto-returning rows still exist
- `Claim healthy swarm` when only historical roster evidence exists

## Field vocabulary

Use these exact field names where practical:

- `live_reachable_count`
- `historical_roster_count`
- `visible_row_count`
- `source_capable_independent_count`
- `authority_capable_count`
- `self_derived_branch_count`
- `auto_returning_hidden_count`
- `counting_basis_summary`
- `redundancy_claim_ceiling`

## Hard rules

- no peer counter may appear without an adjacent `counting basis` drill-in
- historical roster rows must never silently count as current redundancy
- self-derived local branches must never silently count as independent resilience
- hidden rows must never silently imply severance
- the strongest safe sentence must be printed before any optimism badge or health color
''',
'1254-roster-membership-review-page-ever-seen-online-disconnected-hidden-and-self-derived-branches-interface-spec.md': r'''# Roster membership review page: ever-seen, online, disconnected, hidden, and self-derived branches interface spec

## Problem this page solves

A participant row can mean several different things:

- live and reachable now
- offline but still a known roster member
- auto-expired or disconnected after dormancy
- hidden from the list for decluttering only
- self-derived local branch that does not add remote resilience
- disconnected linked-folder visibility row with no current path or bytes

When those meanings are collapsed, the operator cannot tell whether the roster is a coverage map, a memory ledger, or just a cluttered mixture of both.

## Review trigger

Open this page whenever any of the following are true:

- the subject publishes `X of Y peers`
- the operator asks whether there is enough redundancy
- the roster contains gray, hidden, or disconnected rows
- local shares or linked-device branches make the count look larger than the real independent cohort
- a troubleshooting path depends on whether a missing source is truly absent or only detached / hidden / historical

## Fixed review order

### A. Count sentence under review

Show:

- current public sentence being challenged
- displayed count
- screen / API surface that emitted it
- why the sentence may overstate or understate reality

### B. Membership buckets

Bucket every row into exactly one primary bucket:

- `live-independent`
- `live-self-derived`
- `offline-known`
- `disconnected-gray`
- `hidden-offline`
- `visibility-only-disconnected`
- `severed-no-longer-member`
- `unknown`

The page must never leave a row uncategorized.

### C. Automatic-return analysis

For every non-live row, publish:

- can it return automatically?
- does it require a new approval?
- was it hidden only, disconnected by timeout, or severed by explicit action?
- would its return change source coverage, only row visibility, or both?

### D. Independence analysis

For every live row, publish:

- independent remote seat or self-derived local branch
- source of data for this row
- whether it can seed other remote peers directly
- whether it merely fans out the same parent source locally

### E. Safer replacement sentences

Generate three sentences:

1. **visible-row sentence**
2. **live-set sentence**
3. **independent-source sentence**

Example:

- `7 rows are visible in the cohort history.`
- `3 rows are live now.`
- `2 live rows are independent source-capable peers; 1 additional live row is self-derived local fanout.`

## Review outputs

The page must produce:

- revised counts by bucket
- automatic-return map
- independence map
- source-capability warning if only one independent source remains
- one `blocked stronger sentence`

## CLI / API hints

- `anonsync cohort review --subject vault --basis visible-rows`
- `anonsync cohort review --subject vault --split independence`
- `anonsync cohort review --subject vault --show auto-return`

## Hard rules

- `ever seen` may never be rendered as if it were `live now`
- `hidden` may never be rendered as if it were `removed`
- `live` may never be rendered as if it implied `independent`
- `count > 1` may never be rendered as if it implied `multi-source resilience`
''',
'1255-live-capability-proof-page-online-source-capable-authority-capable-and-serve-eligible-evidence-interface-spec.md': r'''# Live capability proof page: online, source-capable, authority-capable, and serve-eligible evidence interface spec

## Purpose

The cohort contract sheet explains what the counts mean.
This proof page exists for the narrower question:

> which current rows can actually do something useful right now?

`Online` is not enough.
A participant may be online yet not be source-capable for the byte you need, may not have mutation authority, or may be a self-derived local branch rather than an independent resilience contributor.

## Proof outputs

The page must separately prove four things:

1. `online_now`
2. `source_capable_now`
3. `serve_eligible_now`
4. `authority_capable_now`

Each claim must be independently evidencable and independently fail.

## Evidence classes

Supported evidence classes must include:

- current transport witness
- current byte-presence witness
- current subject-binding witness
- current seat-posture witness
- self-derived lineage witness
- stale roster only
- unknown

## Fixed proof order

### 1. Candidate row table

For every row under proof, show:

- row handle
- live status
- independent vs self-derived
- source-capable verdict
- serve-eligible verdict
- authority-capable verdict
- evidence freshness
- blocked stronger sentence

### 2. Online proof

Online proof requires:

- current reachability witness
- freshness timestamp
- route witness grade

Online proof does **not** by itself prove byte availability or source usefulness.

### 3. Source-capability proof

Source-capability proof requires:

- byte-presence witness or materialization witness
- subject membership still valid
- no stronger contradictory evidence such as ghost status or detached-only visibility

### 4. Serve-eligibility proof

Serve-eligibility proof requires:

- current reachability witness
- source-capability proof
- seat posture that still allows byte serving
- no current local suspension or equivalent serve block known to the product

### 5. Authority-capability proof

Authority-capability proof requires:

- seat posture proof
- governance / grant proof
- no current detachment or revocation proof overriding it

## Supported verdict vocabulary

For each capability, use:

- `proved`
- `not-proved`
- `contradicted`
- `stale`
- `unknown`

## Example safe sentences

- `Peer amber is online now, but source capability for this subject is not proved.`
- `Peer cedar is source-capable and serve-eligible now, but it is a self-derived local branch and does not add independent remote resilience.`
- `Peer slate remains authority-capable in roster history, but live reachability is stale.`

## Hard rules

- `online` must never imply `source-capable`
- `source-capable` must never imply `authority-capable`
- `serve-eligible` must never imply `independent`
- proof freshness must be shown next to every capability claim
''',
'1256-cohort-drift-timeline-page-live-count-history-expiry-hide-and-reentry-triggers-interface-spec.md': r'''# Cohort drift timeline page: live-count history, expiry, hide, and reentry triggers interface spec

## Problem this page solves

A cohort rarely changes only by explicit adds and removals.
It also drifts through:

- peers going offline
- auto-disconnect after dormancy thresholds
- rows hidden for decluttering
- local-share fanout increasing apparent count
- disconnected linked-folder visibility rows appearing
- later reentry of previously hidden or offline participants

The operator needs one place to see how the cohort sentence drifted over time.

## Timeline events this page must preserve

Supported event classes must include:

- `peer-became-live`
- `peer-went-offline`
- `peer-auto-expired-or-disconnected`
- `row-hidden-for-declutter`
- `row-reappeared-on-return`
- `self-derived-branch-added`
- `visibility-only-row-created`
- `severance-confirmed`
- `counting-basis-changed`

## Fixed timeline columns

- event time
- affected row or cohort slice
- previous bucket
- next bucket
- changed counters
- did independent source count change?
- did only visible row count change?
- reopen trigger if the operator made a prior conclusion

## Required summary cards

### A. Live-count drift

Shows how `live_reachable_count` changed over time.

### B. Historical-roster drift

Shows how `historical_roster_count` changed over time.

### C. Independent-source drift

Shows whether real resilience changed or only the apparent count changed.

### D. Reopen triggers

Lists prior receipts or claims that should be reconsidered because of:

- hidden row reappearance
- auto-expiry of a source-capable peer
- new self-derived branch making the count look safer than it is
- return of a formerly offline source peer

## Example safe sentences

- `Visible row count increased from 4 to 5, but independent source count stayed at 1 because the new row is self-derived local fanout.`
- `Historical roster count stayed at 7 while live set fell from 3 to 1 after two peers crossed the dormancy threshold.`
- `A previously hidden offline device reappeared; this changed row visibility and potential future reachability, but live source coverage is still unproved.`

## Hard rules

- no timeline may plot a single `peer count` line without also plotting independent source count
- hide/show actions must be marked as visibility drift, not resilience drift
- local-branch adds must be marked as fanout drift, not independent cohort growth
''',
'1257-cohort-census-lineage-receipt-page-live-set-roster-basis-and-capability-ceiling-interface-spec.md': r'''# Cohort census lineage receipt page: live set, roster basis, and capability ceiling interface spec

## Purpose

The contract sheet explains the cohort now.
The review and proof pages explain why.
This receipt preserves the specific answer that was safe at one moment.

It exists so later operators can answer:

> what exactly did we mean by the participant count at this time, and what stronger resilience sentence did we refuse to make?

## Receipt sections

1. **Header**
2. **Counting basis snapshot**
3. **Current capability snapshot**
4. **Historical / hidden residue snapshot**
5. **Blocked stronger sentence**
6. **Reopen triggers**

### 1) Header

Show:

- `cohort_receipt_id`
- subject ref
- issued_at
- operator / actor
- strongest safe sentence

### 2) Counting basis snapshot

Must preserve at least:

- `live_reachable_count`
- `historical_roster_count`
- `visible_row_count`
- `source_capable_independent_count`
- `authority_capable_count`
- `self_derived_branch_count`
- `counting_basis_summary`

### 3) Current capability snapshot

For each named critical row, preserve:

- online proof grade
- source-capable grade
- serve-eligible grade
- authority-capable grade
- independence class

### 4) Historical / hidden residue snapshot

Preserve:

- hidden rows that can reappear automatically
- disconnected gray rows
- visibility-only disconnected rows
- auto-expired rows
- severed rows excluded from the cohort

### 5) Blocked stronger sentence

Examples:

- `We did not claim multi-source resilience because only one independent source-capable peer was proved live.`
- `We did not claim the hidden roster was gone because those rows could reappear automatically.`
- `We did not claim five peers added five-way redundancy because two rows were self-derived local branches.`

### 6) Reopen triggers

A receipt must declare it stale and reopen if any of these happen:

- a hidden row returns online
- a live independent source-capable row goes stale or auto-expires
- a self-derived branch is mistaken for independent redundancy by a later surface
- counting-basis logic changes
- detachment / revocation changes cohort membership

## Hard rules

- receipts must preserve both the displayed count and the counting basis
- receipts must preserve independence class for every row used in a resilience claim
- receipts must preserve the blocked stronger sentence verbatim
- receipts must never summarize `3 of 7 peers` without the typed expansion
'''
}

status_addendum = r'''## Revision addendum — cohort census, live-set truth, and historical-roster semantics after rev0351

This tranche locks the next seam around **cohort census and participant-count truth**.
The key decisions now made explicit in the archive are:

- **cohort census is a first-class contract object rather than a side effect of one `X of Y peers` badge**
- **live-reachable set, historical roster, visible rows, source-capable subset, authority-capable subset, and self-derived local branches are different truths**
- **`online` is weaker than `source-capable`, and `source-capable` is weaker than `independent redundancy`**
- **hidden-for-declutter is weaker than removed, and disconnected gray row is weaker than severed membership absence**
- **every serious participant-count claim now needs one receipt that preserves counting basis, live/source split, independence class, residue rows, and the blocked stronger sentence**

New docs added in this tranche:

- `1252-resilio-cohort-census-live-set-historical-roster-and-source-capability-fragmentation-evaluation.md`
- `1253-cohort-census-contract-sheet-page-live-set-historical-roster-source-subset-and-row-visibility-interface-spec.md`
- `1254-roster-membership-review-page-ever-seen-online-disconnected-hidden-and-self-derived-branches-interface-spec.md`
- `1255-live-capability-proof-page-online-source-capable-authority-capable-and-serve-eligible-evidence-interface-spec.md`
- `1256-cohort-drift-timeline-page-live-count-history-expiry-hide-and-reentry-triggers-interface-spec.md`
- `1257-cohort-census-lineage-receipt-page-live-set-roster-basis-and-capability-ceiling-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `3 of 7 peers` can no longer hide whether the `7` are live, merely ever-seen, disconnected gray rows, hidden devices, or self-derived local fanout
- roster review now keeps auto-returning hidden rows adjacent to the live set instead of letting declutter masquerade as severance
- source-coverage review now separates `reachable`, `source-capable`, and `independent resilience` instead of deriving all three from one count
- local-share fanout can no longer silently inflate redundancy claims
- later operators can open one receipt and see what the cohort count actually meant here, who could really help now, what rows were only history or visibility residue, and which stronger resilience sentence the product still refused to make

'''

for name, content in files.items():
    (DOCS / name).write_text(content.strip() + '\n', encoding='utf-8')

status_path = DOCS / '00-status.md'
old = status_path.read_text(encoding='utf-8')
if not old.startswith(status_addendum):
    status_path.write_text(status_addendum + old, encoding='utf-8')
