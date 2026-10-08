# Exit review and replacement interface spec

## Purpose

The archive already has an exit object model, workbench page, CLI grammar, and daemon resources.
What it still lacked was one tighter answer to a practical question:

> what must a real exit or replacement review surface literally show before apply, so AnonSync does not drift back into remove/uninstall folklore?

This document answers that question.

## Why this needs its own spec

Current Resilio docs are useful but revealing.
`How to clear offline devices?` says hide only removes an offline device from view and that it will reappear if it comes back online.
`Disconnecting and Removing Folders` separates one-device disconnect from broader remove behavior.
`How to uninstall Sync?` says the operator should unlink identity and remove remaining Standard shares first or the old instance will keep showing as offline elsewhere.
`If your device is stolen` escalates to backup, remove, unlink, delete storage state, reinstall, regenerate identity, and reshare.
`Guide to Linux, and Sync peculiarities`, `Configuring WebUI`, `Running Sync in configuration mode`, and `Power user preferences` together show that Linux/WebUI/config-mode operation has its own seams and can even ignore some destructive-action preferences.

That means the object model alone is not enough.
The archive needs a fixed interface grammar, not merely a good set of nouns.

## Core rule

Every departure-style action that matters should render through one fixed review shape before apply.
Layout may vary by channel.
Meaning may not.

The minimum fixed section order is:

1. intent and scope
2. stops now
3. stays intentionally
4. residue after apply
5. follow-up options
6. receipt promise

## Entry points

Operators should be able to enter the review from several places without getting different semantics:

- device detail → retire / replace
- share danger zone → retire presence / revoke authority / detach local presence
- recovery or replacement page → successor binding or decommission
- disclosure or access page → narrow by exit when appropriate
- report card → jump directly to reviewed exit draft
- CLI/TUI → `anonsync exit prepare ...` then `anonsync exit show ... --view review`

The entry point may choose the default subject and intent.
It must not choose a different semantic grammar.

## Review pane anatomy

### 1) Intent and scope

The header must say:

- subject kind and label
- reviewed intent label
- scope chips (`local`, `share`, `constellation`, `remote`, `time-bound`)
- freshness / drift state
- one-sentence current answer

Bad examples:

- `Remove item?`
- `This will affect other devices`

Good examples:

- `Decommission device laptop-old`
- `Replace device laptop-old with successor laptop-new`
- `Retire share presence from constellation:travel`

### 2) Stops now

This section answers what future behavior ends immediately after apply.
It may include:

- grants revoked
- sessions ended
- publication stopped
- route leases cleared
- future approvals frozen
- local daemon activity stopped

Every row should say both object and scope.
Example:

- `[constellation] revoke mutate authority for 4 shares`
- `[local] end 2 control sessions from this device`
- `[remote-observation] peers will stop receiving future announcements once they observe revocation`

### 3) Stays intentionally

This section prevents fake cleanliness.
It should show anything intentionally preserved, such as:

- recovery bundles
- local archive bytes
- audit/history receipts
- successor carry-forward state
- retained but dormant mounts

This is the section that most remove/uninstall interfaces skip and most operators later wish they had seen.

### 4) Residue after apply

This section answers what still remains and why.
Residue classes may include:

- offline peers that have not yet observed revocation
- time-bound relay or discovery cache
- remote replicas intentionally left intact
- local preserved bytes awaiting separate reclaim review
- portable artifacts or sessions that still need rotation/revocation

The section should visibly distinguish:

- `none`
- `time-bound`
- `operator-clearable`
- `requires remote observation`
- `unknown / offline`

Residue should never appear only after apply.
If known before apply, it belongs in the main review.

### 5) Follow-up options

This section lists actions that are related but not silently bundled.
Examples:

- rotate stale token
- bind successor device
- prepare reclaim plan
- re-review disclosure after quiet window
- notify steward that offline peers still have not observed revocation

The default should strongly prefer showing follow-up as explicit options instead of quietly folding them into the exit.

### 6) Receipt promise

Before apply, the operator should know what durable proof will exist later.
This section should say:

- which receipt or record will be created
- what that receipt proves
- whether unresolved residue will remain visible through that receipt

A serious operator should not have to guess whether later audit will distinguish “applied cleanly” from “applied with residue”.

## Action footer rules

The footer is where many interfaces become vague.
AnonSync should not.

Rules:

- the primary action label must inherit the reviewed intent (`Decommission device`, `Revoke authority`, `Bind successor`)
- the secondary action should usually be `Inspect residue` or `Preview successor` rather than a generic cancel/apply pair only
- danger notes should state what is **not** included in the current plan
- acknowledgement controls for residue or preserved state must be visually separate from the final apply verb

## Subject-specific variants

### Device decommission

The device variant should emphasize:

- grants and approvals ending
- sessions ending
- route or publication references being cleared
- successor and recovery posture
- local preserved bytes or state roots still present

### Share presence retirement

The share variant should emphasize:

- whether this is local detach, authority revocation, or broader share-presence retirement
- whether remote replicas remain valid
- whether projection/publication narrowing is bundled or separate
- whether version history or rollback candidates remain

### Daemon decommission

The daemon variant should emphasize:

- control access ending
- background runtime shutdown
- state root, recovery bundle, and preserved archives
- whether exported recovery or diagnostic material still exists elsewhere

## Compare view

A rich workbench may show two columns (`before` and `after`) or a diff-like list.
That is fine.
But the compare view should still collapse into the same six-section grammar.
The product must not have one story in the compare pane and a different story in the textual summary.

## Channel-parity rules

This spec applies equally to:

- local GUI
- local web workbench
- TUI
- CLI summary view
- automation-facing review derived from daemon data

Allowed differences:

- density
- layout
- amount of nearby history shown by default
- whether the proof panel is side-by-side or inline

Disallowed differences:

- different intent class labels
- missing residue categories on one channel
- missing continuity/preservation truth on one channel
- different acknowledgement requirements
- a generic destructive verb on one channel where another names the reviewed intent explicitly

## Minimum textual rendering

A narrow textual surface should still be able to render:

```text
Intent & scope
Stops now
Stays intentionally
Residue after apply
Follow-up options
Receipt promise
```

with rows tagged by scope and freshness visible near the header.
Anything less is not a safe projection of the model.

## Why this matters

AnonSync is not justified merely by having more nouns than other sync tools.
It is justified only if the operator can understand high-consequence departure actions more clearly than they can in systems where hide, unlink, disconnect, uninstall, and stolen-device repair are spread across different rituals.

That requires one fixed review grammar.
Not because consistency is pretty, but because consistency is part of the trust model.
