from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / 'docs'

new_docs = {
'1942-resilio-remedy-hardening-attestation-policy-conformance-drift-recertification-and-breach-state-fragmentation-evaluation.md': '''# Resilio remedy hardening attestation policy conformance, drift recertification, and breach-state fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for being unusually candid that `a policy was rolled out`, `defaults exist`, `new arrivals inherit them`, `older material already conforms`, `service and interactive worlds stayed aligned`, and `the same rule is still governing right now` are not one flat truth.
That candor is useful.

The strongest present ingredients are:

- current `Running Sync in configuration mode` docs still say one configuration can apply pre-configured parameters at program start across a number of different machines
- current `Folder Preferences` docs still say important behavior remains configured on a folder-by-folder basis and is available on desktop platforms only
- current `Power user preferences` docs still say some defaults only govern shares whose priority was not altered manually in folder preferences
- current `Selective Sync` docs still say the selected linked-device mode is applied to all newly added folders while current ones remain as they are
- current `Running Sync as a service on Windows` docs still say migrating settings preserves existing shares but a clean installation requires re-sharing and reconnecting folders
- current `Sync Service Troubleshooting on Windows` docs still say switching service user can produce a new storage folder and the old added folders disappear from that world
- current `Disconnecting and Removing Folders` docs still say reconnect can propose a different default path and create a new directory
- current `Sync Main View (Desktop)` docs still say History only covers the last 30 days and peers offline for 7 days disconnect from the folder view
- current `Resilio Sync change log` still records drift-relevant failures such as folder changes detected only during rescan, disappearing folders returning with `(1)`, and files duplicating after re-adding by the same path

## Where the current contract still fragments

The problem is not that Resilio lacks controls.
The problem is that it still does not produce one first-class, case-scoped **policy conformance and drift-recertification** object.

Today an operator can often infer only weaker truths such as:

- a default was configured once
- some new arrivals should inherit that default
- one desktop folder still shows the expected preference
- one service world or one user world no longer sees the same folders
- one reconnect created a new path that might or might not still be in policy
- one recent surface looks calm inside the last 30 days
- one changelog entry explains why drift sometimes only becomes visible after rescan or re-add

Those are useful clues.
They are not the same as an explicit answer to `is the deployed policy still live and conforming for the intended slice right now, which fresh witnesses prove that, which new arrivals or world-switches escaped inheritance, which drift is only suspected, which breach is confirmed, who owns repair, and what stronger still-governing sentence is blocked until recertification?`

## Why that matters for AnonSync

AnonSync needs a stronger sentence than `the rule was deployed`.
It needs to support claims such as:

- the rule was deployed, but current conformance evidence is stale
- the rule still holds for named slice except for fresh drift on one topology branch
- new entrants inherit correctly, but pre-existing objects remain outside conformance until reconcile
- service-world cutover created a sibling world and conformance must be re-proved there
- drift is suspected from weak signals, but breach is not yet confirmed
- breach is confirmed, containment is active, and the strongest honest sentence is `policy degraded pending repair`, not `still governing`

AnonSync therefore needs first-class objects for **live conformance class, witness freshness, recertification clock, inherited-coverage delta, world-switch delta, suspected-drift ledger, confirmed-breach ledger, containment state, repair owner, restored-after-recertification state, blocked stronger sentence, and next evidence that upgrades or collapses conformance standing** rather than leaving operators to infer present truth from config files, a recent UI sample, a remembered rollout, service storage surprises, reconnect side effects, and changelog archaeology.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `is this policy still truly governing the intended slice now?` — only by making the operator combine several partially overlapping mechanics:

- config-mode startup rollout across machines
- desktop-only per-folder preferences
- manual overrides that stop later defaults from applying
- linked-device defaults that apply to newly added folders while current ones remain as they are
- service migrations or principal changes that may preserve or abandon prior shares depending on path chosen
- reconnect behavior that may create a new path
- short-history and peer-presence surfaces
- drift and delayed-detection memory from the change log

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **policy conformance, drift surveillance, recertification, and breach state** directly.
Its interface family should let the product separate at least these truths:

- deployed policy, current conformance unverified
- current conformance evidenced for named slice only
- recertification overdue, stronger sentence blocked
- inherited coverage for new arrivals unverified
- suspected drift under investigation
- confirmed breach with containment active
- repair applied, recertification pending
- conformance restored after fresh recertification
- policy narrowed because conformance could not be restored
- broader `still governing everywhere now` sentence blocked
''',
'1943-remedy-hardening-attestation-policy-conformance-contract-sheet-page-live-conformance-drift-budget-and-recertification-clock-interface-spec.md': '''# Remedy-hardening-attestation policy-conformance contract sheet page — live conformance, drift budget, and recertification clock

## Purpose

This page is the compact contract for deciding whether a policy that was already rolled out for a named estate slice is still honestly governing that slice right now.
It exists so the product can distinguish `deployed once`, `currently conforming with fresh witness`, `recertification overdue`, `suspected drift`, `confirmed breach`, `repair in progress`, `restored after recertification`, and `broader still-governing sentence blocked`.

## Core fields

- policy conformance identifier
- source policy-rollout receipt identifier
- current governing receipt identifier
- current policy-conformance class
- named estate slice under present review
- estate slices explicitly not covered by this conformance claim
- last trusted rollout-verdict class
- current witness freshness class
- latest conformance witness set
- next required recertification time
- inherited-coverage status for newly arrived objects or members
- pre-existing object reconciliation status
- service-world or principal-world continuity status
- reconnect or path-split exposure status
- suspected drift count
- confirmed breach count
- containment status
- repair owner
- repair due time
- highest currently safe conformance sentence
- strongest blocked still-governing sentence
- next evidence that upgrades confidence now
- next evidence that forces downgrade or breach declaration now

## Policy-conformance classes

The page must model at least these distinct classes:

- deployed policy, current conformance unverified
- current conformance evidenced for named slice only
- current conformance evidenced but inherited coverage incomplete
- recertification overdue, stronger sentence blocked
- suspected drift under investigation
- confirmed breach with containment active
- confirmed breach without adequate containment
- repair applied, recertification pending
- conformance restored after fresh recertification
- conformance narrowed, paused, or retired
- broader still-governing sentence blocked

## Drift axes

The page must support at least these drift axes:

- manual override emergence
- new-object inheritance failure
- pre-existing object residual variance
- service-world or principal-world split
- reconnect or path fork
- platform or surface control gap
- rescan or reread delay
- stale witness horizon
- containment adequacy
- repair verification gap

## Fixed rendering order

Every policy-conformance contract sheet must render the same sections in the same order:

1. **Highest currently conformance-safe sentence**
2. **Named estate slice, current conformance class, and witness freshness**
3. **Fresh drift and breach ledger**
4. **Containment, repair owner, and recertification clock**
5. **Next evidence that upgrades or collapses the still-governing claim**

## Hard rules

The contract sheet must never let an operator hide:

- an old rollout receipt behind a `still governing now` sentence
- stale witness behind a `current conformance proved` sentence
- a new-arrival inheritance gap behind `policy covers the slice`
- a service or principal world split behind `same deployment still applies`
- suspected or confirmed drift behind `no known issue` wording
''',
'1944-remedy-hardening-attestation-policy-conformance-review-page-is-the-deployed-policy-still-live-for-the-intended-slice-right-now-interface-spec.md': '''# Remedy-hardening-attestation policy-conformance review page — is the deployed policy still live for the intended slice right now?

## Purpose

This page is the operator-facing review that answers the practical conformance question after rollout: does the product know enough to say the policy still governs the named slice now, or has drift, stale evidence, or world change collapsed that sentence?

## Primary review prompts

The review must answer these prompts in order:

1. **Which rollout receipt is the starting basis for this current conformance review?**
2. **Which named slice is being claimed as still governed right now?**
3. **What fresh witness proves present conformance rather than historical deployment only?**
4. **What changed since the last trusted witness: overrides, new arrivals, reconnects, service moves, or principal changes?**
5. **Is drift only suspected, or is breach now confirmed?**
6. **What is the strongest sentence the product may still say right now?**

## Review sections

### 1. Rollout basis board

Show:

- source rollout receipt and class
- last known conformance class
- why a present-time conformance review is allowed or required now

### 2. Fresh witness board

Show:

- newest conformance witnesses
- witness freshness class
- covered populations
- uncovered populations
- recertification deadline

### 3. Change-since-last-proof board

Show:

- newly added objects or members
- manual overrides since the prior receipt
- service-user, principal, or world changes
- reconnects or path forks
- whether each change is harmless, drift-suspect, or breach-relevant

### 4. Drift and containment board

Show:

- suspected drift items
- confirmed breach items
- containment state
- repair owner and due time
- whether stronger still-governing language is blocked now

### 5. Conformance sentence chooser

The review must output one and only one primary sentence class such as:

- deployed policy, current conformance unverified
- current conformance evidenced for named slice only
- inherited coverage incomplete
- recertification overdue, stronger sentence blocked
- suspected drift under investigation
- confirmed breach with containment active
- confirmed breach without adequate containment
- repair applied, recertification pending
- conformance restored after fresh recertification
- policy narrowed, paused, or retired

## Hard rules

The review must never let an operator hide:

- rollout history behind present conformance
- one narrow fresh example behind whole-slice proof
- `new folders follow it` behind `older covered population still conforms`
- a storage or service-world fork behind `same deployment still governs`
- containment effort behind `breach resolved`
''',
'1945-remedy-hardening-attestation-policy-conformance-proof-page-fresh-witness-drift-detection-and-breach-ceiling-interface-spec.md': '''# Remedy-hardening-attestation policy-conformance proof page — fresh witness, drift detection, and breach ceiling

## Purpose

This page is the evidence-heavy proof surface for present-time conformance claims after rollout.
It proves the exact ceiling on any sentence that tries to say a deployed policy is still governing the named estate slice now.

## Required evidence blocks

### 1. Source rollout basis

Preserve:

- source rollout receipt and class
- original deployment scope
- last trusted conformance receipt
- reason present recertification is required now

### 2. Fresh conformance witness ledger

For each claimed population preserve:

- witness kind
- witness timestamp
- exact population covered
- whether the witness proves present conformance, only historical deployment, or only partial slice coverage
- recertification horizon implied by that witness

### 3. Drift and delta ledger

Preserve:

- manual overrides or newly divergent settings
- new arrivals whose inherited coverage is unproven
- service-world or principal-world splits
- reconnect or path-fork events
- delayed-detection or rescan-sensitive evidence
- resulting downgrade or suspicion class

### 4. Breach, containment, and repair ledger

Preserve:

- every confirmed breach
- exact scope of impact
- containment adequacy
- repair owner and due time
- repair already applied versus still pending
- whether recertification after repair has happened yet

### 5. Claim ceiling

Render:

- highest honest current conformance sentence
- highest honest current containment sentence
- highest honest whole-slice still-governing sentence
- blocked stronger sentence and exact blocker

## Evidence classes

The page must distinguish at least:

- rollout only
- fresh partial conformance proof
- fresh named-slice conformance proof
- inherited coverage incomplete
- recertification overdue
- suspected drift only
- confirmed breach with containment
- confirmed breach without containment
- repair applied pending recertification
- restored conformance after recertification
- broader still-governing sentence blocked

## Hard rules

The proof page must never treat:

- an old rollout artifact as proof of present conformance by itself
- one fresh witness as proof for uncovered populations
- `current ones remain as they are` semantics as if they proved older objects comply
- a service migration as invisible continuity by default
- repair intent as proof of restored conformance
''',
'1946-remedy-hardening-attestation-policy-conformance-timeline-page-recertify-drift-breach-repair-and-restore-events-interface-spec.md': '''# Remedy-hardening-attestation policy-conformance timeline page — recertify, drift, breach, repair, and restore events

## Purpose

This page is the ordered event view for current conformance claims after rollout.
It exists so later operators can see whether the case moved from deployment into fresh proof, overdue recertification, drift suspicion, breach, containment, repair, or restored conformance in the right order.

## Event classes

The timeline must support at least these events:

- rollout receipt adopted as current baseline
- fresh conformance witness captured
- recertification deadline scheduled
- recertification missed
- new population or object entered scope
- inheritance gap detected
- manual override detected
- service-world or principal-world split detected
- reconnect or path fork detected
- suspected drift opened
- breach confirmed
- containment activated
- repair started
- repair applied
- recertification after repair passed
- conformance restored
- policy narrowed, paused, or retired

## Required columns

- timestamp
- event class
- target estate slice
- source evidence reference
- resulting policy-conformance class
- stronger sentence newly allowed or newly blocked

## Hard rules

The timeline must never collapse:

- rollout and present conformance into one event by default
- missed recertification into silent metadata change
- inheritance gaps into invisible background state
- suspected drift and confirmed breach into one event by default
- repair applied and conformance restored into one event by default
''',
'1947-remedy-hardening-attestation-policy-conformance-lineage-receipt-page-current-conformance-drift-state-and-blocked-still-governing-sentences-interface-spec.md': '''# Remedy-hardening-attestation policy-conformance lineage receipt page — current conformance, drift state, and blocked still-governing sentences

## Purpose

This page is the durable one-receipt summary for current conformance claims after rollout.
It lets a later operator read one artifact and know exactly whether the deployed policy is still governing the named slice now, merely believed to be, or blocked by stale proof, suspected drift, or confirmed breach.

## Receipt fields

- receipt identifier
- policy conformance identifier
- source policy-rollout receipt identifier
- current policy-conformance class
- named estate slices currently covered by fresh proof
- estate slices explicitly uncovered or stale
- witness freshness summary
- inherited-coverage summary
- drift and breach summary
- containment and repair summary
- recertification summary
- highest honest current conformance sentence
- blocked stronger still-governing sentence
- evidence bundle references
- issued-at timestamp

## Primary sentence block

The receipt must begin with exactly two lines:

- **Highest honest current conformance sentence**
- **Blocked stronger still-governing sentence**

## Required sections

1. **Why the rollout basis did or did not survive into present-time conformance**
2. **Which populations are freshly covered now and which are not**
3. **Which drift, world splits, or inheritance gaps still matter**
4. **What containment, repair, and recertification state remains**
5. **Why the next stronger `still governing` sentence is blocked**

## Hard rules

The receipt must never let:

- `policy was deployed` impersonate `policy still governs now`
- `fresh witness exists somewhere` impersonate `whole slice freshly proved`
- `new arrivals inherit` impersonate `older populations were reconciled`
- `repair applied` impersonate `recertified conformance`
- `no new alarm surfaced` impersonate `no drift or breach exists`
'''
}

