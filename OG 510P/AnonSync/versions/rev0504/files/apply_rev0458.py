from pathlib import Path

root = Path('/mnt/data/work_rev0457')
docs = root / 'docs'

new_docs = {
    '1888-resilio-remedy-hardening-attestation-revocation-delivery-acknowledgement-and-stale-surface-suppression-fragmentation-evaluation.md': '''# Resilio remedy hardening attestation revocation delivery, acknowledgement, and stale-surface-suppression fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for being candid that spread is real, authority can move quickly, and old state can survive even after one operator action seems to close the story.
That candor matters.

The strongest present ingredients are:

- current `Sync Private Identity & Linking My Devices` docs still say linked devices automatically make all folders available everywhere and approvals can be issued from any linked device where the folder is present
- current `User Management` docs still say permissions can be modified on the fly and all linked devices under one identity act as Owners
- current `Disconnecting and Removing Folders` docs still say disconnect only affects one device while the folder remains in the file system and accessible through a file browser
- current `Folder Types and Management` docs still say pending folders may auto-connect after prior approval and disconnected folders remain visible for later action
- current `Sync Main View (Desktop)` docs still say the ordinary UI evidence horizon is a 30-day History surface and a peer list whose offline peers disconnect after 7 days
- current `Collecting debug logs automatically` docs still say deeper evidence often requires enable, restart, reproduce, and wait
- current `Using Archive for file versioning and restoring deleted files` docs still say older or deleted copies can persist in Archive and only manual restoring is possible
- current `Running Sync in configuration mode` docs still say one configuration can be applied across a number of different machines
- current `Cloning Sync` docs still say unsupported copies can create strange behavior and non-transferring twins

## Where the current contract still fragments

The problem is not that Resilio hides spread or residue.
The problem is that it still does not produce a first-class, case-scoped **revocation delivery and closure** object.

Today an operator can often infer only weaker truths such as:

- a permission was lowered or a folder was disconnected somewhere
- a linked device probably also saw the change because linked devices share ownership authority
- some pending or disconnected instance may reconnect later
- some local bytes still remain on disk after disconnect
- some old version may still exist in Archive
- some event probably appeared in short-horizon History
- some deeper proof may exist, but only if logs were captured after a restart in time
- some cohort probably got configuration changes at next start
- some weird residual state may exist if there was instance cloning or fresh-instance repair

Those are useful clues.
They are not the same as an explicit answer to `did the revocation, revalidation request, or successor-binding actually reach every named dependent, was it acknowledged by the reachable dependents, were stale derivative surfaces suppressed, and which unreachable or unverifiable dependents still keep the old ruling effectively live?`

## Why that matters for AnonSync

AnonSync needs stronger post-revocation truth than `a wave was opened` or `notifications were sent`.
It needs to support claims such as:

- the revocation order exists, but only two of six registered consumers were reachable on a callback path
- all reachable consumers acknowledged receipt, but one stale export remains externally live and cannot yet be suppressed
- new reliance is frozen, three dashboards are hidden, and one downstream receipt is still pending successor reseal
- the original source is historical only for internal consumers, but not yet historical only for external consumers because one delivery channel is unverifiable
- the product cannot honestly say `downstream safe again` because one previously registered consumer has not acknowledged and one disconnected lane may reconnect later
- the product can separately certify `delivered`, `acknowledged`, `suppressed`, `resealed`, and `still residually live` instead of hiding them inside one optimistic badge

AnonSync therefore needs first-class objects for **callback reachability, delivery coverage, acknowledgement coverage, stale-surface suppression, unreachable-dependent risk, escalation owner, closure threshold, and residual-live-surface class** rather than leaving operators to reconstruct closure from permission changes, disconnects, pending folders, short history, archives, startup config, and support capture folklore.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `did the old ruling truly stop being live everywhere that mattered?` — only by making the operator combine several partially overlapping operational surfaces:

- linked-device spread and approval from any linked device
- live permission mutation and owner topology
- disconnect that leaves local bytes present
- pending and disconnected folders that can later reconnect or stay visible
- short-horizon UI surfaces and peer expiry
- Archive residue and manual restore paths
- startup config rollout across multiple machines
- restart-gated debug evidence and clone ambiguity

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **revocation delivery and closure** directly.
Its interface family should let the product separate at least these truths:

- revocation required
- callback path known
- delivery attempted
- delivery confirmed
- acknowledgement received
- successor receipt accepted
- stale surface suppressed
- external stale copy still live
- unreachable dependent risk open
- closure threshold met for named cohort only
- global downstream-safe sentence still blocked
- residual-live-surface debt preserved for later escalation

That is why this revision adds five more first-class pages:
**Remedy-hardening-attestation-revocation-delivery contract sheet**, **Remedy-hardening-attestation-revocation-delivery review**, **Remedy-hardening-attestation-revocation-delivery proof**, **Remedy-hardening-attestation-revocation-delivery timeline**, and **Remedy-hardening-attestation-revocation-delivery lineage receipt**.
''',
    '1889-remedy-hardening-attestation-revocation-delivery-contract-sheet-page-callback-reachability-ack-coverage-and-suppression-owner-interface-spec.md': '''# Remedy-hardening-attestation-revocation-delivery contract sheet page — callback reachability, acknowledgement coverage, and suppression owner

## Purpose

This page is the operator's compact contract for a ruling whose downstream reliance graph already exists and now needs an explicit answer to whether the corrective wave actually reached the dependents, whether reachable dependents acknowledged, whether stale derivative surfaces were suppressed, and who still owns closure when some dependents remain unreachable or unverifiable.
It exists so the product can distinguish `revocation wave opened` from `delivery happened, acknowledgement happened where required, stale surfaces were suppressed, and the remaining residual risk is honestly named`.

## Core fields

- case identifier
- source reliance receipt identifier
- source revocation-wave identifier
- current governing receipt identifier
- current source sentence status
- current delivery-governance class
- current stale-surface class
- freeze-new-reliance flag
- reachable dependent count
- unreachable dependent count
- delivery-confirmed count
- acknowledgement-required count
- acknowledgement-received count
- successor-binding-required count
- successor-binding-complete count
- stale artifact count
- stale artifact suppressed count
- external stale artifact count
- disconnected-or-return-risk count
- unknown callback path risk grade
- last delivery attempt time
- last acknowledgement time
- oldest unsuppressed stale surface time
- closure threshold class
- delivery owner class
- acknowledgement owner class
- suppression owner class
- escalation owner class
- strongest blocked all-clear sentence
- strongest blocked historical-only-everywhere sentence
- next evidence that upgrades closure confidence
- next evidence that forces escalation now

## Delivery-governance classes

The page must model at least these distinct classes:

- revocation required, callback paths incomplete
- callback paths known, delivery not yet attempted
- delivery attempted, confirmation incomplete
- delivered to reachable cohort, acknowledgement pending
- delivered and acknowledged, suppression incomplete
- suppression complete for named cohort, external closure still open
- successor-bound and suppressed for required cohort
- residual-live-surface debt preserved, escalation active
- downstream-safe restored for named cohort only
- global downstream-safe sentence blocked

## Dependent classes

The page must support at least these consumer or stale-surface classes:

- internal automation with callback path
- external automation with callback path
- human decision maker
- dashboard or status surface
- exported file or packet
- downstream receipt quoting the source
- policy or template derived from the source
- disconnected or pending lane that may later return
- externally mirrored artifact without callback path

## Required distinctions

The page must keep these truths separate:

- registry known versus callback path known
- delivery attempted versus delivery confirmed
- delivery confirmed versus acknowledgement received
- acknowledgement received versus stale artifact suppressed
- successor receipt issued versus successor receipt bound by the dependent
- stale local residue versus publicly live stale surface
- named-cohort closure versus global closure
- historical-only source for one audience versus historical-only source everywhere

## Layout

The page should be organized into seven zones:

### 1) Governing correction rail

Always print:

- the current governing receipt
- whether new reliance is frozen
- the strongest blocked all-clear sentence
- the strongest blocked `historical only everywhere` sentence
- the exact reason each stronger sentence is blocked

### 2) Reachability rail

Show a table with at least these columns:

- dependent identifier
- dependent class
- callback path class
- last reachable time
- last confirmed delivery time
- acknowledgement requirement
- acknowledgement status
- successor-binding requirement
- stale-surface status
- current escalation status

The page must never collapse `registered`, `reachable`, `delivered`, `acknowledged`, and `suppressed` into one badge.

### 3) Delivery coverage rail

Show coverage as a ladder, not a binary:

- revocation required
- callback known
- delivery attempted
- delivery confirmed for reachable cohort
- acknowledgement complete for required cohort
- stale surfaces suppressed for named cohort
- closure threshold met
- global closure proven

The active rung must be highlighted and each blocked rung must show the exact missing evidence.

### 4) Residual-live-surface rail

Show why broad closure may still be blocked:

- unreachable dependent with prior observed consumption
- disconnected or pending lane may later reconnect
- exported copy lacks callback path
- dashboard or publication still visible
- downstream receipt still quoting superseded source
- archive or local residue not yet evaluated
- clone or fresh-instance ambiguity
- evidence horizon expired before confirmation

### 5) Closure obligations rail

Show every active obligation with status:

- deliver corrective notice
- obtain acknowledgement
- bind successor receipt
- hide or retract stale surface
- revalidate dependent decision
- reseal downstream receipt
- escalate unreachable dependent
- declare residual risk preserved
- close wave only after threshold is met

Status values must include:

- not started
- in progress
- blocked
- confirmed
- waived by policy
- unverifiable

### 6) Ownership rail

Show exactly who owns each action class:

- callback-path owner
- delivery owner
- acknowledgement owner
- stale-surface suppression owner
- successor-binding owner
- escalation owner
- final closure approver

### 7) Actions rail

The page must support explicit actions such as:

- attach callback evidence
- issue delivery attempt
- record confirmation
- request acknowledgement
- bind successor receipt
- mark stale surface hidden
- mark artifact retracted
- escalate unreachable dependent
- preserve residual-live-surface debt
- close named-cohort wave

## Operator promises

The contract sheet must let the operator say things like:

- `all registered internal automations were delivered the correction, but one external export remains live without callback proof`
- `delivery is confirmed for the reachable cohort, yet acknowledgement remains incomplete for two human decision makers`
- `the source is historical only for internal consumers, not yet for external consumers`
- `named-cohort closure is complete, but global downstream-safe language remains blocked because one disconnected lane may later return`

## Hard decisions frozen by this page

This interface family makes these product decisions explicit:

- no broad `everyone got the correction` sentence without callback and delivery basis
- no `downstream safe again` sentence while any unsuppressed stale surface remains live
- no `historical only everywhere` sentence while any dependent still lacks confirmed successor binding or suppression
- no passive notification substitute for closure when the old source still appears on live downstream surfaces
''',
    '1890-remedy-hardening-attestation-revocation-delivery-review-page-did-the-revocation-or-revalidation-actually-reach-every-dependent-and-suppress-stale-surfaces-interface-spec.md': '''# Remedy-hardening-attestation-revocation-delivery review page — did the revocation or revalidation actually reach every dependent and suppress stale surfaces?

## Review question

Can the product honestly present this corrective wave as merely opened, delivered to the reachable cohort, acknowledged where required, closed for a named cohort, or still residually unsafe because stale surfaces remain live or some dependents cannot be verified?

## Review panels

### 1) Reachability review

Ask whether every dependent that previously relied on the source has a known callback path.
The review must preserve:

- callback path known and tested
- callback path inferred but untested
- callback path missing
- callback path stale or expired
- disconnected or pending lane that may later return

False upgrades to reject include:

- treating registry presence as proof of reachability
- treating one callback channel for one device as proof for all linked or derivative dependents

### 2) Delivery review

Ask what evidence proves that the corrective notice or successor-binding request actually reached the dependent.
The review must classify evidence at least as:

- queued only
- attempted
- transport-confirmed
- opened or fetched
- durable receipt from dependent owner
- successor binding observed

The page must reject `delivered` when the evidence only proves that a message was generated locally.

### 3) Acknowledgement review

Force the operator to decide which dependents merely need delivery and which require affirmative acknowledgement before the case can close.
The review must separate:

- notice-only dependents
- acknowledgement-required dependents
- successor-binding-required dependents
- revalidation-required dependents
- policy-waived acknowledgement cases

### 4) Stale-surface review

Force explicit review of every place the old ruling may still be live:

- dashboards or status pages
- exported packets
- mirrored external copies
- downstream receipts
- policy or template text
- disconnected local bytes that still inform users
- Archive or retained old versions

The review must reject any broad closure claim that outruns stale-surface evidence.

### 5) Residual-risk review

Force review of every reason the corrective wave may still be incomplete:

- unreachable dependent after prior consumption
- expired evidence horizon
- pending or disconnected lane may reconnect later
- clone or fresh-instance ambiguity
- external artifact without callback path
- acknowledgement requested but not returned
- suppression requested but not confirmed

### 6) Closure-threshold review

The page must land on explicit branches such as:

- wave opened, callback map incomplete
- delivered to reachable cohort only
- delivered and acknowledged, suppression pending
- named-cohort closure achieved
- external residual risk preserved
- global all-clear blocked
- downstream safe again for required cohort

### 7) Speakability review

The review must decide which sentence is honestly speakable now:

- `correction issued; delivery not yet proven`
- `delivered to reachable dependents only`
- `acknowledged by required internal dependents only`
- `stale surfaces suppressed for the named cohort`
- `external residual risk preserved; do not claim global closure`
- `downstream safe again for the required cohort only`

## Output states

The page must be able to land on at least these outputs:

- callback coverage incomplete
- delivery confirmed, acknowledgement incomplete
- acknowledgement complete, stale surfaces unsuppressed
- named cohort closed, external cohort unverifiable
- residual-live-surface debt preserved
- permanently blocked from `historical only everywhere` language
''',
    '1891-remedy-hardening-attestation-revocation-delivery-proof-page-delivery-acknowledgement-enforcement-and-residual-live-surface-floor-interface-spec.md': '''# Remedy-hardening-attestation-revocation-delivery proof page — delivery, acknowledgement, enforcement, and residual-live-surface floor

## Purpose

This page is the durable proof that revocation delivery and closure were evaluated under explicit reachability, delivery, acknowledgement, successor-binding, and stale-surface suppression rules.
It must let a later verifier see not only that a wave was opened, but whether the old ruling truly stopped being live across the required dependent cohort.

## Sections

### 1) Closure header

Publish:

- case identifier
- source reliance receipt identifier
- corrective-wave identifier
- current governing receipt identifier
- current delivery-governance class
- current stale-surface class
- closure threshold class

### 2) Reachability summary

List at least:

- total registered dependents
- reachable dependents by class
- unreachable dependents by class
- dependents with expired callback evidence
- dependents that may later reconnect
- dependents with no callback path by design

### 3) Delivery and acknowledgement table

For each dependent or dependent cohort print:

- dependent identifier or cohort label
- callback path class
- delivery evidence
- last confirmed delivery time
- acknowledgement requirement
- acknowledgement evidence
- successor-binding evidence
- current remediation status
- current escalation status

### 4) Stale-surface suppression map

The proof must print explicit results for each derivative surface:

- surface identifier
- surface class
- source sentence previously shown
- suppression action required
- suppression evidence
- successor receipt bound or not
- current live status
- residual audience still exposed or not

### 5) Closure obligation table

For each active obligation print:

- obligation identifier
- trigger event
- affected dependent or surface
- action required
- owner
- deadline or horizon
- completion evidence
- current status

Example proof outputs:

- `delivery attempted to all registered dependents; callback confirmation incomplete for one external automation`
- `all required internal dependents acknowledged, but one stale exported packet remains live`
- `successor receipt bound for all downstream receipts; dashboard suppression still pending`
- `named-cohort closure achieved; external residual risk preserved`

### 6) Safe-speak sentence ladder

The proof must print the sentence ladder explicitly:

- current governing sentence about closure
- strongest speakable named-cohort closure sentence
- strongest blocked global all-clear sentence
- strongest blocked `historical only everywhere` sentence

### 7) Claim ceilings

The page must explicitly forbid false upgrades such as:

- `everyone received the correction` when callback paths are incomplete
- `everyone acknowledged` when acknowledgement was not required or not evidenced for some dependents
- `the old ruling is gone everywhere` when any stale surface is still live
- `global downstream safe again` when external residual risk remains open
- `historical only everywhere` when successor binding or suppression is still incomplete
''',
    '1892-remedy-hardening-attestation-revocation-delivery-timeline-page-freeze-notify-ack-enforce-escalate-and-closeout-events-interface-spec.md': '''# Remedy-hardening-attestation-revocation-delivery timeline page — freeze, notify, acknowledge, enforce, escalate, and closeout events

## Purpose

This page is the chronological spine for revocation delivery and closure.
It exists to preserve the difference between opening a corrective wave, reaching dependents, receiving acknowledgement, suppressing stale surfaces, escalating unreachable dependents, and closing only the portion of the world that was actually proven safe again.

## Event classes

The timeline must support at least these event classes:

- new reliance frozen
- callback path registered
- callback path tested
- corrective notice issued
- delivery confirmed
- acknowledgement requested
- acknowledgement received
- successor receipt bound
- stale surface hidden or retracted
- dependent decision revalidated
- downstream receipt resealed
- unreachable dependent escalated
- reconnect risk re-opened
- named-cohort closure approved
- global closure blocked
- residual-live-surface debt preserved

## Required timeline columns

Every event row must print at least:

- event timestamp
- actor or subsystem
- event class
- affected dependent or surface
- prior closure class
- resulting closure class
- evidence attached
- whether the event upgrades speakability, only preserves history, or reopens risk

## Required chronology guarantees

The timeline must preserve:

- when freeze-new-reliance took effect relative to delivery attempts
- whether acknowledgement was requested before or after a stale surface was hidden
- whether successor binding preceded closure claims
- whether residual-live-surface debt was preserved before or after a named-cohort closure statement
- whether a later reconnect or callback expiry reopened the case

## Required timeline summaries

The page must compute and print:

- first corrective-wave issuance time
- first confirmed delivery time
- first required acknowledgement completion time
- first stale-surface suppression time
- last reopen or escalation time
- named-cohort closure time if any
- current oldest still-open obligation age

## Speakability rules

The timeline must not allow:

- `closed` before the first applicable delivery confirmation
- `acknowledged` before evidence of acknowledgement exists
- `historical only everywhere` before the last required stale surface is suppressed or explicitly preserved as residual risk
- `downstream safe again` without preserving any later reconnect or callback-expiry event that reopens the closure claim
''',
    '1893-remedy-hardening-attestation-revocation-delivery-lineage-receipt-page-delivery-coverage-stale-surface-suppression-and-blocked-stronger-sentences-interface-spec.md': '''# Remedy-hardening-attestation-revocation-delivery lineage receipt page — delivery coverage, stale-surface suppression, and blocked stronger sentences

## Purpose

This page is the durable receipt that captures what level of revocation delivery and closure was honestly achieved for a case at a specific time.
It must survive later review and show not merely that a corrective wave existed, but what cohort was truly reached, what stale surfaces were suppressed, what residual risk remained, and which stronger closure sentence the product refused to make.

## Receipt header

The receipt must print:

- receipt identifier
- case identifier
- source reliance receipt identifier
- corrective-wave identifier
- current governing receipt identifier
- current delivery-governance class
- current stale-surface class
- current closure threshold class
- receipt issuance time

## Receipt body

The receipt must always include:

- strongest speakable closure sentence
- strongest blocked global all-clear sentence
- strongest blocked historical-only-everywhere sentence
- reachable dependent count
- delivery-confirmed count
- acknowledgement-complete count for required cohort
- stale-surface suppressed count
- residual-live-surface count
- unreachable-dependent count
- escalation owner
- exact reason broader closure is blocked

## Mandatory distinctions preserved by the receipt

The receipt must preserve at least these distinctions:

- wave opened versus delivered
- delivered versus acknowledged
- acknowledged versus successor-bound
- successor-bound versus stale surface suppressed
- named-cohort closure versus global closure
- residual risk preserved versus residual risk absent

## Example speakable sentences

The receipt should support outputs such as:

- `corrective wave opened; callback coverage incomplete`
- `delivered to all reachable dependents; acknowledgement still pending for one required human consumer`
- `all required internal dependents acknowledged and all internal stale surfaces suppressed`
- `named cohort closed; one external exported artifact remains live without callback path`
- `historical only for the required cohort, not historical only everywhere`

## Claim ceilings

The receipt must block false upgrades such as:

- `everyone got the correction`
- `nothing stale remains`
- `the old ruling is dead everywhere`
- `global closure achieved`

unless the receipt actually carries the evidence needed for those stronger statements.
'''
}

