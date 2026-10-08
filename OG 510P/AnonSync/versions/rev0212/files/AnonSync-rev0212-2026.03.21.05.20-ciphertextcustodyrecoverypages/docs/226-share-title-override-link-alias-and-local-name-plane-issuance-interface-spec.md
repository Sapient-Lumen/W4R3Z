# Share-title override, per-artifact alias issuance, and reset-to-truth interface spec

## Purpose

The archive already had a general name-plane model.
What it still lacked was one tighter interface contract for a narrower but common case:

> one local share wants a friendlier UI title, one outgoing artifact wants a recipient-specific label, and the operator needs to know which name is real, which one propagates, and how to get back to baseline truth.

Current Resilio docs still make this seam concrete.
They still say the UI normally uses the folder name on disk, that desktop builds allow a custom share name only in UI, that the override does not rename the folder on disk, does not propagate to linked peers, and can still be inserted into a generated link or QR code.
They also still say disconnecting such a share leaves the custom name in UI until the operator uses Reset.

That is useful capability, but the semantics remain scattered.
AnonSync should expose it as one explicit title-override contract.

## Core decision

AnonSync should separate four facts whenever a user wants to "rename a share":

- **disk basename**
- **local subject title override**
- **artifact issuance label**
- **reset baseline**

The product must make it impossible to confuse:

- a local cosmetic title
- a peer-visible subject rename
- a one-off outgoing label for one artifact
- the actual on-disk path name

## Why this matters

Current Resilio behavior still leaves four operator questions too reconstructive:

- whether the current visible title is baseline or an override
- whether changing the share title changed the disk name
- whether the next outgoing artifact inherits the local override or only a temporary issuance alias
- whether disconnect/reconnect or reset returns to disk truth or preserves local decoration

AnonSync should therefore keep one stronger rule:

> every visible title must declare its plane, propagation scope, inheritance rule, and reset target.

## Fixed review order

Every local share-title change or artifact-label issuance should render the same sections in the same order:

1. **Current title planes**
2. **Requested change**
3. **Propagation and reset behavior**
4. **Admissible outcomes**
5. **Receipt promise**

### 1) Current title planes

Show:

- current disk basename
- current local title override, if any
- current subject title
- default artifact label inheritance source
- whether current view is baseline or overridden

### 2) Requested change

Classify the action as one of:

- `set local override`
- `clear local override`
- `issue artifact with one-off alias`
- `change subject title`
- `rename disk path`
- `inspect only`

### 3) Propagation and reset behavior

Show clearly:

- does it rename the folder on disk?
- do existing peers see the new title?
- do future artifacts inherit the override?
- is the change sticky across disconnect/reconnect?
- what does `Reset to truth` resolve to?

### 4) Admissible outcomes

Primary actions:

- `Apply local title override`
- `Issue one artifact with custom alias`
- `Promote local title to subject-title review`
- `Rename disk path through path review`
- `Reset visible title to baseline`
- `Keep current title planes separate`

### 5) Receipt promise

The receipt must state:

- which title planes changed
- which audiences saw the change
- whether any outgoing artifact received a one-off alias
- what `reset` will restore next time

## Main surface

Each share detail page should include a **Title planes** card:

- **Subject title**
- **Local title**
- **Disk name**
- **Next artifact label source**
- **Reset target**

Any inline rename affordance should require the user to pick one of those planes before typing.

## Object model implications

### Title override profile

Fields:

- `title_override_profile_id`
- `subject_ref`
- `disk_basename`
- `local_title_override` nullable
- `artifact_label_default_source` (`subject-title`, `local-title`, `manual-each-time`)
- `reset_target` (`disk-basename`, `subject-title`, `local-default`)
- `status`

### Artifact label issuance plan

Fields:

- `artifact_label_issuance_plan_id`
- `subject_ref`
- `carrier_family`
- `baseline_label`
- `requested_label`
- `one_off` boolean
- `future_inheritance_effect`
- `receipt_promise`

### Title-plane receipt

Fields:

- `title_plane_receipt_id`
- `subject_ref`
- `changed_planes[]`
- `unchanged_planes[]`
- `artifact_refs[]`
- `reset_target_after`
- `recorded_at`

## Explicit non-goals

AnonSync should not:

- silently rename the disk path because the user wanted a friendlier title
- quietly reuse the last recipient-specific artifact alias as a standing subject title
- hide whether the current visible name is baseline or overridden
- preserve stale decorative names after detach without showing the reset path

## Relationship to nearby specs

This spec narrows and operationalizes:

- `182-presented-name-disk-name-and-portable-artifact-alias-interface-spec.md`
- `171-cross-root-rehome-move-and-missing-path-repair-interface-spec.md`
- `118-offer-carrier-alias-equivalence-and-canonical-artifact-identity-spec.md`

Those documents explain the general name-plane and artifact-identity doctrine.
This one fixes the everyday interface contract for local overrides and per-artifact alias issuance.
