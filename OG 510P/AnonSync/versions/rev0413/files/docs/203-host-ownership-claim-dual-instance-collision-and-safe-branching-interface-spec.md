# Host ownership claim, dual-instance collision, and safe branching interface spec

## Purpose

The archive already had target-preflight, same-machine lineage, and service-root contamination language.
What it still lacked was one explicit contract for a nastier same-host failure:

> when two local runtimes or storage universes try to claim the same on-disk subject, what page proves who already owns the path, what hidden service state would be corrupted by a second claim, and what safe alternatives exist besides “try it and see”?

Current official Resilio docs make this seam sharper than a generic `folder already added` warning would.
Their current `Service files missing` guidance still says the error may appear if you run two instances of Sync on the same computer, or use an external disk drive as storage for two instances of Sync, and then add the same folder to Sync A and Sync B; in that case the internal files of the former instance get corrupted and further synchronization becomes impossible.
The change log also still records a historical issue where no warning was shown when a folder owned by another Sync instance was shared from Windows Explorer.

That is not just “be careful.”
It is a strong signal that host-level path ownership should be a first-class contract.

## Core decision

AnonSync should make **host ownership claims** first-class.

Before any new bind on a path that already contains AnonSync service state or competing sync-state evidence, the interface must declare:

- which local runtime/seat currently claims the path
- whether the claim matches this runtime, another local runtime, another storage root, or unknown foreign state
- whether the operator is attempting to reattach, branch, migrate, or illegally double-claim
- what action would preserve continuity and what action would corrupt or fork hidden state

If a second runtime can still “just add” a claimed path and discover the mistake only after state corruption, the interface is not explicit enough.

## Why this matters

Current Resilio docs still reveal eight truths AnonSync should not clone:

- the ordinary symptom can be `Service files missing`, even though the real cause may be host-level dual ownership
- hidden `.sync` state still carries ownership information strong enough to make the path unusable after collision
- external disks magnify the risk because one portable filesystem may meet multiple runtimes or storage universes over time
- historical change-log notes show that warning absence itself has been a real problem
- host-local `same machine` actions are not all equivalent: branch, mirror, reattach, migrate, and second-claim are different intents
- a path-level collision can damage local continuity without any remote peer doing anything wrong
- the operator needs ownership proof before mutation, not just after an error
- “same path on same host” deserves its own review grammar, not only the generic duplicate-subject classifier

AnonSync should therefore keep one stronger rule:

> a local path with existing sync-state evidence must be admitted through a claim classifier before any second bind, with illegal double-claim blocked by default.

## Fixed review order

Every same-host path-claim conflict should render the same sections in the same order:

1. **Claim classifier now**
2. **Ownership proof and lineage**
3. **Safe alternatives**
4. **Receipt and replay promise**

### 1) Claim classifier now

This section should show one of:

- `same-runtime reattach`
- `same-runtime existing bind`
- `same-host safe branch candidate`
- `same-host migration candidate`
- `cross-runtime ownership collision`
- `foreign/unknown sync-state residue`
- `evidence insufficient`

The operator must be able to answer: **what kind of local path conflict is this actually?**

### 2) Ownership proof and lineage

This section should show:

- discovered service-state markers
- which local runtime/seat last wrote them
- subject identity match or mismatch
- whether the path appears to be a derivative branch, a migrated bind, or a true collision
- confidence level for the classification

The operator must be able to answer: **who already owns this path, and how sure is the system?**

### 3) Safe alternatives

This section should show candidate actions such as:

- reattach the existing subject to this runtime
- open the owning runtime instead of creating a new claim
- branch locally as an explicit child subject
- migrate ownership from one runtime/seat to another with receipts
- import as foreign residue for inspection only
- bind elsewhere

Each alternative must declare:

- continuity class
- whether hidden service state is preserved, rewritten, or quarantined
- whether remote peers will perceive the action as same subject, successor, or new subject
- reversibility

The operator must be able to answer: **what can I do here without corrupting hidden state or lying about continuity?**

### 4) Receipt and replay promise

This section should show:

- chosen action
- previous and new host ownership claim
- any quarantined residue
- resulting lineage relationship
- durable custody receipt

The operator must be able to answer: **which runtime owns this path now, and what continuity story was recorded?**

## Main surface

Any attempt to add/bind a path with pre-existing AnonSync markers should route through a **Host claim review** page, not a one-line modal.
That page should show:

- path
- current claimant seat/runtime
- discovered hidden-state generation
- proposed intent
- blocked risks

Example review messages:

- `This path is already owned by seat workstation/main. Reattach instead of re-claim.`
- `This path appears to be a portable drive last owned by seat laptop/service. Migrate or inspect residue; do not branch in place.`
- `State markers exist but claimant is unknown. Open in inspection-only mode before any mutation.`

## Object model implications

AnonSync should add or strengthen these objects:

- `host_path_claim`
- `claim_conflict_case`
- `safe_branch_review`
- `claim_migration_review`
- `foreign_state_inspection_case`
- `custody_receipt`

Suggested fields for `claim_conflict_case`:

- `path`
- `existing_claimant_seat`
- `existing_claimant_runtime`
- `existing_subject_id`
- `existing_state_generation`
- `proposed_intent`
- `collision_class`
- `safe_alternatives[]`
- `quarantine_required`

## Relationship to earlier specs

This spec intentionally complements but does not duplicate earlier work:

- **same-machine derivation** covers *intentional source→child lineage* inside one model
- **target-preflight collision** classifies duplicate binds at the subject level
- **service-root contamination** prevents syncing the service root itself

This new spec focuses on:
- *host-level ownership proof*
- *cross-runtime collision on the same path*
- *safe branching versus illegal second-claim*

## Failure and edge cases

### External drive moved between hosts

If the path contains state written by another known seat, the page should classify:
`portable ownership migration candidate`
not
`fresh add`

### Unknown foreign markers

If evidence suggests other sync software or unrecognized lineage markers, the system must refuse automatic claim and offer inspection-only import.

### Same subject, different runtime, same host

This should be blocked by default unless the operator chooses an explicit migration or reattach action with continuity receipts.

### Missing markers after previous corruption

If the path looks ordinary but receipts elsewhere suggest recent ownership, the system should surface `possible scrubbed residue` and degrade confidence accordingly.

## Event language

Event stream language should use explicit phrases:

- `existing host claim discovered`
- `cross-runtime claim collision blocked`
- `path opened in inspection-only mode`
- `ownership migrated with continuity preserved`
- `local branch created as child subject`

Avoid vague lines like:
- `folder conflict`
- `cannot add folder`
- `path issue`

## The non-clone reason

This is a direct reason not to clone Resilio's surface.
Current Resilio docs still let the operator learn about same-host dual-instance ownership only after hidden `.sync` state is already damaged enough to suspend syncing.
AnonSync should instead make host ownership claims visible before mutation, with safe reattach, safe branch, migrate, and inspect-only alternatives clearly separated.
