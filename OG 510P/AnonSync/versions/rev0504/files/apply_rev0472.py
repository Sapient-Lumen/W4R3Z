from pathlib import Path

root = Path('.')
docs = root / 'docs'

new_files = {
'1972-resilio-remedy-hardening-attestation-postcondition-durability-recurrence-and-steady-state-fragmentation-evaluation.md': '''# Resilio remedy hardening attestation postcondition durability, recurrence, and steady-state fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for being candid that `the intended state is true right now on the surfaces we checked`, `that state will remain true for the intended slice across later churn`, and `future arrivals or reconnecting lanes cannot silently re-open the old hazard` are not one flat truth.
That candor is useful.

The strongest present ingredients are:

- current `Sync Private Identity & Linking My Devices` docs still say every folder added on one linked device automatically becomes available on all the other linked devices, so present realization and future-arrival durability are not the same question
- current `Synchronization Modes` docs still say disconnected folders remain visible and may later be connected, while selective-sync folders are placeholder-heavy and hydrate only when a source peer is online
- current `Disconnecting and Removing Folders` docs still say disconnected folders can be reconnected later, may reconnect to a different default path, and removed linked-device folders can still remain on unlinked remotes
- current `How to clear offline devices?` docs still say hiding an offline linked device is only a view cleanup and that the device will reappear if it ever comes back online
- current `How to pause syncing` docs still say paused peers still sync deletions and still rescan and index new files
- current `What if several people make changes to the same file?` docs still say an offline peer can later come online and overwrite newer online work
- current `Using Archive for file versioning and restoring deleted files` docs still say restored files can be pushed back into Archive again on rescan if Sync was not running
- current `Cannot download files` docs still say a mesh can advertise files that later collapse into ghost-file warnings when no peer still has the bytes
- current `Resilio Sync change log` still records recurrence-style failures such as all folders disconnecting when a 30-days-offline peer comes online, deleted files returning sometimes, and folders returning with `(1)` after path churn or re-adds

## Where the current contract still fragments

The problem is not that Resilio lacks durability-relevant clues.
The problem is that it still does not produce one first-class, case-scoped **postcondition-durability** object.

Today an operator can often infer only weaker truths such as:

- the target state is realized for the currently visible cohort, but future linked-device arrivals will inherit a different state unless checked again
- the folder is disconnected or placeholder-light right now, but it can later reconnect, hydrate, or revive through a different path
- an offline device was hidden from view, but it was not actually retired from the governing world and may later re-enter it
- a paused lane looks quiescent, but deletions and indexing still keep moving underneath the pause
- a restored file appears back, but later rescan or later-offline replay can still displace it
- the current mesh looks satisfied, but a ghost-file or path-duplication condition can later re-open the hazard after the initial realization sentence was published

Those are useful clues.
They are not the same as an explicit answer to `will the realized target state stay true for the governed slice across the next governing horizon, despite reconnects, future arrivals, hidden returners, paused-side effects, replay, restore, and path churn?`

## Why that matters for AnonSync

AnonSync needs a stronger sentence than `the target state is true here now`.
It needs to support claims such as:

- the target state is realized now, but durability is blocked by future-arrival inheritance risk
- the target state is realized for the current cohort, but reconnect or replay risk still dominates the next governing horizon
- the target state is realized and stable within a named steady-state horizon for a named slice only
- the target state is realized and recurrence-resistant for the governed slice, while broader stronger permanence language remains blocked

So AnonSync should not clone Resilio's present contract at this seam.
It should borrow the candor about reconnects, placeholders, hidden returners, pause semantics, restore fragility, and ghost-file warnings, while replacing the fragmented operator story with one first-class family for **postcondition durability, recurrence budget, steady-state horizon, and survivor-lane truth**.
''',
'1973-remedy-hardening-attestation-postcondition-durability-contract-sheet-page-steady-state-horizon-recurrence-budget-and-survivor-lanes-interface-spec.md': '''# Remedy-hardening-attestation postcondition-durability contract sheet page — steady-state horizon, recurrence budget, and survivor lanes

## Purpose

This page is the compact contract for deciding whether a target state that is already realized is likely to stay realized for the intended slice across the next governing horizon.
It exists so the product can distinguish `realized now only`, `realized but fragile`, `realized for current cohort only`, `realized but future-arrival unsafe`, `realized but reconnect-or-replay vulnerable`, `stable through named horizon`, `durable for governed slice`, and `broader permanence blocked`.

## Core fields

- postcondition-durability identifier
- source postcondition-realization receipt identifier
- governing realization sentence
- target postcondition sentence
- governed slice identifier
- steady-state horizon identifier or duration
- future-arrival cohort definition
- reconnecting-lane inventory
- hidden-or-cleared device inventory
- paused or delayed-lane inventory
- replay or overwrite hazard inventory
- restore-or-rearchive hazard inventory
- path-churn or duplication hazard inventory
- ghost-or-placeholder regression inventory
- durability witness class summary
- recurrence budget summary
- current postcondition-durability class
- highest currently safe durability sentence
- strongest blocked stronger sentence
- next fact that upgrades durability standing now
- next fact that collapses durability standing now

## Postcondition-durability classes

The page must model at least these distinct classes:

- realized now only, durability unreviewed
- realized, but durability witnesses missing
- realized for currently visible cohort only
- realized, but future-arrival inheritance risk open
- realized, but reconnect or hidden-returner risk open
- realized, but replay or overwrite risk open
- realized, but restore or rearchive risk open
- realized, but path-churn or duplicate-path risk open
- realized, but placeholder or ghost regression risk open
- stable within named steady-state horizon for named slice only
- durable for governed slice within named horizon
- broader permanence or universal durability blocked

## Minimum required comparisons

The page must force explicit comparison between:

- current visible cohort and future-arrival cohort
- current connected world and reconnecting or returning worlds
- bytes-present outcome and placeholder-only outcome
- first restoration and restore survival after rescan
- hidden-from-view devices and actually retired devices
- stable-within-named-horizon and permanent-or-global durability

## Hard rules

- `realized now` must never silently upgrade to `durable`.
- `hidden from view` must never silently upgrade to `gone`.
- `paused` must never silently upgrade to `state frozen`.
- `restored once` must never silently upgrade to `restore will survive replay or rescan`.
- `folder visible on linked devices` must never silently upgrade to `future-arrival behavior already governed safely`.
- `no current contradiction` must never silently upgrade to `recurrence-resistant`.
''',
'1974-remedy-hardening-attestation-postcondition-durability-review-page-will-the-realized-state-stay-true-across-new-arrivals-reconnects-and-later-replays-interface-spec.md': '''# Remedy-hardening-attestation postcondition-durability review page — will the realized state stay true across new arrivals, reconnects, and later replays?

## Purpose

This page is the operator-facing review that answers the practical durability question after postcondition realization is already good enough: given that the intended state is true now for some slice, will it stay true for the governed slice across the next governing horizon, and what is the strongest durability sentence the product may honestly publish now?

## Primary review prompts

The review must answer these prompts in order:

1. **What target postcondition is currently realized, and for which slice?**
2. **What future arrivals, reconnecting lanes, hidden devices, or delayed worlds can still re-enter that slice?**
3. **Which witnesses show the state surviving beyond first realization rather than merely appearing once?**
4. **Which hazards could re-open the old condition through replay, rescan, restore loss, path churn, or placeholder regression?**
5. **What steady-state horizon is actually covered by evidence, and what permanence language stays blocked?**
6. **What is the highest durability sentence the product may honestly say now?**

## Review sections

### 1. Realization basis board

Show:

- source postcondition-realization receipt
- target postcondition sentence
- governed slice
- currently realized class

### 2. Survivor-lane board

Show:

- future-arrival cohort
- reconnecting lanes
- hidden or cleared devices that may return
- paused or delayed lanes
- external or unlinked remnant lanes if relevant

### 3. Recurrence-hazard board

Show:

- replay or overwrite hazards
- restore or rearchive hazards
- placeholder or ghost-file hazards
- path-duplication or wrong-default-path hazards
- any recurrence budget already exceeded

### 4. Horizon board

Show:

- named steady-state horizon
- witnesses that cover that horizon
- slice that is actually covered
- broader stronger sentence that remains blocked

## Operator decisions this page must support

The review must let an operator decide among at least these outcomes:

- keep the case at realized-now-only
- certify durability for named current cohort only
- block durability because future-arrival governance is open
- block durability because reconnect or replay hazards remain live
- certify horizon-bounded durability for named slice
- certify governed-slice durability while broader permanence stays blocked
''',
'1975-remedy-hardening-attestation-postcondition-durability-proof-page-survival-witnesses-recurrence-risks-and-durability-ceiling-interface-spec.md': '''# Remedy-hardening-attestation postcondition-durability proof page — survival witnesses, recurrence risks, and durability ceiling

## Purpose

This page is the evidence-heavy proof surface for determining whether a realized target state has stayed true long enough, broadly enough, and safely enough to justify a durability sentence.
It proves the exact ceiling on any sentence that tries to say the realized state is not merely current, but now steady enough to survive later churn for the governed slice.

## Required evidence blocks

### 1. Realization basis ledger

Preserve:

- source postcondition-realization receipt
- target postcondition sentence
- governed slice
- current realization class

### 2. Survivor-lane ledger

Preserve:

- future-arrival cohort inventory
- reconnecting lane inventory
- hidden or cleared device inventory
- paused or delayed-lane inventory
- unlinked but still relevant remnant lanes if any

### 3. Durability witness ledger

Preserve:

- repeated favorable observations across the named horizon
- cross-world survival witnesses
- future-arrival-safe witnesses
- reconnect-safe witnesses
- replay-safe witnesses
- restore-survival witnesses

### 4. Recurrence-risk ledger

Preserve:

- overwrite or replay threats
- placeholder or ghost regression threats
- rearchive threats
- duplicate-path or wrong-default-path threats
- any evidence that a previously hidden device can reappear

### 5. Durability ceiling ledger

Preserve:

- current postcondition-durability class
- highest honest durability sentence
- broader permanence sentence still blocked
- exact missing fact required for the next upgrade

## Proof rules

- The proof must distinguish a first favorable observation from repeated survival observations.
- The proof must distinguish current-cohort calm from future-arrival safety.
- The proof must distinguish hidden devices from retired devices.
- The proof must distinguish route replay risk from merely absent replay evidence.
- The proof must preserve all hazard lanes even when the current UI looks stable.
''',
'1976-remedy-hardening-attestation-postcondition-durability-timeline-page-realize-hold-drift-recur-stabilize-and-expire-events-interface-spec.md': '''# Remedy-hardening-attestation postcondition-durability timeline page — realize, hold, drift, recur, stabilize, and expire events

## Purpose

This page is the ordered event view for durability questions after postcondition realization is established.
It exists so later operators can see whether the case moved from first realization into horizon-bounded stability, or whether future arrivals, reconnects, hidden returners, pause-side effects, replay, restore loss, or path churn re-opened the hazard.

## Event classes

The timeline must support at least these events:

- source realization receipt imported
- steady-state horizon defined
- first survival observation recorded
- repeated favorable observation recorded
- future-arrival cohort expanded
- reconnecting lane re-entered
- hidden device returned
- paused-lane side effect observed
- replay or overwrite threat raised
- restore attempted
- restore survived rescan
- restore lost on rescan or replay
- ghost or placeholder regression observed
- duplicate-path or wrong-default-path recurrence observed
- named-slice durability confirmed
- governed-slice durability confirmed
- broader permanence sentence blocked
- durability expired or superseded

## Required columns

- timestamp
- event class
- source evidence or observation reference
- resulting postcondition-durability class
- stronger durability sentence newly allowed or newly blocked

## Hard rules

The timeline must never collapse:

- first realization and later survival
- hidden-device cleanup and actual retirement
- reconnect observed and reconnect-safe
- restore happened and restore survived
- current calm and horizon coverage
''',
'1977-remedy-hardening-attestation-postcondition-durability-lineage-receipt-page-steady-state-horizon-recurrence-state-and-blocked-stronger-sentences-interface-spec.md': '''# Remedy-hardening-attestation postcondition-durability lineage receipt page — steady-state horizon, recurrence state, and blocked stronger sentences

## Purpose

This page is the durable one-receipt summary for postcondition durability after postcondition realization review.
It lets a later operator read one artifact and know exactly whether the target state is merely realized now, horizon-stable for a named slice, durable for the governed slice, or still blocked by future-arrival, reconnect, replay, restore, placeholder, ghost, or path-churn recurrence risk.

## Receipt fields

- receipt identifier
- postcondition-durability identifier
- source postcondition-realization receipt identifier
- target postcondition summary
- governed-slice summary
- steady-state horizon summary
- future-arrival summary
- reconnect and hidden-returner summary
- replay and overwrite summary
- restore and rearchive summary
- placeholder, ghost, or path-churn summary
- current postcondition-durability class
- highest honest durability sentence
- blocked stronger sentence
- evidence references
- issued-at timestamp

## Primary sentence block

The receipt must begin with exactly two lines:

- **Highest honest postcondition-durability sentence**
- **Blocked stronger sentence**

## Required sections

1. **What target state is already realized now**
2. **Which survivor lanes can still re-enter the governed world**
3. **Which witnesses show stability beyond first realization**
4. **Which recurrence hazards still cap the durability sentence**
5. **Why the next stronger permanence sentence is blocked**
'''
}