for name, content in new_docs.items():
    (DOCS / name).write_text(content.strip() + '\n', encoding='utf-8')

readme_addendum = '''## Revision addendum after rev0466 — remedy hardening attestation policy conformance, drift recertification, and breach state

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **whether a rule that is already portable and already rolled out for a named estate slice is still honestly governing that slice right now, rather than merely having been deployed once and then left to drift, override, fork, or stale proof**.
It does eight things in one tranche:

1. Continues the archive after rev0466 with a new page family centered on what happens *after* policy rollout and exception governance exist but *before* the product should pretend the same rule still governs the intended populations now.
2. Tightens the non-clone line again: borrow Resilio's candor about config-mode startup rollout, desktop-only folder preferences, defaults that stop applying after manual overrides, linked-device defaults that apply to newly added folders while current ones remain as they are, service migrations that may preserve or abandon prior shares, service-user storage forks, reconnects that may create a new path, short-history visibility, and drift-sensitive changelog memory; refuse any contract where the operator still has to reconstruct `is this policy still live and conforming now?` from scattered operational surfaces.
3. Adds one new **Resilio evaluation** document focused on why current remedy-hardening-attestation-policy-conformance truth is still too fragmented to clone even though the ingredients are useful.
4. Adds five new **interface specs** for remedy-hardening-attestation-policy-conformance contract sheet, review, proof, timeline, and lineage receipt.
5. Makes one hard product decision explicit: **deployed policy is weaker than currently recertified conformance.**
6. Makes another hard product decision explicit: **fresh conformance for a sampled population is weaker than fresh conformance for the named slice, and `new arrivals inherit` is weaker than `older covered populations were reconciled and still conform`.**
7. Makes a third hard product decision explicit: **suspected drift, confirmed breach, containment active, repair applied, and restored-after-recertification are separate public truths that may not collapse into optimistic `still governing` language.**
8. Packages the result as another continuation archive whose new tranche makes the `fresh witness / recertification clock / inheritance gap / world split / drift suspicion / breach state / repair owner / receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1942-resilio-remedy-hardening-attestation-policy-conformance-drift-recertification-and-breach-state-fragmentation-evaluation.md`
- `1943-remedy-hardening-attestation-policy-conformance-contract-sheet-page-live-conformance-drift-budget-and-recertification-clock-interface-spec.md`
- `1944-remedy-hardening-attestation-policy-conformance-review-page-is-the-deployed-policy-still-live-for-the-intended-slice-right-now-interface-spec.md`
- `1945-remedy-hardening-attestation-policy-conformance-proof-page-fresh-witness-drift-detection-and-breach-ceiling-interface-spec.md`
- `1946-remedy-hardening-attestation-policy-conformance-timeline-page-recertify-drift-breach-repair-and-restore-events-interface-spec.md`
- `1947-remedy-hardening-attestation-policy-conformance-lineage-receipt-page-current-conformance-drift-state-and-blocked-still-governing-sentences-interface-spec.md`
'''