for name, content in new_docs.items():
    (docs / name).write_text(content)

readme = root / 'README.md'
prepend = '''## Revision addendum after rev0457 — remedy hardening attestation revocation delivery, acknowledgement, and stale-surface-suppression truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **whether a corrective wave that was properly opened against known dependents also actually reached them, was acknowledged where required, suppressed stale derivative surfaces, and earned an honest closure sentence rather than just a better-looking status rail**.
It does eight things in one tranche:

1. Continues the archive after rev0457 with a new page family centered on what happens *after* dependency spread and revocation-wave obligations are explicit but *before* the product should pretend the old ruling is no longer effectively live anywhere that matters.
2. Tightens the non-clone line again: borrow Resilio's candor about linked-device spread, on-the-fly permission mutation, disconnect that leaves local bytes present, pending and disconnected folders, short-horizon peer and History visibility, archive residue, restart-gated debug proof, config rollout across multiple machines, and unsupported cloning; refuse any contract where the operator still has to reconstruct `did the correction actually reach the dependents and suppress stale surfaces?` from scattered operational surfaces.
3. Adds one new **Resilio evaluation** document focused on why current remedy-hardening-attestation-revocation-delivery truth is still too fragmented to clone even though the ingredients are useful.
4. Adds five new **interface specs** for remedy-hardening-attestation-revocation-delivery contract sheet, review, proof, timeline, and lineage receipt.
5. Makes one hard product decision explicit: **known reliance is weaker than callback-reachable reliance.**
6. Makes another hard product decision explicit: **delivery attempted is weaker than delivery confirmed, and delivery confirmed is weaker than acknowledgement-complete closure for the required cohort.**
7. Makes a third hard product decision explicit: **acknowledged correction is weaker than stale-surface suppression, and named-cohort closure is weaker than global `historical only everywhere` closure.**
8. Packages the result as another continuation archive whose new tranche makes the `callback path / delivery evidence / acknowledgement requirement / stale surface / suppression owner / residual-live-surface debt / receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1888-resilio-remedy-hardening-attestation-revocation-delivery-acknowledgement-and-stale-surface-suppression-fragmentation-evaluation.md`
- `1889-remedy-hardening-attestation-revocation-delivery-contract-sheet-page-callback-reachability-ack-coverage-and-suppression-owner-interface-spec.md`
- `1890-remedy-hardening-attestation-revocation-delivery-review-page-did-the-revocation-or-revalidation-actually-reach-every-dependent-and-suppress-stale-surfaces-interface-spec.md`
- `1891-remedy-hardening-attestation-revocation-delivery-proof-page-delivery-acknowledgement-enforcement-and-residual-live-surface-floor-interface-spec.md`
- `1892-remedy-hardening-attestation-revocation-delivery-timeline-page-freeze-notify-ack-enforce-escalate-and-closeout-events-interface-spec.md`
- `1893-remedy-hardening-attestation-revocation-delivery-lineage-receipt-page-delivery-coverage-stale-surface-suppression-and-blocked-stronger-sentences-interface-spec.md`


'''
readme.write_text(prepend + readme.read_text())