for name, content in new_files.items():
    (docs / name).write_text(content + "\n", encoding='utf-8')

readme_addendum = '''## Revision addendum — postcondition durability, recurrence resistance, and steady-state truth after rev0471

This tranche locks the next seam around **whether a target state that is already realized will actually stay true for the intended slice across later churn**.
The key decisions now made explicit in the archive are:

- **postcondition-realized current conformance is a first-class rung, but it is weaker than postcondition-durable current conformance across a named steady-state horizon**
- **realized now only, realized for current cohort only, future-arrival-risk-open realization, reconnect-risk-open realization, replay-risk-open realization, restore-fragile realization, placeholder-or-ghost-regression-open realization, named-slice horizon stability, governed-slice durability, and broader permanence sentence blocked are different truths**
- **first realization is weaker than repeated survival, repeated survival is weaker than horizon-bounded durability, and horizon-bounded durability is weaker than any broader permanence language that still remains blocked**
- **linked-device auto-arrival, reconnectable folders, hidden-returner devices, paused-share side effects, archive restore fragility, ghost-file warnings, offline overwrite precedence, and path churn can no longer silently impersonate `the remedy will stay landed`**
- **every serious post-realization durability sentence now needs one receipt that preserves the source realization receipt, steady-state horizon, future-arrival cohort, survivor lanes, recurrence hazards, highest honest durability sentence, and the blocked stronger sentence**

New docs added in this tranche:

- `1972-resilio-remedy-hardening-attestation-postcondition-durability-recurrence-and-steady-state-fragmentation-evaluation.md`
- `1973-remedy-hardening-attestation-postcondition-durability-contract-sheet-page-steady-state-horizon-recurrence-budget-and-survivor-lanes-interface-spec.md`
- `1974-remedy-hardening-attestation-postcondition-durability-review-page-will-the-realized-state-stay-true-across-new-arrivals-reconnects-and-later-replays-interface-spec.md`
- `1975-remedy-hardening-attestation-postcondition-durability-proof-page-survival-witnesses-recurrence-risks-and-durability-ceiling-interface-spec.md`
- `1976-remedy-hardening-attestation-postcondition-durability-timeline-page-realize-hold-drift-recur-stabilize-and-expire-events-interface-spec.md`
- `1977-remedy-hardening-attestation-postcondition-durability-lineage-receipt-page-steady-state-horizon-recurrence-state-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `the target state is true now` can no longer hide whether it is likely to stay true through later churn
- a hidden or disconnected device can no longer silently impersonate an actually retired recurrence lane
- a restored or placeholder-cleared file can no longer silently impersonate recurrence-resistant steady state
- later operators can open one receipt and see exactly which horizon is covered, which future arrivals or reconnects remain live, which recurrence hazards still dominate, and which stronger permanence sentence stayed blocked

'''

