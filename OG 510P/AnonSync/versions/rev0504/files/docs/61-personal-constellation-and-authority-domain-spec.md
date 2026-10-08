# Personal constellation and authority-domain spec

## Purpose

The archive already has contact records, pending peers, bounded introductions, approval grants, succession plans, role profiles, capability offers, and compatibility posture.
What it still lacked was one shared contract for a simpler but dangerous question:

> when a device is “one of mine”, what exactly becomes easier, what authority does **not** broaden automatically, what visibility does that membership grant, and how do mixed roles stay legible inside the same personal constellation?

This document answers that question.
It exists so AnonSync does not recreate a familiar sync-product mistake where “my devices” becomes a convenience label that silently widens owner power, approval reach, share visibility, and cleanup blast radius all at once.

## Resilio-derived motivation

Current Resilio docs still collapse several distinct operator questions into one linked-device convenience model:

- linked devices automatically make all Sync folders available across the linked set
- all of your own linked devices act as Owners when syncing across one identity
- a remote user can choose to automatically approve all of your linked devices for future sharing after approving one of them
- you can approve a new peer from any linked device where the folder is already active
- disconnected folders are still part of the linked-device inventory, and removing one can remove it from all linked devices
- the docs separately warn that mixed v2/v3 linked constellations can conflict on licensing and cost access to UI or share configuration

Those are all real convenience features.
They are not one trustworthy authority model.
The operator still has to reconstruct whether “linked” means:

- visible here
- writable here
- re-shareable from here
- able to approve future claims from here
- safe to treat as a replacement for another member
- safe to remove or disconnect only locally

AnonSync should not clone that shape.
A serious control surface should instead publish one personal-constellation and authority-domain model where convenience membership, local visibility, per-share role, future-approval reach, and destructive scope remain separate public facts.

## Core rule

A personal constellation is a first-class convenience boundary, not an ownership merger.
Membership may help with discovery, incoming visibility, default policies, or local review ergonomics.
It must still keep these questions explicit:

- which members belong to the constellation
- what class each member has (`personal`, `shared-admin`, `appliance`, `untrusted-storage`, `recovery-only`, `foreign-trusted`)
- what default visibility a newly offered share gains on each member
- what per-share authority each member currently has
- which approval or claim scopes may extend across members
- which destructive or disconnect actions are local, per-member, per-share, or constellation-wide
- what receipt proves membership, role, visibility, or scope changes later

If the operator cannot answer those questions from one surface, the constellation model is still too implicit.

## Public objects

### Constellation record

A first-class record describing one convenience-linked set of devices that may share defaults, visibility posture, and reviewed approval reach without pretending to be one undifferentiated owner blob.

Fields:

- `constellation_id`
- `label`
- `purpose` (`personal-mesh`, `household`, `lab`, `mixed`, `temporary-migration`)
- `members[]`
- `default_visibility_policy_ref`
- `default_member_class`
- `approval_scope_policy_ref`
- `replacement_policy_ref`
- `compatibility_posture_ref`
- `active_findings[]`
- `created_at`
- `updated_at`
- `receipt_refs[]`

### Constellation member

A first-class view of one device as it participates in the constellation.
This is not just a device card repeated in another list; it captures authority and visibility posture relative to the constellation.

Fields:

- `member_id`
- `device_ref`
- `member_class` (`personal`, `shared-admin`, `appliance`, `untrusted-storage`, `recovery-only`, `foreign-trusted`)
- `visibility_default` (`incoming-only`, `detached`, `metadata-visible`, `adopt-manually`, `auto-adopt-reviewed`)
- `default_role_profile_ref` nullable
- `can_issue_approvals`
- `approval_scope_limit` (`self-only`, `same-constellation-reviewed`, `share-bounded`, `none`)
- `can_re_share`
- `can_authorize_successor`
- `replacement_equivalence` (`none`, `same-class-reviewed`, `same-seat-reviewed`)
- `release_posture_ref`
- `drift_findings[]`
- `joined_at`
- `retired_at` nullable

### Authority domain

A first-class explanation object for “who can do what from where” on one share or subject.
This exists so the operator can tell whether convenience membership changed visibility only, or also affected mutation, re-share, approval, or succession power.

Fields:

- `authority_domain_id`
- `subject_ref`
- `member_authorities[]`
- `baseline_policy_refs[]`
- `active_override_refs[]`
- `cross_member_findings[]`
- `created_at`

Each `member_authorities[]` entry should at least name:

