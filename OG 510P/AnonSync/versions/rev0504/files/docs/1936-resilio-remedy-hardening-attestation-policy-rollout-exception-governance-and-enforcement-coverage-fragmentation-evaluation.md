
# Resilio remedy hardening attestation policy rollout, exception governance, and enforcement-coverage fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for being unusually candid that a setting existing, a setting being a default, a setting being present on one platform, and a setting actually governing an estate are not one flat truth.
That is useful.

The strongest present ingredients are:

- current `Running Sync in configuration mode` docs still say one configuration can apply pre-configured parameters at program start across a number of different machines, but only for Standard folders
- current `Folder Preferences` docs still say important behavior remains configured on a folder-by-folder basis and is available on desktop platforms only
- current `Power user preferences` docs still say some defaults apply only to shares whose priority was not altered manually in folder preferences
- current `Ignoring files in Sync (Ignore List)` docs still say same IgnoreList across peers is advisable but not compulsory, existing structure already stored in the database keeps propagating, and immediate application may require a restart
- current `How to create a Read Only folder while syncing across linked devices?` docs still say linked devices auto-receive Owner permission and a read-only outcome on a linked device requires a Standard-folder manual detour
- current `Sharing a folder locally` docs still say local shares are desktop-only, inherit from a source folder, and some permission changes require remove-and-re-share rather than live mutation
- current `Sync Preferences` docs still say some defaults are platform-scoped rather than universal
- current `Resilio Sync 3.0 change log` still records UI, warning, and interaction fixes, which matters because a rollout that looked complete on one surface is not automatically durable enforcement

## Where the current contract still fragments

The problem is not that Resilio lacks deployment mechanics.
The problem is that it still does not produce one first-class, case-scoped **policy rollout and exception-governance** object.

Today an operator can often infer only weaker truths such as:

- this default exists in config mode for Standard folders
- this preference exists per folder on desktop
- this power-user default stops applying after a manual per-share override
- this ignore rule is recommended everywhere but not required everywhere
- this linked-device path still needs a manual Standard-folder detour to achieve one read-only outcome
- this local-share branch inherits from the source but cannot always be retuned in place
- this platform can show a control the other platform cannot

Those are useful clues.
They are not the same as an explicit answer to `has this portable rule actually been deployed for the intended estate slice, which populations remain grandfathered or manually overridden, which waivers are active, which exceptions expire when, and what stronger estate-wide sentence is still blocked right now?`

## Why that matters for AnonSync

AnonSync needs a stronger sentence than `this closed case became a reusable rule`.
It needs to support claims such as:

- the rule is portable, but rollout has not started
- rollout exists for a named cohort only
- deployment is complete for one platform class and not another
- manual overrides still exempt part of the estate
- waivers exist, but they are named, owned, time-bounded, and counted as debt rather than hidden variance
- the strongest honest sentence is `enforced for named slice with three expiring exceptions`, not `estate-wide policy now in force`

AnonSync therefore needs first-class objects for **policy scope, target estate slice, deployment owner, effective control family, verification sample, override inventory, waiver inventory, grandfathered population, expiry debt, enforcement coverage class, blocked broader sentence, and next evidence that upgrades or collapses rollout truth** rather than leaving operators to infer estate reality from config files, per-folder toggles, manual detours, and remembered defaults.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `did this precedent actually become governing policy for the intended estate?` — only by making the operator combine several partially overlapping mechanics:

- config-mode rollout across machines but Standard-only scope
- desktop-only per-folder preferences
- manual per-share overrides that break later default following
- non-compulsory IgnoreList sameness and delayed immediate effect
- linked-device Owner defaults plus manual read-only detours
- local-share inheritance and re-share-only permission changes
- platform-scoped defaults and current-version UI behavior

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **policy rollout, exception governance, and enforcement coverage** directly.
Its interface family should let the product separate at least these truths:

- precedent portable, rollout not started
- rollout proposed, target slice named
- deployment active for named slice only
- deployed but verification incomplete
- enforced for named slice with bounded waivers
- grandfathered population still outside policy
- exception debt above budget
- review overdue or waiver expiry reached
- policy retired, narrowed, or superseded
- broader estate-wide sentence blocked