status_addendum = '''## Current frontier after rev0471 — postcondition durability, recurrence resistance, and steady-state truth

The next hard decision now frozen in the archive is that **a target state can be realized now without yet being durable across the next governing horizon**.
This tranche therefore turns **postcondition durability** into a first-class family.

What is now explicit:

- `realized now` is not `durable`
- `current visible cohort stable` is not `future-arrival safe`
- `hidden device` is not `retired device`
- `reconnected or restored once` is not `reconnect-safe or restore-safe`
- `no contradiction at this moment` is not `recurrence-resistant steady state`
- `named-horizon durability` may still be the current ceiling while broader permanence language stays blocked

Operator consequence:

Every serious post-realization durability claim now needs one artifact that names the source realization receipt, the steady-state horizon, the survivor lanes, the recurrence budget, the live hazards, the highest honest durability sentence, and the blocked stronger sentence.

## Revision addendum — status shift toward postcondition durability, recurrence resistance, and steady-state governance after rev0471

The next seam after **postcondition realization, effectuation, and settlement truth** is now explicit:

- the archive can already say whether the intended state actually became true for a named slice and survived the immediate settlement window
- it still needed to own the harder truth of **whether that realized state will stay true across later churn, future arrivals, reconnects, hidden returners, replay, restore fragility, and path churn for the intended horizon**, because realized now, realized for current cohort only, future-arrival-risk-open, reconnect-risk-open, replay-risk-open, restore-fragile, horizon-stable, governed-slice durable, and broader permanence blocked are not one consequence class
- current Resilio docs reinforce that gap because linked devices still auto-receive folders, disconnected folders can later reconnect, hidden offline devices can reappear, paused peers still sync deletions and keep indexing, offline peers can later overwrite newer work, restored files can be pushed back into Archive on rescan, ghost-file states still exist, and the changelog still records recurrence-style failures like disconnected-by-returning-offline-peer, deleted-file return, and folder duplication or return with `(1)`

This pass turns that gap into a first-class product object: **the remedy-hardening attestation postcondition-durability and recurrence-governance case**.

What is newly true in the archive:

- **postcondition-realized standing is weaker than postcondition-durable standing**
- **realized now only, realized for current cohort only, future-arrival-risk-open realization, reconnect-risk-open realization, replay-risk-open realization, restore-fragile realization, placeholder-or-ghost-regression-open realization, named-slice horizon stability, governed-slice durability, and broader permanence blocked are separate public truths**
- **first realization is weaker than repeated survival, repeated survival is weaker than horizon-bounded durability, and horizon-bounded durability is weaker than broader permanence**
- **linked-device spread, reconnect recipes, hidden-device cleanup, pause semantics, overwrite precedence, Archive rituals, ghost warnings, and path defaults now degrade into durability inputs instead of impersonating the durability verdict**
- **every serious post-realization sentence now needs one receipt that preserves source realization, horizon, future-arrival cohort, survivor lanes, recurrence hazards, highest honest durability sentence, and the blocked stronger sentence**

What remains intentionally true:

- postcondition realization still matters
- executable mandate and verdict legitimacy still matter
- observer integrity, policy conformance, remediation, and affected-party closure still matter
- but none of those may substitute for one explicit answer about whether the realized state is actually likely to stay true for the intended slice across the next governing horizon

New docs added in this tranche:

- `1972-resilio-remedy-hardening-attestation-postcondition-durability-recurrence-and-steady-state-fragmentation-evaluation.md`
- `1973-remedy-hardening-attestation-postcondition-durability-contract-sheet-page-steady-state-horizon-recurrence-budget-and-survivor-lanes-interface-spec.md`
- `1974-remedy-hardening-attestation-postcondition-durability-review-page-will-the-realized-state-stay-true-across-new-arrivals-reconnects-and-later-replays-interface-spec.md`
- `1975-remedy-hardening-attestation-postcondition-durability-proof-page-survival-witnesses-recurrence-risks-and-durability-ceiling-interface-spec.md`
- `1976-remedy-hardening-attestation-postcondition-durability-timeline-page-realize-hold-drift-recur-stabilize-and-expire-events-interface-spec.md`
- `1977-remedy-hardening-attestation-postcondition-durability-lineage-receipt-page-steady-state-horizon-recurrence-state-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `the target state is true now` can no longer hide whether it is likely to stay true after later churn
- a hidden device can no longer silently impersonate a retired recurrence lane
- one successful restore or reconnect can no longer silently impersonate steady-state durability
- later operators can open one receipt and see exactly which horizon is covered, which survivor lanes remain live, which recurrence hazards still dominate, and why the next stronger permanence sentence stayed blocked

'''