status = docs / '00-status.md'
status_prepend = '''## Revision addendum — remedy hardening attestation revocation delivery, acknowledgement, and stale-surface-suppression truth after rev0457

This tranche locks the next seam around **closure after revocation propagation**.
The key decisions now made explicit in the archive are:

- **dependency-governed relied-upon standing is a first-class rung, but it is weaker than dependency-governed-and-corrective-wave-delivered standing**
- **corrective wave opened, callback map incomplete, delivered to reachable cohort only, acknowledgement pending, acknowledgement complete for required cohort, stale-surface suppression pending, named-cohort closure achieved, external residual risk preserved, global all-clear blocked, and historical-only-everywhere closure achieved are different truths**
- **registered consumer is weaker than reachable consumer, reachable consumer is weaker than delivered consumer, delivered consumer is weaker than acknowledged consumer, and acknowledged consumer is weaker than suppressed stale surface**
- **disconnect, permission mutation, linked-device spread, pending auto-connect, Archive residue, peer-list calm, and config rollout can no longer silently impersonate revocation closure truth**
- **every serious closure sentence now needs one receipt that preserves callback-path status, delivery evidence, acknowledgement requirement, stale-surface status, residual-live-surface debt, highest honest closure sentence, and the blocked stronger sentence**

New docs added in this tranche:

- `1888-resilio-remedy-hardening-attestation-revocation-delivery-acknowledgement-and-stale-surface-suppression-fragmentation-evaluation.md`
- `1889-remedy-hardening-attestation-revocation-delivery-contract-sheet-page-callback-reachability-ack-coverage-and-suppression-owner-interface-spec.md`
- `1890-remedy-hardening-attestation-revocation-delivery-review-page-did-the-revocation-or-revalidation-actually-reach-every-dependent-and-suppress-stale-surfaces-interface-spec.md`
- `1891-remedy-hardening-attestation-revocation-delivery-proof-page-delivery-acknowledgement-enforcement-and-residual-live-surface-floor-interface-spec.md`
- `1892-remedy-hardening-attestation-revocation-delivery-timeline-page-freeze-notify-ack-enforce-escalate-and-closeout-events-interface-spec.md`
- `1893-remedy-hardening-attestation-revocation-delivery-lineage-receipt-page-delivery-coverage-stale-surface-suppression-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `we opened a revocation wave` can no longer hide whether the correction reached the dependents
- `they were told` can no longer silently impersonate acknowledgement or successor binding
- `the old ruling is historical now` can no longer hide a still-live dashboard, export, downstream receipt, or reconnectable lane
- later operators can open one receipt and see exactly which dependents were reachable, which actually received the correction, which required acknowledgement, which stale surfaces were suppressed, what residual-live-surface debt remains, and which stronger closure sentence the product refused to make


'''
status.write_text(status_prepend + status.read_text())

