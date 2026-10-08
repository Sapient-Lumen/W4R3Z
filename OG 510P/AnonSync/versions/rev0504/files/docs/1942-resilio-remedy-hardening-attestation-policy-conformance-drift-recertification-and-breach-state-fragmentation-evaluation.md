# Resilio remedy hardening attestation policy conformance, drift recertification, and breach-state fragmentation evaluation

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