status_addendum = '''## Revision addendum — status shift toward policy conformance, drift recertification, and breach state after rev0466

The next seam after **policy rollout, exception governance, and enforcement coverage** is now explicit:

- the archive can already say whether a portable rule actually became governing policy for a named estate slice
- it still needed to own the harder truth of **whether that deployed policy is still live and conforming for the intended slice right now, with fresh witnesses, explicit recertification horizons, explicit drift state, and explicit breach or repair posture**, because deployed once, freshly conforming, recertification overdue, inherited coverage incomplete, drift suspected, breach confirmed, containment active, repair applied, and restored-after-recertification are not one consequence class
- current Resilio docs reinforce that gap because config mode applies settings at startup across multiple machines, folder preferences remain desktop-only and per-folder, some defaults stop governing after manual overrides, linked-device mode applies to newly added folders while current ones remain as they are, service migrations may either preserve or abandon prior shares, service-user changes can create a new storage world, reconnect can create a new path, visibility remains short-horizon, and the changelog still records delayed-detection and re-add pathologies

This pass turns that gap into a first-class product object: **the remedy-hardening attestation policy-conformance and drift-recertification case**.

What is newly true in the archive:

- **deployed policy is weaker than currently recertified conformance**
- **deployed policy, current conformance evidenced for named slice, inherited coverage incomplete, recertification overdue, suspected drift, confirmed breach, repair pending recertification, and restored-after-recertification are separate public truths**
- **fresh sample proof is weaker than fresh named-slice conformance, and named-slice conformance is weaker than a stronger still-governing sentence that also survives inheritance, world-split, and repair checks**
- **config files, remembered defaults, linked-device modes, service migrations, reconnect paths, recent calm surfaces, and changelog folklore now degrade into evidence inputs instead of impersonating the present conformance verdict**
- **every serious still-governing sentence now needs one receipt that preserves source rollout receipt, witness freshness, inherited-coverage status, world continuity status, drift or breach ledger, containment state, repair owner, recertification clock, highest honest conformance sentence, and the blocked stronger sentence**

What remains intentionally true:

- policy rollout still matters
- precedent portability still matters
- affected-party closure, subscriber invalidation, and downstream remediation still matter
- but none of those may substitute for one explicit answer about whether the deployed rule still governs the named slice now or only did so historically

New docs added in this tranche:

- `1942-resilio-remedy-hardening-attestation-policy-conformance-drift-recertification-and-breach-state-fragmentation-evaluation.md`
- `1943-remedy-hardening-attestation-policy-conformance-contract-sheet-page-live-conformance-drift-budget-and-recertification-clock-interface-spec.md`
- `1944-remedy-hardening-attestation-policy-conformance-review-page-is-the-deployed-policy-still-live-for-the-intended-slice-right-now-interface-spec.md`
- `1945-remedy-hardening-attestation-policy-conformance-proof-page-fresh-witness-drift-detection-and-breach-ceiling-interface-spec.md`
- `1946-remedy-hardening-attestation-policy-conformance-timeline-page-recertify-drift-breach-repair-and-restore-events-interface-spec.md`
- `1947-remedy-hardening-attestation-policy-conformance-lineage-receipt-page-current-conformance-drift-state-and-blocked-still-governing-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `this rule was rolled out` can no longer hide whether it still governs now
- stale witness can no longer silently impersonate fresh conformance
- inherited coverage for new arrivals can no longer silently impersonate reconciliation of older covered populations
- later operators can open one receipt and see exactly what fresh proof exists, which drift or breach is live, who owns repair, when recertification is due, and which stronger sentence the product refused to make
'''

