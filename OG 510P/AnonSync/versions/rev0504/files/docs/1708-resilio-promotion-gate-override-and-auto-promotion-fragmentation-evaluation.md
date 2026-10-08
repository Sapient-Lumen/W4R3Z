# Resilio promotion-gate, override, and auto-promotion fragmentation evaluation

## Claim

Current official Resilio docs are still admirably candid that `green now`, `warnings absent`, `approval notification seen`, `history looks quiet`, `all connected peers synced`, `hidden work may still be running`, `rescan may still discover more`, and `the stronger sentence is now safe to promote` are not one flat truth.
That candor is useful.
It is also exactly why AnonSync should not clone the present contract.

The missing product object is now sharper than stability:

> after the product knows **an effect was attained and even stability-earned under the current rule**, it still needs one first-class answer to **whether the stronger sentence is actually authorized to go live now, through which lane, under what automation policy, with what override debt, and under what demotion trigger**.

Current Resilio materials still do not provide one typed promotion object for:

- distinguishing stable-enough evidence from stronger-sentence authorization
- distinguishing review-eligible from auto-promotable
- distinguishing manual promotion from override promotion
- preserving that warnings, hidden work, delayed rescans, or no-source residue may still keep stronger promotion blocked
- preserving which stronger sentence is merely visible as the next step versus actually armed for execution
- preserving who may override the gate, for how long, and with what residue or debt
- preserving what event would demote or reopen the stronger sentence after promotion

Instead, the operator still has to translate green checks, peer counts, bell notifications, short-window history, warning pages, and troubleshooting caveats into a judgment about whether the system may actually speak the stronger sentence.

## What current official docs still say

Current official docs still jointly show all of the following:

- `Sync Main View (Desktop)` still says a green checkmark means files are synced with all connected peers, the bell lights up for approval requests or other notifications, and History shows general syncing activity for the last 30 days.
- `Core warnings` still treats issues like watcher exhaustion, hidden internal tasks, unavailable sources, database errors, and time-difference problems as separate warning families rather than one combined decision object.
- `Some internal tasks are taking time to complete` still says background operations such as hashing, reading, comparing, block checking, and other hidden work can continue while Sync later recovers on its own.
- `Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan` still says update discovery can degrade to manual or periodic rescan when watcher limits are hit.
- `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time.` still says an announced or expected file may still lack any actually available source peer by the time retrieval is attempted.

This is strong operational candor.
It is not a first-class promotion contract.

## Why this still fragments the decisive answer

One ordinary fairness answer still requires stitching together several docs and surfaces:

- whether the evidence is merely stable or also promotion-worthy for the next stronger sentence
- whether the next stronger sentence is manual-only, auto-eligible, override-only, or still blocked
- whether the absence of a visible warning is meaningful enough to arm automation
- whether hidden work, delayed rescan, or missing-source residue should keep a stronger sentence frozen
- whether an operator is making a narrow allowed promotion or silently leaping to a stronger irreversible one
- whether an override creates explicit debt, probation, review expiry, or later demotion exposure

That means current official materials can help answer `is the share quiet now`, `are connected peers synced`, `did a notification appear`, `what warnings exist`, or `why more work may surface later`.
They still do not directly answer `may the product promote this case to the stronger sentence now, through which lane, and on what responsibility basis?`

That gap is exactly where AnonSync should refuse cloning.

## Hard replacement line for AnonSync

AnonSync should borrow the useful ingredients:

- explicit connected-vs-total peer candor
- explicit bell-and-history visibility for operational cues
- explicit warnings for delayed discovery, hidden work, and no-source residue
- explicit acknowledgement that calm-looking UI does not mean nothing else can happen

But AnonSync should replace the page contract with a first-class **promotion gate** object where each stronger sentence has its own:

- prerequisite proof bundle
- smallest already-earned sentence
- next stronger sentence being considered
- manual-only versus auto-promotable policy row
- confidence or cleanliness floor for auto-promotion
- named reviewer or override authority
- override reason, expiry, and debt consequences
- demotion and reopen triggers
- promotion timeline
- promotion lineage receipt

## Product decision tightened here

The new design line is:

- **stability-earned is weaker than promotion-authorized**
- **review-eligible, manual-only, auto-promotable, promoted, override-promoted, override-denied, demoted, and re-armed are different truths**
- **automation eligibility is typed per stronger sentence and is not inherited just because the lower rung looks calm**
- **manual override never hides its actor, reason, expiry, debt, or demotion triggers**
- **later regressions, newly surfaced warnings, delayed discoveries, or policy changes may demote a previously armed stronger sentence without erasing the earlier history**

## Consequence for the non-clone score

Resilio still belongs on the borrow side for operational candor about statuses, notifications, history, and warning families.
Resilio remains on the non-clone side for the fairness-critical promotion contract.

The reason is now precise:

> current Resilio docs still expose green connected-peer calm, bell notifications, short-window history, warning families, hidden internal work, rescan fallback, and no-source residue as separate operational facts rather than one typed promotion object for `is the stronger sentence actually authorized to go live now, through which lane, with what automation rights, override debt, and demotion triggers?`, so the operator still has to reconstruct whether the product may speak the stronger sentence instead of merely seeing that the system looks calmer.
