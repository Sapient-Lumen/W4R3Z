# Release channel, upgrade, and compatibility-boundary spec

## Purpose

The archive already had preflight reports, state-root transition rules, transport-runtime lifecycle guidance, and scattered warnings about mixed-version linking or capability mismatch.
What it still lacked was one public contract for a simpler operational question:

> what release family, edition, channel, schema, and compatibility boundary is this subject on right now, what change is being proposed, what will remain compatible, and what rollback or cutover truth survives if we move?

This document answers that question.
It exists so AnonSync does not recreate a common sync-product failure mode where safe upgrade knowledge lives in NAS-specific warnings, changelogs, update FAQs, license notes, or support-only memory instead of the operator surface.

## Resilio-derived motivation

Current Resilio docs still distribute release and compatibility truth across several separate surfaces:

- desktop update settings and update instructions explain how to notice or install updates, but not one durable compatibility contract
- v3 update guidance says only Home/Free/Pro installs may update and that Business installations must not update to v3 because configured shares can be lost even if files remain on disk
- Linux/NAS install pages repeat the same edition/version-family warning across platform-specific articles
- the linking guide warns that mixing v2 and v3 inside one linked-device constellation can conflict on licensing and lead to lost access to UI and share configuration
- changelog notes and support articles still carry some of the real migration lore, such as migration-specific fixes, autoupdate quirks, or custom-config preservation details

Those are useful support notes.
They are not one durable release-compatibility contract.

## Core rule

Release posture is explicit state.
Installed version, edition/family, release channel, schema epoch, supported downgrade span, peer/cluster compatibility class, transport-bundle compatibility, and proposed cutover target are separate public facts.
They may be related.
They may not collapse into one intuition such as “an update exists”, “the peers can still sync”, or “the installer probably preserves my shares”.

## Public objects

### Release posture

A first-class summary of current release truth for one subject.

Fields:

- `release_posture_id`
- `subject_ref`
- `subject_kind` (`daemon`, `transport-bundle`, `workbench-client`, `peer-constellation`)
- `installed_version`
- `edition_family`
- `release_channel` (`stable`, `candidate`, `nightly`, `pinned`, `vendor-packaged`, `local-build`)
- `schema_epoch`
- `api_epoch`
- `compatibility_family`
- `update_state` (`current`, `update-available`, `security-update-available`, `pinned-outdated`, `mixed-family`, `migration-blocked`, `unknown`)
- `downgrade_posture` (`safe-window`, `config-risk`, `schema-risk`, `unsupported`, `unknown`)
- `peer_skew_summary`
- `linked_constellation_state` (`uniform`, `mixed-version`, `mixed-edition`, `mixed-channel`, `unknown`)
- `last_checked_at` nullable
- `next_review_at` nullable

### Upgrade plan

A reviewed proposal to move one or more subjects across a release boundary.

Fields:

- `upgrade_plan_id`
- `subject_refs[]`
- `current_release_refs[]`
- `target_release`
- `channel_change` nullable
- `edition_change` nullable
- `required_cutover_scope[]` (`restart-only`, `drain-and-restart`, `plan-bearing-share-reopen`, `state-root-verify`, `manual-repair-followup`)
- `compatibility_findings[]`
- `schema_change_state` (`none`, `forward-only`, `reversible-window`, `unknown`)
- `rollback_posture`
- `blocked_by[]`
- `warnings[]`
- `preconditions[]`
- `expires_at` nullable

### Release receipt

A durable record proving that release posture changed, an upgrade plan was applied, or an operator explicitly accepted a compatibility boundary.

Fields:

- `release_receipt_id`
- `action` (`check-release`, `adopt-channel`, `apply-upgrade`, `complete-cutover`, `record-rollback`, `accept-compatibility-boundary`)
- `subject_refs[]`
- `from_release`
- `to_release`
- `channel_delta`
- `schema_delta`
- `compatibility_delta`
- `accepted_warnings[]`
- `created_at`

## Rules

1. **Update availability is not upgrade readiness.**  
   A newer build may exist while schema change, edition mismatch, mixed-family linking, or policy drift still block honest adoption.

2. **Compatibility must be workflow-specific.**  
   “Can connect” is too weak. Peer sync compatibility, linked-constellation safety, access/workbench API compatibility, and downgrade safety need separate truth.

3. **Edition/family boundaries must be explicit.**  
   Personal/Home/Business-style distinctions cannot stay hidden behind download pages or installer choice. If a target family changes share or license semantics, the surface must say so directly.

4. **Mixed-version constellations must stay visible.**  
   A cluster can be partially compatible yet still unsafe for linking, auto-approval, or configuration carry-forward. Operators should see that without reading release notes.

5. **Rollback posture must be first-class.**  
   “Just reinstall the old version” is not a product contract. The model must say whether rollback is safe, schema-risky, config-risky, or unsupported.

6. **Transport/runtime bundles are separate from daemon release truth.**  
   Embedded Tor/I2P payloads, helper binaries, or other runtime pieces may move on different cadences, but the operator must still see the exact compatibility boundary and provenance.

7. **Receipts matter as much as version numbers.**  
   Later audit should prove which warnings were accepted, what compatibility class was in force, and what cutover/rollback story was promised at apply time.

## CLI contract

Minimal commands:

```text
anonsync release show
anonsync release show --subject daemon
anonsync release check
anonsync release compare --peer laptop-02
anonsync release plan create --target stable-1.2.0
anonsync release plan create --target candidate-1.3.0-rc1 --allow-channel-shift
anonsync release plan show rup_01J...
anonsync release plan apply rup_01J...
anonsync release receipt show rlr_01J...
```

These commands should answer:

- what version/family/channel/schema is active right now
- whether an available target is merely newer or actually safe for this subject constellation
- whether peer sync, linked-device semantics, API clients, or bundled runtimes would cross an important compatibility boundary
- what rollback posture remains if the proposed target is adopted
- what receipt proves the change or the accepted warning boundary later

## Workbench contract

The workbench should expose a `Releases` page distinct from both `System State` and `Recovery`.
Its job is not to replace package managers.
Its job is to answer:

- what release posture the daemon, bundled runtimes, and important peers are on right now
- whether the constellation is uniform or carries risky version/family/channel skew
- what a proposed upgrade would preserve, block, or narrow
- whether rollback is supported, guarded, or explicitly not promised

The page should support:

- filtering by subject kind, channel, update state, and compatibility family
- comparing current posture against a candidate target before any real mutation
- creating a reviewed upgrade plan that names restart, drain, or post-cutover verification requirements
- inspecting receipts for release checks, accepted compatibility boundaries, applied upgrades, and recorded rollbacks
- jumping from a blocked upgrade plan to the precise finding, such as mixed-family linkage, schema-risk, or unsupported edition change

## Design tests

The model is not explicit enough if any of the following remains true:

- the operator still needs NAS- or platform-specific download pages to know whether this installation may cross into another edition family
- a linked constellation can be mixed-version or mixed-edition without the workbench/CLI naming that as a first-class state
- an update can be “available” while downgrade or rollback truth remains implicit
- release-channel changes and daemon upgrades silently widen observability, telemetry, or runtime-bundle behavior
- later audit cannot prove which compatibility warnings were accepted when the cutover happened

## Outcome

A mature AnonSync surface should let an operator move from `is there a new version?` to `for which subject?` to `what compatibility boundary does it cross?` to `what cutover and rollback truth survives if I move?` without leaving the shared public model.
That is what this document locks in.