eval_addendum = '''## Addendum after rev0471 — why postcondition durability, recurrence resistance, and steady-state truth now sit on the non-clone side

Current Resilio still deserves credit for useful durability ingredients.
Those stay on the **borrow** side.

The load-bearing ingredients from current official docs are now:

- `Sync Private Identity & Linking My Devices` still says every folder added on one linked device automatically becomes available on all the other linked devices
- `Synchronization Modes` still says disconnected folders remain visible and can later be connected, while selective-sync lanes expose placeholders and still depend on an online source peer for hydration
- `Disconnecting and Removing Folders` still says disconnected folders can later reconnect, may reconnect to a different default path, and removed linked-device folders may remain on unlinked remotes
- `How to clear offline devices?` still says hiding an offline device is only visual cleanup and that the device reappears if it comes back online
- `How to pause syncing` still says paused peers still sync deletions and continue rescanning and indexing new files
- `What if several people make changes to the same file?` still says an offline peer can later overwrite newer online work
- `Using Archive for file versioning and restoring deleted files` still says restored files can be moved back into Archive on rescan if Sync was not running
- `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time.` still says ghost-file situations exist where a file was announced but no peer still has the bytes
- `Resilio Sync change log` still records recurrence-style failures such as all folders disconnecting when a 30-days-offline peer comes online, deleted files returning sometimes, and folders reappearing with `(1)` after churn

That is good durability candor.
It is also exactly why AnonSync should not clone the present page contract.
One ordinary answer to `will this already-realized state actually stay true for the governed slice across the next governing horizon?` still depends on combining linked-device auto-arrival, reconnectable folders, hidden-returner devices, pause semantics, overwrite replay, Archive restore rules, ghost-file warnings, and changelog folklore.

So this tranche freezes a stronger replacement line: **realized-now, current-cohort-only stability, future-arrival-risk-open stability, reconnect-risk-open stability, replay-risk-open stability, restore-fragile stability, horizon-bounded durability, and governed-slice steady-state durability become separate modeled truths.**

That is why this revision adds five more first-class pages: **Remedy-hardening-attestation-postcondition-durability contract sheet**, **postcondition-durability review**, **postcondition-durability proof**, **postcondition-durability timeline**, and **postcondition-durability lineage receipt**.

'''

