# Target-custody and exclusive-bind review spec

The archive already has state roots, mount binding, local derivation, topology review, bring-up review, and mutation gating.
This document answers the narrower practical question those abstractions still left open:

> what must a real operator surface literally show before a daemon, state root, or host profile claims a local target that may already carry sync state, so AnonSync does not drift back into hidden-marker folklore, double-binding corruption, or “just re-add after deleting internal files” recovery ritual?

This is the host-local custody companion to `42-state-root-and-service-profile-spec.md`, the path-claim companion to `43-mount-binding-repair-and-preservation-spec.md`, the same-host safety companion to `73-local-derivation-and-self-edge-review-spec.md`, and the textual-parity companion to `39-interface-pattern-language.md`.

## Why this needs its own spec

Resilio's docs make the seam unusually clear.
`Service files missing / Cannot identify destination folder` says every synced folder gets a hidden `.sync` folder whose ID is critical for synchronization, that deleting or corrupting it suspends sync, and that the error can also appear if two Sync instances use the same folder on one computer or on one external disk.
The same article says that if folder A is added to Sync instance A and then to Sync instance B, the internal files of the former instance can be corrupted and the recovery path is to make sure nothing important remains in archive, delete `.sync`, remove the share, and add it back.
`Selected folder is already added to Sync` adds that the same `.sync/ID` marker is how Sync decides a folder is already present on one device.
`Cloning Sync` separately says plain-copy cloning of an instance is unsupported.

The lesson is not merely that hidden service folders are awkward.
The lesson is that a useful product can still leave one of the most dangerous local questions under-specified:

- which daemon/state-root/service-profile currently owns this target
- whether a discovered marker means same-subject continuation, foreign-instance residue, stale abandoned state, or an active collision
- whether the safe next step is ordinary attach, reviewed successor claim, local derivation, inspect-only import, or hard block
- whether an external disk moved between hosts is being treated as supported continuity, unsupported clone instinct, or silent corruption risk

AnonSync should not clone that shape.

## Core rule

A non-trivial local target claim should always compile to a reviewed target-custody surface.
That includes at least:

- any target where AnonSync discovers prior custody markers, active state receipts, or foreign daemon lineage
- any target reachable from multiple local runtimes, service profiles, or host identities where simultaneous ownership is plausible
- any removable or external storage that may have been attached to another host or another AnonSync state root
- any case where the requested bind would collide with active local derivation, overlap review, or existing mount binding
- any recovery, attach, successor, or profile-switch action where hidden marker state could be mistaken for ordinary empty-path adoption
- any cleanup path that would otherwise ask the operator to delete hidden internal state before the system honestly explains what continuity or residue story that marker represents

A channel may compress the review when risk is truly low.
It may not replace the meaning with vague `Use this folder`, `Reconnect here`, `Delete internal files`, or `Add anyway` prose.

## Entry points that must converge

The product may offer several ergonomic entry points:

- workbench path picker `Review custody`
- state-root page `Inspect discovered target ownership`
- bind/repair page `Resolve foreign marker`
- CLI `custody inspect --path /mnt/archive`
- CLI `custody review --path /mnt/archive --intent attach`
- CLI `custody show <binding_collision_case_id> --view review`
- a daemon-side refusal that emits a custody case instead of corrupting one instance or silently stealing the target from another

But these must all converge on the same public target-custody model.
The operator should never have to wonder whether one surface is merely warning about a non-empty path while another is the only place that actually explains host-local ownership, marker lineage, and admissible continuity actions.

## Fixed review order

Every non-trivial target-custody review should render the same sections in the same order:

1. **Target and discovered markers**
2. **Current custody and lineage**
3. **Requested bind and continuity story**
4. **Collision and corruption risk**
5. **Admissible custody actions**
6. **Receipt promise**

### 1) Target and discovered markers

This section should show:

- the requested target path and host/storage tier
- discovered custody markers, internal IDs, or receipts if any
- whether the target is empty, known-managed, foreign-managed, ambiguous, or partially degraded
- whether the path is local-native, removable, network-reviewed, or otherwise warning-tier

The operator must be able to answer: **what path am I about to claim, and what sync-state evidence already exists there?**

### 2) Current custody and lineage

This section should show:

- which daemon, state root, service profile, or host last claimed the target when that can be proven
- whether the discovered claim matches the currently active local state universe, a sibling local profile, a successor candidate, or an unknown/foreign lineage
- whether the prior claim looks active, stale, abandoned, superseded, or collision-prone
- whether the target also participates in local derivation, overlap review, or another active topology relationship

The operator must be able to answer: **who seems to own this target now, and is that ownership part of my current continuity story or somebody else's?**

### 3) Requested bind and continuity story

This section should show:

- whether the operator is trying to adopt into the same subject, attach known state, claim as successor, derive locally, inspect only, or clear abandoned residue
- whether the requested action preserves the same subject identity, creates a new local target, or would fork/collide with existing lineage
- whether the requested action is ordinary continuation, reviewed continuity, or already blocked pending stronger proof
- whether the action would rewrite marker state, preserve it, consume it into a new receipt, or leave it untouched

The operator must be able to answer: **what local continuity story am I claiming for this path, and does the product agree that it is honest?**

### 4) Collision and corruption risk

This section should show:

- whether simultaneous or recent multi-instance ownership is suspected
- whether the target could corrupt active state, split one logical subject across two local universes, or silently shadow an existing bind
- whether removable-media movement, service-profile drift, or stale marker damage weakens confidence
- whether recovery/preservation state exists before any marker rewrite or cleanup