eval_addendum = '''## Revision addendum after rev0466 — why remedy hardening attestation policy conformance, drift recertification, and breach state now sit on the non-clone side

Current official Resilio docs are still admirably candid that `the policy exists`, `the rollout happened`, `new folders inherit the mode`, `one folder still shows the right setting`, `the service is running`, and `the policy is still governing the intended slice right now` are not one flat truth.
`Running Sync in configuration mode` still says one configuration can apply pre-configured parameters across a number of different machines at startup.
`Folder Preferences` still says important controls remain folder-by-folder and desktop-only.
`Power user preferences` still says some defaults apply only to shares whose priority was not altered manually in folder preferences.
`Selective Sync` still says the selected linked-device mode applies to all newly added folders while current ones remain as they are.
`Running Sync as a service on Windows` still says migration preserves old shares but a clean installation requires re-sharing and reconnecting folders.
`Sync Service Troubleshooting on Windows` still says changing service user can create a new storage folder where the old added folders are absent.
`Disconnecting and Removing Folders` still says reconnect can propose a different default path and create a new directory.
`Sync Main View (Desktop)` still says History only covers the last 30 days and offline peers disconnect from folder view after 7 days.
`Resilio Sync change log` still records drift-adjacent failures such as folder changes detected only during rescan, disappearing folders returning with `(1)`, and files duplicating after re-adding by the same path.

This is strong conformance-ingredient candor.
It is also exactly why AnonSync should not clone the present contract.
One ordinary answer to `is this policy still genuinely governing the intended slice now?` still depends on combining startup config rollout, desktop-only per-folder controls, override persistence, future-only inheritance semantics, service-user world continuity, reconnect path behavior, short-horizon visibility, and changelog memory about delayed detection.

So this tranche freezes a stronger replacement line: **deployed policy, current conformance evidenced, inherited coverage incomplete, recertification overdue, suspected drift, confirmed breach, containment active, repair applied, and restored-after-recertification become separate modeled truths.**

That is why this revision adds five more first-class pages: **Remedy-hardening-attestation-policy-conformance contract sheet**, **Remedy-hardening-attestation-policy-conformance review**, **Remedy-hardening-attestation-policy-conformance proof**, **Remedy-hardening-attestation-policy-conformance timeline**, and **Remedy-hardening-attestation-policy-conformance lineage receipt**.
'''

