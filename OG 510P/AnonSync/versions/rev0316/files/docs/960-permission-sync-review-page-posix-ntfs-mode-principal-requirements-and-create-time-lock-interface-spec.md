# Permission sync review page — POSIX, NTFS mode, principal requirements, and create-time lock interface spec

## Purpose

This page exists for the moment when an operator is about to create or materially commit to a subject whose permission metadata policy matters.

The question is not merely `turn on permission sync?`
It is:

> which permission family is in scope, which exact mode is being promised, which runtime principal and mapping prerequisites are required, and is this a live edit or a birth-time commitment?

## Review order

Every permission-sync review should render the same sections in the same order:

1. **Current versus proposed metadata class**
2. **Permission family scope**
3. **Mode semantics**
4. **Principal requirements**
5. **Target compatibility and mapping prerequisites**
6. **Mutability class**
7. **Blast radius and safer alternatives**
8. **Receipt promise**

## 1) Current versus proposed metadata class

Show a two-column comparison:

- current byte/metadata contract
- proposed byte/metadata contract

Examples:

- `bytes-only -> apply-with-principal-conditions`
- `apply-with-principal-conditions -> rewrite-to-local-inheritance`

## 2) Permission family scope

The review must separately name:

- `POSIX permissions`
- `NTFS permissions`
- `Owner included`
- `Owner excluded`
- `Local inherited rewrite`
- `default fallback metadata`

Never compress these into one vague `permission sync enabled` row.

## 3) Mode semantics

For NTFS-like policies, the review must show which of these is intended:

- `don't sync owner`
- `sync full ACL`
- `re-apply local inherited permissions`
- `preserve only`
- `omit`

For POSIX-like policies, show:

- whether uid/gid and mode bits are expected to transfer
- whether same-name or same-ID mapping is required
- whether fallback is available or the run should block

## 4) Principal requirements

Show the actual preconditions before apply:

- runtime must be `Local System`
- runtime must be `local administrator`
- runtime must be `domain admin`
- source and target must be in the same domain
- target must resolve same user/group ID or name
- a reference source is required for pre-seeded bi-directional merges

The page must clearly mark each precondition as:

- `already proved`
- `not yet proved`
- `cannot be true on this target`
- `stale proof`

## 5) Target compatibility and mapping prerequisites

Show:

- current target filesystem / storage family
- native support for the selected metadata family
- whether non-native preservation is possible
- whether later application on a different target is expected
- current mapping confidence

Examples:

- `NTFS target · native apply available`
- `Linux target · preserve-only for incoming NTFS ACL`
- `POSIX target · mapping incomplete; safe apply blocked`

## 6) Mutability class

This section is mandatory.
The review must state whether the proposed metadata policy is:

- `live-editable`
- `next-run`
- `restart-gated`
- `birth-locked`
- `successor-required`

For creation-locked cases, the page must say so in plain language:

- `This permission mode becomes fixed when the subject/job is created.`

## 7) Blast radius and safer alternatives

Show the operational consequences of the proposed choice:

- changes to owner semantics
- cross-platform ceilings
- possible inability to fulfill the promise everywhere
- principal escalation requirements
- memory / merge / pre-seeded cost warnings when relevant

Safer alternative ladder may include:

- `Downgrade to bytes-only`
- `Preserve metadata without native apply`
- `Use local inherited rewrite`
- `Create a successor with stronger principal`
- `Block until mapping proof is fresh`

## 8) Receipt promise

The resulting receipt must prove:

- selected permission family and mode
- principal requirements accepted
- mapping prerequisites proved or left unresolved
- mutability class at time of apply
- stronger rejected sentence

## Object model

### Permission sync review

- `permission_sync_review_id`
- `subject_ref`
- `current_metadata_authority_class`
- `proposed_metadata_authority_class`
- `permission_family_set[]`
- `selected_mode`
- `principal_requirements[]`
- `mapping_requirements[]`
- `target_compatibility_summary`
- `mutability_class`
- `blast_radius_summary`
- `safer_alternative_refs[]`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`

## CLI shape

```text
anonsync metadata review create   --subject finance-share   --mode ntfs-full-acl   --include-owner yes   --require-principal domain-admin
```

## Result

AnonSync should refuse any metadata-policy change flow that still depends on remembering which mode secretly needs which principal or whether the choice freezes at creation time.
