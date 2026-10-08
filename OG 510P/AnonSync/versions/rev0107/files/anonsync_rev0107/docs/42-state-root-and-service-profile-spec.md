# State root and service profile spec

## Purpose

This document makes one operator seam first-class:

> which durable state is this AnonSync instance actually using, under which runtime/service profile, and how can that state be inspected, moved, exported, attached, or replaced without folklore?

This matters because several Resilio Sync documents reveal the same hidden coupling from different angles:

- Linux/headless startup can create or reuse a storage root based on `--storage` or the current directory
- WebUI/service installs create a different-feeling control experience even when they are meant to represent the same product
- Windows service install choices explicitly distinguish migrated state from a clean install
- unsupported cloning is still the answer for one tempting class of “just copy the app state” recovery attempts

AnonSync should not leave those seams implicit.
The product should surface them as ordinary operator state.

## Core rule

State roots, identity roots, and service profiles are not implementation leftovers.
They are first-class operator objects.

That means:

- an operator can inspect which root is active right now
- a daemon can prove which shares, identity, and caches belong to that root
- changing runtime profile does not silently switch to a different hidden universe
- export, attach, move, and replace transitions are supported workflows with plans and receipts
- every state-root transition is auditable and explainable later

## Vocabulary

### State root

A durable local state root is the on-disk home for one AnonSync control universe.
It may contain:

- identity material
- local inventory metadata
- share and mount records
- cached route / contact / approval memory according to policy
- transport runtime state allowed to persist
- audit and event indexes according to retention policy

A state root should have a stable ID and an inspectable path.
A path alone is not the identity of the root.

### Identity root

The identity root is the subset of durable state that defines who this device claims to be for AnonSync purposes.
It may be exportable or replaceable under stricter rules than ordinary cache state.

### Service profile

A service profile is the runtime context through which a state root is opened.
Examples:

- foreground workstation session
- managed background service
- local web workbench process
- recovery/maintenance invocation with restricted mutation rights

The point of the profile is not branding.
It is to make runtime context inspectable without changing the underlying semantics.

## Non-negotiable design rules

1. **One root, one answer.**
   Every surface should be able to say which state root is active and where it lives.

2. **Profile changes are not identity magic.**
   Switching from foreground app to service or local web workbench may change process privileges and startup behavior, but it should not silently change share inventory, identity, or trust state.

3. **Attach is different from create.**
   Pointing AnonSync at an existing state root should be an explicit attach/import/rebind workflow, not accidental discovery through a launch flag.

4. **Move is different from clone.**
   A supported state-root move should produce a reviewed transition with quiesce checks, integrity verification, and post-move attestation. It should not rely on unsignaled directory copies or unsupported disk cloning rituals.

5. **Recovery posture must be visible before transition.**
   If moving or replacing a state root would strand encrypted recovery material, route history, or successor context, the operator should learn that before commit.

6. **Dangerous root transitions require proof-carrying plans.**
   Service-profile rebinding, identity-root replacement, or attach-to-existing-state should never be naked one-shot verbs.

## Object model additions

### State root

Fields:

- `state_root_id`
- `path`
- `status` (`active`, `attached`, `detached`, `maintenance`, `stale`, `superseded`)
- `opened_by_service_profile_id`
- `identity_root_ref`
- `contains_share_count`
- `contains_mount_count`
- `contains_contact_count`
- `transport_runtime_refs[]`
- `cache_policy_summary`
- `created_at`
- `last_verified_at` nullable
- `integrity_state` (`verified`, `needs-scan`, `drifted`, `partial`, `unknown`)
- `provenance_ref` nullable

### Service profile

Fields:

- `service_profile_id`
- `name`
- `mode` (`workstation`, `background-service`, `local-web`, `maintenance`, `recovery-cli`)
- `user_context`
- `listen_policy`
- `mutation_capabilities[]`
- `state_root_policy` (`must-attach-explicitly`, `may-create-empty`, `read-only-only`, `single-known-root`)
- `created_at`
- `last_used_at` nullable
- `provenance_ref` nullable

### State snapshot

A compact attestation of a state root before or after transition.

Fields:

- `state_snapshot_id`
- `state_root_ref`
- `captured_at`
- `share_count`
- `mount_count`
- `contact_count`
- `identity_fingerprint`
- `service_profile_ref`
- `integrity_summary`
- `recovery_posture_summary`
- `drift_flags[]`

### State transition plan

A reviewed mutation covering root attach/move/export/replace work.

Fields:

- `state_transition_plan_id`
- `transition_type` (`attach`, `move-root`, `switch-profile`, `replace-identity-root`, `export-state`, `import-state`)
- `source_state_root_ref` nullable
- `target_state_root_ref` nullable
- `source_service_profile_ref` nullable
- `target_service_profile_ref` nullable
- `preflight_report_ref`
- `state_transition_report_ref`
- `preservation_report_ref` nullable
- `quiesce_required`
- `rollback_strategy`
- `generated_at`
- `expires_at` nullable

