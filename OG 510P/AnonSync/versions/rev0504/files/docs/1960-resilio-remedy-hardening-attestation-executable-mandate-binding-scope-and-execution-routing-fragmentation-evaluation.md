# Resilio remedy hardening attestation executable mandate, binding scope, and execution-routing fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for being candid that `the verdict looks legitimate`, `the permission looks changed`, `the linked device should now have access`, `the local share should inherit the new posture`, `the service should now behave the same way`, and `the intended change is therefore binding and executed everywhere it matters` are not one flat truth.
That candor is useful.

The strongest present ingredients are:

- current `Sync Private Identity & Linking My Devices` docs still say that once devices are linked, all folders automatically become available on all linked devices, that remote users can auto-approve future sharing across linked devices, and that approvals can be issued from any linked device where the folder is present
- current `Comprehensive guide to syncing (Desktop-Desktop)` docs still say linked devices receive automatic full read-write access while manual sharing is the path where access privileges can be chosen folder by folder
- current `User Management` docs still say Advanced-folder permissions can be changed without disrupting synchronization, and disconnect revokes future updates while leaving already synchronized files in place
- current `How to create a Read Only folder while syncing across linked devices?` docs still say linked devices automatically receive Owner permission and that a read-only result on a linked device requires a Standard-folder Read Only key detour plus manual disconnect and manual re-entry
- current `Sharing a folder locally` docs still say local shares cannot receive Owner permission, Advanced local-share permissions cannot be changed through user management and instead require remove-and-re-share, and reconnecting a source share does not automatically reconnect the local share
- current `Running Sync in configuration mode` docs still say one config can apply settings across many machines at start, but only for Standard folders, and that shared folders declared in config disable WebUI and override folders previously added from WebUI
- current `Sync Service Troubleshooting on Windows` docs still say service-user changes can create a different storage world where old folders are absent and require re-add plus re-share or reconnect, and that some WebUI exposure changes require service restart
- current `Running Sync on schedule` docs still say `Paused` stops uploads and downloads but still allows file deletions to sync and new files to be rescanned and indexed

## Where the current contract still fragments

The problem is not that Resilio lacks execution knobs.
The problem is that it still does not produce one first-class, case-scoped **executable-mandate and execution-routing** object.

Today an operator can often infer only weaker truths such as:

- this linked device should now inherit access automatically
- this manual share path can produce a different access result than the linked-device path
- this permission change is live for one peer class but not for another topology
- this local derivative share must be removed and re-shared instead of mutated in place
- this configuration can shape startup state for Standard folders but not for Advanced folders
- this service world can require restart or even a world fork before the intended effect exists
- this scheduler or pause state still allows some side effects to continue

Those are useful clues.
They are not the same as an explicit answer to `who is now actually bound, through which execution path, by which deadline, with which actuator and fallback, and what stronger execution-complete sentence is still blocked?`

## Why that matters for AnonSync

AnonSync needs a stronger sentence than `the verdict is legitimate`.
It needs to support claims such as:

- the verdict is legitimate, but advisory only because no mandate has been issued yet
- the verdict is binding for a named operator cohort only, not for the entire estate
- the mandate exists, but the chosen actuator is unavailable in this world or topology
- the execution route exists, but manual steps still remain for a read-only detour, re-share, reconnect, or restart
- execution has started, but only a named slice has completed and broader execution remains blocked
- a fallback path is now governing because in-place mutation was unsupported
- the product can justify `mandate issued` or `execution pending`, but not yet `execution complete`

AnonSync therefore needs first-class objects for **binding scope, obligated actor set, required action set, actuator class, chosen execution route, deadline, fallback route, execution witness, execution-failure class, highest honest execution sentence, and blocked stronger sentence** rather than leaving operators to infer execution truth from linked-device defaults, permission toggles, manual detours, restart folklore, or scheduler side effects.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `now that the verdict is legitimate, who is actually bound and has execution really landed?` — only by making the operator combine several partially overlapping mechanics:

- linked-device automatic spread and approval memory
- manual folder-sharing lanes with separate privilege semantics
- live permission changes for some cases and remove-and-re-share replacement for others
- local-share inheritance and non-reconnection behavior
- Standard-only config rollout with WebUI override side effects
- service-user world forks, re-add or reconnect requirements, and restart gates
- paused lanes that still propagate deletions or indexing side effects

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **executable mandate, binding scope, and execution routing** directly.
Its interface family should let the product separate at least these truths:

- legitimate verdict, advisory only
- legitimate verdict, mandate draft pending ratification
- mandate issued for named cohort only
- mandate issued, actuator unavailable
- mandate issued, execution pending within deadline
- deadline missed, fallback required
- partially executed for named slice only
- fully executed for named slice
- broader stronger sentence blocked