evalf = docs / '10-resilio-sync-evaluation.md'
eval_prepend = '''## Revision addendum after rev0457 — why remedy hardening attestation revocation delivery, acknowledgement, and stale-surface suppression now sit on the non-clone side

Current official Resilio docs are still admirably candid that `we changed permissions`, `we disconnected the folder`, `History looks calm`, `the peer is gone from the list`, `the old files are in Archive`, and `the correction probably got around` are not one flat closure truth.
`Sync Private Identity & Linking My Devices` still says linked devices automatically make all folders available everywhere and approvals can be issued from any linked device where the folder is present.
`User Management` still says permissions can be changed on the fly and all linked devices under one identity act as Owners.
`Disconnecting and Removing Folders` still says disconnect only affects one device while the folder remains in the file system.
`Folder Types and Management` still says pending folders may auto-connect after prior approval and disconnected folders remain visible for later action.
`Sync Main View (Desktop)` still says History only covers the last 30 days and offline peers disconnect from the peer list after 7 days.
`Using Archive for file versioning and restoring deleted files` still says old versions can persist in Archive and only manual restoring is possible.
`Collecting debug logs automatically` still says deeper proof often requires enabling debug logging, restarting, reproducing the issue, and waiting at least 15 minutes.
`Running Sync in configuration mode` still says one configuration can be applied across a number of different machines.
`Cloning Sync` still says unsupported copies can create strange behavior and non-transferring twins.

This is strong operational candor.
It is also exactly why AnonSync should not clone the present contract.
One ordinary answer to `did the correction actually reach every dependent and make the stale ruling stop being live?` still depends on combining linked-device spread, permission mutation, disconnect semantics, pending or disconnected folders, short-horizon UI, Archive residue, startup config rollout, restart-gated support evidence, and clone ambiguity.

So this tranche freezes a stronger replacement line: **revocation opened, callback-reachable, delivered, acknowledged, successor-bound, stale-surface-suppressed, named-cohort closed, externally residually live, and historical-only-everywhere become separate modeled truths.**

That is why this revision adds five more first-class pages: **Remedy-hardening-attestation-revocation-delivery contract sheet**, **Remedy-hardening-attestation-revocation-delivery review**, **Remedy-hardening-attestation-revocation-delivery proof**, **Remedy-hardening-attestation-revocation-delivery timeline**, and **Remedy-hardening-attestation-revocation-delivery lineage receipt**.


'''
evalf.write_text(eval_prepend + evalf.read_text())