## State page in the workbench

The workbench should expose a dedicated `System State` page.
Not because operators visit it every hour, but because some of the worst surprises happen there.

The page should answer:

- which state root is active
- which service profile is controlling it
- whether the root was verified recently
- what identity fingerprint and share inventory are attached
- whether backup/recovery posture is healthy enough for root transition work
- whether another known root exists locally and is detached, stale, or awaiting attach review

### Required cards

#### 1) Active state root

Shows:

- state root path and stable ID
- last verification time
- inventory counts
- identity fingerprint summary
- any drift or partial-integrity finding

#### 2) Runtime / service profile

Shows:

- current profile mode
- current user / service context
- listen posture for local control surfaces
- whether mutation is allowed from this profile
- whether this profile is allowed to create a new root or only attach an existing one

#### 3) Transition tools

Shows:

- export state
- verify state
- prepare move
- attach known root
- prepare profile switch
- replace identity root

Every mutation here should deep-link into a report or plan, not fire directly.

#### 4) Recovery posture

Shows:

- backup/export recency
- recovery bundle sufficiency where relevant
- whether transition rollback is credible
- what would be lost if the current root disappeared now

#### 5) Audit / recent transitions

Shows:

- last attach/move/export/import/switch events
- who triggered them
- whether transition completed cleanly
- where the explain trail lives

## CLI surface

Suggested commands:

```text
anonsync state show
anonsync state roots
anonsync state root show srt_01J...
anonsync state verify
anonsync state export --output ./mesh.asb
anonsync state attach --path ~/.config/anonsync/root-a --plan
anonsync state move-root --to /srv/anonsync/root --plan
anonsync state switch-profile --to background-service --plan
anonsync state replace-identity-root --from ./identity.asi --plan
anonsync plan show stp_01J...
anonsync plan apply stp_01J...
```

Expected semantics:

- `state show` prints the active root, active service profile, identity fingerprint summary, and recent verification state
- `state roots` lists known local roots without pretending that they are all active
- `state verify` produces a current attestation and integrity summary
- `state attach` never silently adopts a non-empty path; it produces a preflighted plan
- `state move-root` requires quiesce checks, post-move verification, and an explicit rollback story
- `state switch-profile` shows whether the target profile would open the same root or require explicit attach
- `replace-identity-root` is guarded as an identity/trust mutation, not presented as a cosmetic import

## API surface

A daemon API should expose at least:

```text
GET  /v1/state
GET  /v1/state/roots
GET  /v1/state/roots/{state_root_id}
POST /v1/state/roots:verify
POST /v1/state/roots:attach
POST /v1/state/roots:move
GET  /v1/service-profiles
GET  /v1/service-profiles/{service_profile_id}
POST /v1/service-profiles/{service_profile_id}:prepare-switch
POST /v1/state/export
POST /v1/state/import
```

Attach/move/import/switch operations should usually return or reference a plan object, not only a boolean success payload.

## Required transition report

State-root and service-profile work should use a dedicated `state-transition` report family.
A good report should answer:

- which root and profile are involved
- whether the target is empty, existing, attached elsewhere, or integrity-drifted
- whether the transition preserves identity continuity
- whether recovery posture remains adequate afterward
- whether rollback is credible
- what quiesce or restart boundary is required

This is important because the operator question is rarely just “did it work?”
The real question is:

> did I move the same AnonSync universe, or did I accidentally create or attach a different one?

## Event and audit expectations

At minimum, the system should emit:

- `state_root.verified`
- `state_root.attached`
- `state_root.detached`
- `state_root.move.prepared`
- `state_root.move.completed`
- `state_root.move.failed`
- `service_profile.switch.prepared`
- `service_profile.switch.completed`
- `identity_root.replaced`
- `state.exported`
- `state.imported`

Each event should link back to the relevant report and plan.

## Dangerous transitions that must stay explicit

The interface must never blur these together:

- open the same root under a different runtime profile
- attach a different existing root
- create an empty new root
- replace identity material inside the current root
- import a backup into a fresh root
- move one root's path on disk without changing identity

Those actions can feel superficially similar from the outside.
Their consequences are not similar.

## Canonical operator promises

If this document is implemented well, AnonSync should be able to make six important promises:

1. The operator can always tell which state root is active.
2. Service/background/local-web usage does not secretly change the trust model.
3. Moving durable state is a supported plan, not a support-article ritual.
4. Recovery/export posture is visible before risky transitions.
5. State-root transitions produce receipts, audit entries, and explain trails.
6. “All my shares disappeared” is treated as a product bug or blocked transition, not as normal operator archaeology.
