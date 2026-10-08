# Metadata authority contract sheet page — byte truth, permission truth, and mapping class interface spec

## Purpose

This page exists so the product can answer one ordinary operator question without support archaeology:

> for this subject on this seat and target class, are bytes the only authoritative truth, or are ownership / ACL / mode bits also part of what the system is promising?

The page must not flatten permission posture into one checkbox such as `sync permissions`.
It must publish the effective metadata authority class and the proof ceiling behind it.

## Contract summary

Every metadata-authority sheet should keep the same sections in the same order:

1. **Subject and target scope**
2. **Byte truth versus metadata truth**
3. **Effective metadata authority class**
4. **Runtime principal and mapping basis**
5. **Target compatibility and apply ceiling**
6. **Blocked stronger sentence**
7. **Allowed next actions**

## 1) Subject and target scope

Show:

- subject name and stable ID
- target seat / agent / runtime
- target path or storage class
- job or subject kind
- current profile / policy source
- whether the view is current, imported from receipt, or partially inferred

## 2) Byte truth versus metadata truth

Render two adjacent rows, never one collapsed badge.

### Byte truth row

Show:

- current byte posture (`authoritative`, `replica`, `staged`, `partial`, `unknown`)
- whether byte transfer is healthy
- whether byte integrity proof is fresh

### Metadata truth row

Show:

- current metadata posture (`in-scope`, `preserve-only`, `local-rewrite`, `omitted`, `blocked`, `unknown`)
- current proof freshness
- whether the metadata sentence is stronger, weaker, or incomparable to byte truth

A file may therefore legitimately show:

- `bytes authoritative`
- `permissions preserve-only until NTFS destination`

The product may not compress that to `healthy`.

## 3) Effective metadata authority class

The sheet must publish exactly one effective class:

- `apply-and-enforce`
- `apply-with-principal-conditions`
- `preserve-for-later-application`
- `rewrite-to-local-inheritance`
- `bytes-only`
- `blocked`
- `unknown`

### Meanings

#### `apply-and-enforce`
The runtime and target can both apply the intended permission metadata now.

#### `apply-with-principal-conditions`
Application is intended, but depends on principal or identity-mapping conditions staying true.

#### `preserve-for-later-application`
Metadata is being carried forward as meaningful state, but the current target cannot fully apply it here.

#### `rewrite-to-local-inheritance`
The product intentionally drops or rewrites incoming permission details so the local target inherits from the parent environment.

#### `bytes-only`
Permission metadata is intentionally out of scope for this subject or target.

#### `blocked`
The declared metadata contract cannot be fulfilled safely enough to continue without review.

## 4) Runtime principal and mapping basis

This section must make the hidden preconditions public.
Show:

- service account / runtime principal
- elevation class (`ordinary user`, `local admin`, `Local System`, `domain admin`, `unknown`)
- domain / namespace basis when relevant
- user/group mapping class (`same IDs`, `same names`, `SID-only`, `domain-resolved`, `default ACL fallback`, `unproven`)
- whether target-side identity resolution is currently proved, assumed, stale, or failed

The operator should be able to answer:

- who is trying to apply permissions?
- under what namespace assumptions?
- why is that enough or not enough?

## 5) Target compatibility and apply ceiling

Show:

- target filesystem or storage family
- whether native permission application is supported here
- whether preservation without application is possible
- whether inheritance rewrite is configured
- the current strongest safe sentence

Examples:

- `NTFS ACL will be applied here now`
- `NTFS ACL preserved here but only applied when file later reaches NTFS storage`
- `incoming permissions rewritten to local inherited permissions`
- `permission truth omitted by policy`

## 6) Blocked stronger sentence

Every sheet must show one stronger sentence the system refuses to claim.
Examples:

- `reject saying “permissions fully matched everywhere”`
- `reject saying “owner preserved exactly”`
- `reject saying “cross-platform target can enforce source ACL natively”`

## 7) Allowed next actions

Permit only actions that match the current class:

- `Review permission sync mode`
- `Inspect principal mapping proof`
- `Downgrade to bytes-only`
- `Escalate principal requirements`
- `Open failure review`
- `Export metadata receipt`

## Object model

### Metadata authority sheet

- `metadata_authority_sheet_id`
- `subject_ref`
- `seat_ref`
- `target_ref`
- `byte_truth_class`
- `metadata_truth_class`
- `effective_metadata_authority_class`
- `runtime_principal_class`
- `mapping_class`
- `target_compatibility_class`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `proof_freshness_class`
- `source_basis_refs[]`
- `receipt_refs[]`

## CLI shape

```text
anonsync metadata show --subject finance-share --seat branch-gw-1 --target /srv/cache
```

## Non-goals

This page does not itself change policy.
It explains the current truth and routes to the correct review object.

## Result

AnonSync should make permission metadata truth just as explicit as byte truth.
If the operator still has to infer the real contract from job-profile checkboxes, service-account folklore, and late error codes, this page has failed.