sources_addendum = '''\n\n## rev0467 source set — remedy hardening attestation policy conformance, drift recertification, and breach state

The most load-bearing source set for this pass was:

- Resilio's current `Running Sync in configuration mode` article, which still says one configuration can apply pre-configured parameters at program start across a number of different machines.
- Resilio's current `Folder Preferences` article, which still says important controls remain folder-by-folder and desktop-only.
- Resilio's current `Power user preferences` article, which still says some defaults apply only to shares whose priority was not altered manually in folder preferences.
- Resilio's current `Selective Sync` article, which still says linked-device mode applies to all newly added folders while current ones remain as they are.
- Resilio's current `Running Sync as a service on Windows` article, which still says migration preserves prior shares but a clean installation requires re-sharing and reconnecting them.
- Resilio's current `Sync Service Troubleshooting on Windows` article, which still says switching service user can create a new storage world where old added folders are absent.
- Resilio's current `Disconnecting and Removing Folders` article, which still says reconnect may propose a different default path and create a new directory.
- Resilio's current `Sync Main View (Desktop)` article, which still says History only covers 30 days and offline peers disconnect from folder view after 7 days.
- Resilio's current `Resilio Sync change log`, which still records drift-sensitive failures such as folder changes detected only during rescan, disappearing folders returning with `(1)`, and file duplication after re-adding by the same path.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for candid conformance ingredients
- but current Resilio still answers `is this policy still truly governing now, for the intended slice?` too diffusely
- AnonSync should therefore prefer explicit remedy-hardening-attestation-policy-conformance sheets, policy-conformance reviews, policy-conformance proofs, policy-conformance timelines, and durable policy-conformance lineage receipts over overloaded rollout artifacts, folder preferences, service-world assumptions, reconnect behavior, short-horizon UI, and changelog memory

Primary sources:

- Running Sync in configuration mode
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Folder Preferences
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Power user preferences
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Selective Sync
  https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync

- Running Sync as a service on Windows
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Sync Service Troubleshooting on Windows
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Disconnecting and Removing Folders
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Sync Main View (Desktop)
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- Resilio Sync change log
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log
'''

for fname, addendum in [('README.md', readme_addendum), ('docs/00-status.md', status_addendum), ('docs/10-resilio-sync-evaluation.md', eval_addendum)]:
    path = ROOT / fname
    old = path.read_text(encoding='utf-8')
    if addendum.splitlines()[0] not in old:
        path.write_text(addendum + '\n\n' + old, encoding='utf-8')

spath = DOCS / 'sources.md'
sold = spath.read_text(encoding='utf-8')
if '## rev0467 source set — remedy hardening attestation policy conformance, drift recertification, and breach state' not in sold:
    spath.write_text(sold + sources_addendum + '\n', encoding='utf-8')