- `member_ref`
- `visibility_state`
- `role_profile_ref`
- `can_mutate`
- `can_re_share`
- `can_approve_claims`
- `can_replace_or_succeed`
- `effective_scope_summary`

### Constellation receipt

A durable record proving that membership, member class, visibility defaults, or approval-scope posture changed.

Fields:

- `constellation_receipt_id`
- `constellation_ref`
- `action` (`create`, `member-add`, `member-retire`, `member-class-change`, `visibility-default-change`, `approval-scope-change`, `replacement-scope-change`)
- `before_summary`
- `after_summary`
- `actor_ref`
- `created_at`

## Rules

1. **Membership is not owner merge.**  
   Joining a constellation must not silently grant owner-equivalent share power everywhere.

2. **Visibility is separate from authority.**  
   A newly visible share on a member may still be detached, metadata-only, review-gated, read-only, encrypted-only, or otherwise constrained.

3. **Approval scope must name its horizon explicitly.**  
   “Approve from any of my devices” is not acceptable as vague convenience. The product should say whether the approval is self-only, same-constellation-reviewed, share-bounded, or not allowed from that member class.

4. **One person may still operate heterogeneous devices.**  
   The same operator should be able to keep a laptop fully writable, a phone metadata-visible and read-only, a NAS appliance receive-only, and an untrusted box encrypted-only without falling out of the same reviewed constellation.

5. **Member removal and share removal stay separate.**  
   Retiring a member, hiding a disconnected incoming share, removing one local adoption, and revoking a share across the constellation must remain different actions with different receipts.

6. **Compatibility posture is part of constellation truth.**  
   Mixed release families, capability gaps, or unsupported member classes should surface on the constellation itself, not only on one member's detail page.

7. **Local-share or share-type quirks must not redefine the authority model.**  
   Whether a claim arrived locally, via portable offer, or through later share adoption should not change what `personal`, `appliance`, or `untrusted-storage` means.

## CLI contract

Minimal commands:

```text
anonsync constellation list
anonsync constellation show cst_01J...
anonsync constellation members cst_01J...
anonsync constellation member show mem_01J...
anonsync constellation authority show --share finance
anonsync constellation member class set mem_01J... --to appliance --plan
anonsync constellation visibility-default set mem_01J... --to incoming-only --plan
anonsync constellation receipt show csr_01J...
```

These commands should answer:

- which devices are actually in this personal constellation
- what class and default visibility each member has
- whether a member can mutate, re-share, approve, or only review/adopt
- whether a high-signal action is local-only, member-wide, share-wide, or constellation-wide
- which receipt proves a membership or authority-boundary change

## Workbench contract

The workbench should expose a `Constellation` page distinct from `Policies`, `Recovery`, and peer detail pages.
Its job is not to become another device list.
Its job is to answer:

- which members belong to this convenience-linked set
- what class each member has and why
- what default visibility new offers or shares gain on each member
- where approval or successor authority may travel
- which mixed-version, mixed-capability, or drift findings threaten the constellation's safety story

The page should support:

- filtering by member class, visibility default, approval reach, and compatibility posture
- opening one member drawer that compares visibility, role, and authority on important shares
- opening a share-scoped authority-domain view that contrasts members side by side
- jumping to receipts for membership, class, or scope changes
- preparing a reviewed class/scope/visibility change without leaving the workbench

## Report-language integration

The shared report language should support at least these families here:

- `constellation-authority` — what each member can currently see, mutate, re-share, or approve
- `constellation-compatibility` — why mixed member posture remains safe, guarded, or blocked
- `constellation-scope-risk` — why a removal, disconnect, or approval change reaches farther than one local member

These reports should behave like any other report-backed finding: severity, freshness, scope, and safest next action remain explicit.

## Design tests

The model is not explicit enough if any of the following remains true:

- “linked” still implies owner-like power everywhere without a visible authority-domain explanation
- the operator cannot tell whether a share is merely visible on a member versus writable or re-shareable there
- one member class cannot be tightened without pretending it left the constellation entirely
- approval reach across a constellation still depends on memory instead of one explicit scope field
- a local disconnect or cleanup action still requires guessing whether it affects one member or every member

## Outcome

A mature AnonSync surface should let the operator move from `these are my devices` to `show constellation membership and authority domains` to `tighten one member's default visibility or role` to `prove later what changed and why` without leaving the public model or re-learning share-type-specific folklore.
That is what this document locks in.