sources_addendum = '''## rev0472 source set — postcondition durability, recurrence resistance, and steady-state horizon

The most load-bearing source set for this pass was:

- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says every folder added on one linked device automatically becomes available on the others.
- Resilio's current `Synchronization Modes` article, which still says disconnected folders remain visible and can later be connected, while selective-sync placeholder hydration still depends on an online source peer.
- Resilio's current `Disconnecting and Removing Folders` article, which still says disconnected folders can later reconnect, may reconnect to a different default path, and removed linked-device folders may still remain on unlinked remotes.
- Resilio's current `How to clear offline devices?` article, which still says hidden offline devices reappear if they come back online.
- Resilio's current `How to pause syncing` article, which still says paused peers still sync deletions and continue rescanning and indexing.
- Resilio's current `What if several people make changes to the same file?` article, which still says offline peers can later overwrite newer online work.
- Resilio's current `Using Archive for file versioning and restoring deleted files` article, which still says restored files can be moved back into Archive on rescan if Sync was not running.
- Resilio's current `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time.` article, which still says ghost-file states can arise when a file announcement outlives the actual bytes.
- Resilio's current `Resilio Sync change log`, which still records recurrence-style failures such as disconnects triggered by returning offline peers, deleted files returning, and folders reappearing with `(1)` after churn.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for candid durability ingredients
- but current Resilio still answers `will the realized state stay true across later churn?` too diffusely
- AnonSync should therefore prefer explicit remedy-hardening-attestation-postcondition-durability sheets, reviews, proofs, timelines, and durable lineage receipts over overloaded current-cohort calm, reconnect recipes, hidden-device cleanup, pause semantics, Archive rituals, ghost warnings, and changelog memory

Primary sources:

- Sync Private Identity & Linking My Devices
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Synchronization Modes
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Disconnecting and Removing Folders
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- How to clear offline devices? (desktop only)
  https://help.resilio.com/hc/en-us/articles/204762439-How-to-clear-offline-devices-desktop-only

- How to pause syncing
  https://help.resilio.com/hc/en-us/articles/206217325-How-to-pause-syncing

- What if several people make changes to the same file?
  https://help.resilio.com/hc/en-us/articles/204754209-What-if-several-people-make-changes-to-the-same-file

- Using Archive for file versioning and restoring deleted files.
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- Cannot download files / These files cannot be downloaded as there are no source peers online for too long time.
  https://help.resilio.com/hc/en-us/articles/360010899719-Cannot-download-files-These-files-cannot-be-downloaded-as-there-are-no-source-peers-online-for-too-long-time

- Resilio Sync change log
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

'''

readme = (root/'README.md').read_text(encoding='utf-8')
(root/'README.md').write_text(readme_addendum + readme, encoding='utf-8')
status = (docs/'00-status.md').read_text(encoding='utf-8')
(docs/'00-status.md').write_text(status_addendum + status, encoding='utf-8')
evalf = (docs/'10-resilio-sync-evaluation.md').read_text(encoding='utf-8')
(docs/'10-resilio-sync-evaluation.md').write_text(eval_addendum + evalf, encoding='utf-8')
sources = (docs/'sources.md').read_text(encoding='utf-8')
(docs/'sources.md').write_text(sources_addendum + sources, encoding='utf-8')

print('rev0472 applied')
