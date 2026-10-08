# Presented name, disk name, and portable-artifact alias interface spec

## Purpose

The archive already separates subject identity from authority identity.
What it still lacked was one interface contract for a different naming problem:

> when a share has one on-disk name, another local presentation name, and yet another portable-artifact or invite label, what page stops those from collapsing back into one ambiguous `folder name` story?

Current Resilio docs make this seam unusually clear.
They still say a desktop share can get a custom UI name that does not rename the folder on disk and does not propagate to linked devices, while a different custom name can be inserted into a link during sharing even though the underlying share name remains unchanged.
Separate docs still say renaming the synced folder itself affects only the local device.
That means a useful product can still have at least four live name planes at once.

AnonSync should not hide that.

## Core decision

AnonSync should make **name planes** explicit:

- **subject title** — the stable human-facing title for the shared subject
- **local mount label** — the label used in one local work surface
- **disk name** — the path component on one specific target path
- **portable artifact label** — the title shown in an offer, invite, or exported artifact
- **peer-visible alias** — a chosen label intentionally announced to peers

A name-plane change must say which of those planes changes and which do not.

## Why this matters

Current Resilio docs still reveal four truths AnonSync should not clone:

- UI names and on-disk names can diverge
- link labels can diverge again from both
- those different labels do not all propagate to the same places
- local folder rename and shared-subject identity are still easy to conflate if the product only shows one name slot

So AnonSync needs a stricter rule:

> every name mutation must declare its plane, audience, propagation scope, and continuity effect.

## Fixed review order

Every non-trivial naming-plane action should render the same sections in the same order:

1. **Current name planes**
2. **Requested mutation and propagation scope**
3. **Continuity and ambiguity risks**
4. **Admissible outcomes and receipt promise**

### 1) Current name planes

This section should show at least:

- subject title
- local mount label for the active seat
- on-disk path basename for the active mount
- currently active peer-visible alias, if any
- currently active portable-artifact label, if any

The operator must be able to answer: **which names already exist here, and where do they live?**

### 2) Requested mutation and propagation scope

This section should show:

- which plane is being changed
- who will observe the change
- whether future artifacts inherit the new label
- whether existing peers or mounts are unaffected
- whether a path rename, subject relabel, and artifact alias edit are being proposed separately or together

The operator must be able to answer: **what name is changing, for whom?**

### 3) Continuity and ambiguity risks

This section should show:

- whether the requested change could be mistaken for authority continuity, path continuity, or a new subject
- whether two planes would become misleadingly equal or misleadingly divergent
- whether the action should escalate into path review, identity review, or artifact reissue review

The operator must be able to answer: **could this rename lie about what stayed the same?**

### 4) Admissible outcomes and receipt promise

This section should show only honest next actions, such as:

- `Retitle subject only`
- `Rename local mount label only`
- `Rename disk path here`
- `Set peer-visible alias`
- `Reissue artifact with new label`
- `Keep planes separate and explain why`

The receipt promise must state which planes changed and which remained untouched.

## Public objects

### Name plane profile

Fields:

- `name_plane_profile_id`
- `subject_ref`
- `subject_title`
- `peer_visible_alias` nullable
- `local_mount_labels[]`
- `disk_base_names[]`
- `artifact_labels[]`
- `last_mutated_at`
- `provenance_ref` nullable

### Name plane review

Fields:

- `name_plane_review_id`
- `subject_ref`
- `requested_plane` (`subject-title`, `local-mount-label`, `disk-name`, `peer-alias`, `artifact-label`, `mixed`)
- `requested_scope` (`local-seat`, `selected-mount`, `future-artifacts`, `peer-visible`, `mixed`)
- `ambiguity_findings[]`
- `admissible_actions[]`
- `generated_at`
- `expires_at` nullable

### Name plane receipt

Fields:

- `name_plane_receipt_id`
- `review_ref`
- `changed_planes[]`
- `unchanged_planes[]`
- `propagation_scope`
- `artifact_reissue_ref` nullable
- `completed_at`
- `provenance_ref` nullable

## Workbench rules

A share header should never compress all name planes into one unlabeled title.
At minimum, the detail page should show:

- **Subject**
- **Disk path here**
- **Peers see**
- **New invites show**

If all four values happen to match, the product may collapse them visually into one calm presentation.
If they diverge, the interface must not hide the divergence.

## CLI implications

A minimum public surface should include:

```text
anonsync subject names show <subject>
anonsync subject names review <subject> --plane artifact-label --value "Team Archive"
anonsync subject names apply <review_id>
anonsync subject names receipt show <receipt_id>
```