The operator must be able to answer: **if I continue, am I safely continuing one story, or am I about to collide, fork, or destroy evidence?**

### 5) Admissible custody actions

This section should show:

- reuse the existing verified local bind
- attach as reviewed same-lineage continuation
- prepare successor/re-home claim
- narrow to inspect-only or compare-only mode
- preserve evidence and block active claim
- clear explicitly abandoned marker state only after reviewed acknowledgement

The operator must be able to answer: **what safe custody actions are actually available for this target right now?**

### 6) Receipt promise

This section should show:

- which custody receipt will exist after apply, defer, reject, or cleanup
- what it will later prove about target path, discovered markers, prior lineage, chosen continuity story, and any preserved evidence
- whether the receipt remains provisional because lineage or marker integrity is ambiguous
- what later audit survives if the target is later rebound, moved again, or reused by another runtime

The operator must be able to answer: **what later evidence will prove why this path was claimed, blocked, or cleaned up?**

## Action hierarchy inside target-custody review

The primary action should be the safest meaningful next step.
Examples:

- target clearly belongs to the current active root and subject → `Reuse verified bind`, not `Create new share`
- external disk carries foreign-managed markers with weak lineage proof → `Inspect only and preserve evidence`, not `Delete marker and continue`
- requested attach matches a reviewed successor plan → `Prepare successor claim`, not `Add as ordinary path`
- same host appears to have two active local runtimes contesting the path → `Block collision and inspect owners`, not `Take over target`

Convenience labels such as `Use folder`, `Reconnect`, `Add share`, or `Delete .sync` should be visually separate and usually not primary.

## Public objects

### Target custody record

A first-class object describing the currently known ownership and lineage posture of one local target.

Fields:

- `target_custody_record_id`
- `path`
- `storage_tier`
- `marker_state` (`none`, `known-managed`, `foreign-managed`, `stale-managed`, `degraded`, `ambiguous`)
- `current_owner_subject_ref` nullable
- `current_owner_state_root_ref` nullable
- `current_owner_service_profile_ref` nullable
- `lineage_confidence` (`high`, `guarded`, `low`, `unknown`)
- `collision_state` (`none`, `possible`, `active`, `historical`, `blocked`)
- `preservation_requirement` (`none`, `recommended`, `required`)
- `last_verified_at`

### Binding collision case

A first-class reviewed case describing why one requested path claim is guarded or blocked.

Fields:

- `binding_collision_case_id`
- `target_path`
- `requested_intent` (`adopt`, `attach`, `successor-claim`, `derive-local`, `cleanup`, `inspect-only`)
- `related_subject_refs[]`
- `related_state_root_refs[]`
- `risk_class` (`collision`, `fork`, `residue-uncertain`, `marker-degraded`, `unsupported-clone-like`, `other`)
- `safe_actions[]`
- `required_preservation_refs[]`
- `created_at`
- `updated_at`

### Custody receipt

A first-class receipt proving how target ownership or marker cleanup was reviewed and applied.

Fields:

- `custody_receipt_id`
- `target_path`
- `pre_state_summary`
- `applied_action`
- `post_state_summary`
- `lineage_claim`
- `evidence_preserved`
- `operator_acknowledgements[]`
- `recorded_at`

## What the surface must never imply

The target-custody surface must never imply that these are the same thing:

- non-empty path comparison versus discovered sync-state ownership
- same-lineage attach versus foreign-marker takeover
- successor/re-home continuity versus ordinary local adoption
- removable-disk reuse versus supported shared local ownership
- cleanup of abandoned markers versus recovery-proof destruction
- blocked collision versus harmless duplicate visibility

If the product compresses those differences, it has recreated the ritual it is trying to replace.

## Linux/headless parity rule

A Linux-first product has to assume that path claims often happen through CLI, SSH, headless daemons, and service-profile transitions.
So the reviewed target-custody grammar must survive across those channels.
It is not acceptable for one richer surface to show lineage, owners, collision risk, and evidence posture while Linux/headless falls back to `folder not empty`, `already managed`, or `delete internal files and retry` folklore.

## Cross-links to other review models

Target-custody review should often hand off to nearby review families, but it should not dissolve into them.

- **Bring-up review** answers what opening a host/state/control entry means.
  Target-custody review answers whether this specific path can honestly join that story.
- **Mount binding review** answers how a chosen subject binds to a chosen path over time.
  Target-custody review answers whether the path is safely claimable at all.
- **Successor cutover review** answers broader continuity-sensitive replacement.
  Target-custody review answers whether a candidate target really belongs to that replacement story.
- **Local derivation review** answers how one source fans into another same-host target.
  Target-custody review answers whether the target is even available for that relationship.

## CLI projection expectation

A textual projection should be able to render the fixed review order directly, for example through `anonsync custody show <binding_collision_case_id> --view review`.
That output should be good enough that a headless operator does not need a richer workbench merely to learn whether a target is empty, already owned, lineage-safe, collision-prone, or only cleanable after explicit preservation.

## Why this is worth the trouble

AnonSync only justifies its extra complexity if host-local safety also becomes easier to read.
A fixed target-custody grammar is how the archive avoids rebuilding a system where hidden markers, service-account drift, external-disk reuse, unsupported clone warnings, and `delete internal files then add back` recovery notes are all individually documented, yet the full meaning of “who already owns this target, under which continuity story, and what is the safe next step?” still depends on which troubleshooting page the operator happened to remember first.