sources = docs / 'sources.md'
append = '''
## rev0458 source set — remedy hardening attestation revocation delivery, acknowledgement, and stale-surface suppression

The most load-bearing source set for this pass was:

- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says linked devices automatically make all folders available everywhere and approvals can be issued from any linked device where the folder is present.
- Resilio's current `User Management` article, which still says permissions can be changed on the fly and all linked devices under one identity act as Owners.
- Resilio's current `Disconnecting and Removing Folders` article, which still says disconnect only affects one device while the folder remains in the file system.
- Resilio's current `Folder Types and Management` article, which still says pending folders may auto-connect after prior approval and disconnected folders remain visible for later action.
- Resilio's current `Sync Main View (Desktop)` article, which still says History covers only the last 30 days and offline peers disconnect from the peer list after 7 days.
- Resilio's current `Using Archive for file versioning and restoring deleted files` article, which still says old or deleted copies persist in Archive and only manual restoring is possible.
- Resilio's current `Collecting debug logs automatically` article, which still says useful deeper evidence often requires enable, restart, reproduce, and waiting at least 15 minutes.
- Resilio's current `Running Sync in configuration mode` article, which still says one configuration can be applied across a number of different machines.
- Resilio's current `Cloning Sync` article, which still says unsupported copies can create non-transferring twins and other strange behavior.
- Resilio's current `Resilio Sync 3.0 change log`, which still records UI and WebUI-adjacent fixes that reinforce why visible calm cannot carry the whole closure claim alone.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for candid closure ingredients
- but current Resilio still answers `did the correction truly reach the dependents and suppress stale surfaces?` too diffusely
- AnonSync should therefore prefer explicit remedy-hardening-attestation-revocation-delivery sheets, revocation-delivery reviews, revocation-delivery proofs, revocation-delivery timelines, and durable revocation-delivery lineage receipts over overloaded permission, disconnect, Archive, peer-list, and support-log language

Primary sources:

- Sync Private Identity & Linking My Devices
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Disconnecting and Removing Folders
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Folder Types and Management
  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management

- Sync Main View (Desktop)
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- Using Archive for file versioning and restoring deleted files
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- Collecting debug logs automatically
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Running Sync in configuration mode
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Cloning Sync
  https://help.resilio.com/hc/en-us/articles/360018421940-Cloning-Sync

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log
'''
sources.write_text(sources.read_text() + append)

print('rev0458 content written')
