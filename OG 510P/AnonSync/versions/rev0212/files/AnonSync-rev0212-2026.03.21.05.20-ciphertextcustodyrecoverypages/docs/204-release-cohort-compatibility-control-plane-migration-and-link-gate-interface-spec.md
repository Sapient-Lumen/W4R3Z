# Release cohort compatibility, control-plane migration, and link gate interface spec

## Purpose

The archive already had release-posture, capability uplift, and successor-continuity language.
What it still lacked was one explicit contract for a dangerous convenience seam:

> when two devices or runtimes are about to be linked across release cohorts or control-plane generations, what page proves whether the convenience operation is really compatible, what settings or shares might be displaced, and whether the system is doing a safe join, a control-plane takeover, or a migration?

Current official Resilio docs make this seam sharper than a generic `Link device` wizard would.
Their current linking docs still say it is highly advisable **not** to link devices where Sync v2 and v3 are installed, because they may conflict on the applied license and lead to lost access to Sync UI and shares configuration even though files on storage are not affected.
The same linking docs also still say that if you attempt to link two devices which are already running Sync and therefore have different certificates, one device will lose its certificate, take over the other certificate, and have its Advanced folders removed from the app while new folders from the other instance are copied; on iOS those Advanced folders are removed from Sync and deleted from the filesystem.

That is not an ordinary convenience join.
It is a control-plane migration with cohort risk.

## Core decision

AnonSync should make **cohort compatibility** and **control-plane takeover risk** first-class.

Before any operation that merges two already-configured control planes, the interface must declare:

- whether the peers are in the same release cohort, schema epoch, and capability family
- whether the action is a safe join, a reviewed migration, or an unsafe merge
- what control-plane objects may be replaced, hidden, or retired
- what data-plane bytes remain untouched even if the control plane changes
- what preflight steps would make the migration safe

If an operator can still mistake a control-plane takeover for a simple `link my devices` action, the interface is not explicit enough.

## Why this matters

Current Resilio docs still reveal nine truths AnonSync should not clone:

- cross-version linking is still warned against in documentation rather than blocked or reviewed as a first-class compatibility case
- a link can carry license state, certificate identity, and configured shares together
- two already-configured devices are not merely “joined”; one can take over the other's certificate
- data-plane bytes surviving on disk does not make control-plane loss benign
- UI/share-config loss is still a real outcome even when content bytes survive
- on iOS the blast radius can be harsher because app removal also deletes Advanced folders from the filesystem
- cohort compatibility is therefore not only a transport question but a control-plane migration question
- convenience workflows can still conceal succession or replacement semantics
- operators deserve a stable review grammar for joins across version/channel/schema differences

AnonSync should therefore keep one stronger rule:

> any join across differing control-plane cohorts must be admitted through a compatibility gate that classifies the action as safe join, reviewed migration, or blocked unsafe merge.

## Fixed review order

Every non-trivial cohort join should render the same sections in the same order:

1. **Compatibility matrix now**
2. **Control-plane impact**
3. **Migration or join plan**
4. **Receipt and replay promise**

### 1) Compatibility matrix now

This section should show:

- release channel and version family
- schema epoch
- capability family / edition features
- local and remote control-plane population
- compatibility class:
  - `same cohort safe join`
  - `same schema reviewed takeover risk`
  - `different cohort migration required`
  - `unsafe merge blocked`

The operator must be able to answer: **are these two runtimes actually safe to join as-is?**

### 2) Control-plane impact

This section should show:

- certificate/identity continuity effect
- share registry effect
- approval/trust effect
- policy/defaults effect
- license/capability effect
- whether data-plane bytes remain untouched, reindexed, hidden, or at risk

The operator must be able to answer: **what control-plane world changes if I proceed, even if the files stay on disk?**

### 3) Migration or join plan

This section should show ordered options such as:

- join as a fresh empty seat to an existing control plane
- migrate the older cohort first, then join
- export/attest local receipts before takeover
- preserve both worlds and use explicit successor import
- block and require manual upgrade before any join

Each option must declare:

- continuity class
- share-registry result
- path-bind result
- whether any local subjects will be retired from the app view
- reversibility

The operator must be able to answer: **what is the safest path to the desired end state without accidentally replacing one control plane with another?**

### 4) Receipt and replay promise

This section should show:

- chosen compatibility action
- resulting cohort state
- control-plane lineage result (`joined`, `succeeded`, `replaced`, `blocked`)
- preserved/exported receipts
- any remaining upgrade or reapproval steps

The operator must be able to answer: **what kind of join or migration actually happened, and what world survived it?**

## Main surface

Any link/import/join flow involving a non-empty local control plane should route through a **Compatibility gate** page.
That page must not pretend the question is only `Do you trust this device?`
It must also answer:

- `Are these cohorts compatible?`
- `Is this a join or a takeover?`
- `What happens to the local share registry?`
- `What survives only on disk, outside the control plane?`

Example messages:

- `Both seats are already configured. This is not a simple link; it is a control-plane migration candidate.`
- `Remote cohort is newer and incompatible with your current schema epoch. Upgrade or preserve both worlds and import later.`
- `Files on disk are expected to survive, but local app-visible subjects would be retired from this seat.`

## Object model implications

AnonSync should add or strengthen these objects:

- `cohort_compatibility_report`
- `control_plane_join_review`
- `control_plane_migration_review`
- `takeover_risk_case`
- `join_receipt`
- `control_plane_successor_record`

Suggested fields for `cohort_compatibility_report`:

- `local_release_family`
- `remote_release_family`
- `local_schema_epoch`
- `remote_schema_epoch`
- `local_subject_count`
- `remote_subject_count`
- `capability_deltas[]`
- `compatibility_class`
- `blocked_reasons[]`
- `recommended_paths[]`

## Relationship to other archive decisions

This spec intentionally complements:

- **release posture**: what build/channel/schema a runtime belongs to
- **successor continuity**: how one control plane may intentionally replace another
- **identity replacement**: why convenience should not silently carry takeover semantics

The new contribution here is the explicit **preflight gate** for convenience joins across non-empty control planes and mixed cohorts.

## Failure and edge cases

### Two empty seats, same cohort

This can be a simple safe join.
The page should say so clearly and avoid overdramatizing.

### One empty seat, one populated seat

This is still not equivalent to two populated seats.
The review should emphasize low local blast radius on the empty side.

### Mixed cohort but files on disk survive

The interface must still flag that control-plane loss is meaningful even when data-plane bytes are safe.

### Mobile/storage-constrained seats

If the platform has harsher filesystem consequences on replacement or retirement, the compatibility gate must say so before apply.

## Event language

Event stream language should use explicit phrases:

- `cohort compatibility review required`
- `control-plane takeover blocked`
- `safe join admitted`
- `reviewed migration preserved receipts before successor import`
- `data-plane intact; control-plane replaced`

Avoid vague lines like:
- `linked successfully`
- `join completed`
- `settings migrated`

## The non-clone reason

This is a strong reason not to clone Resilio's convenience language.
Current Resilio docs still treat some joins that can displace certificate identity, UI/share configuration, and even mobile filesystem presence as part of the normal linking story, with the warning living mostly in documentation.
AnonSync should instead expose one compatibility gate that distinguishes safe join from reviewed migration from blocked unsafe merge before any control-plane world is replaced.
