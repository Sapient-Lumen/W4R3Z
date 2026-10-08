# Canonical-name portability review page: case, encoding, invalid symbol, and path budget

## Purpose

This page is the hard gate whenever a candidate name may not survive across peers or target filesystems.
It turns opaque conflict fallout into a typed portability review before commit.

## Core decision

AnonSync should not let `.Conflict`-like artifacts teach name portability after the fact.
Instead, it must review portable-name failure classes directly:

- case-fold collision
- normalization / encoding mismatch
- invalid symbol class
- reserved-name class
- path budget overflow
- mixed multi-class failure

## Fixed page order

1. **Candidate set**
2. **Failure-class evidence**
3. **Admissible outcomes**
4. **Repair and receipt commitment**

### 1) Candidate set

Show:

- exact observed names
- exact bytes or normalized rendering where useful
- affected subject / subtree
- affected target profiles
- whether the case was discovered at bind, import, rename, repair, or rescan

The operator must be able to answer: **which concrete names are in dispute?**

### 2) Failure-class evidence

For each relevant class show a small card:

- class name
- evidence sentence
- affected targets
- severity (`watch`, `guarded`, `high`, `blocked`)
- whether the class alone blocks propagation or merely narrows it

Examples of evidence sentences:

- `These two names differ only by letter case on a case-folding target.`
- `This path exceeds the reviewed budget on the selected target profile.`
- `This candidate contains a blocked trailing-symbol form on at least one target.`

The operator must be able to answer: **why is this not portable?**

### 3) Admissible outcomes

Only honest outcomes may appear:

- `Preserve distinct names on capable targets only`
- `Canonicalize to reviewed portable rendering`
- `Fork into local-only variants pending adjudication`
- `Quarantine invalid variant`
- `Block propagation to selected targets`
- `Abort mutation`

Each outcome must state:

- who observes it
- whether any variant is discarded, quarantined, or kept
- whether a later human rename is still required

### 4) Repair and receipt commitment

Show:

- receipt fields that will be emitted
- canonical portable rendering if chosen
- preserved variants
- blocked or quarantined variants
- stronger sentence that was refused, for example `propagate both names unchanged to all peers`

## Public objects

### Canonical portability review

Fields:

- `canonical_portability_review_id`
- `subject_ref`
- `candidate_names[]`
- `target_profile_refs[]`
- `failure_classes[]`
- `suggested_outcomes[]`
- `chosen_outcome` nullable
- `generated_at`
- `expires_at` nullable

### Portability failure class

Fields:

- `class`
- `evidence`
- `affected_targets[]`
- `severity`
- `blocks_global_propagation` boolean

## CLI implications

Minimum commands:

```text
anonsync names portability scan --subject <subject>
anonsync names portability review <canonical_portability_review_id>
anonsync names portability apply <canonical_portability_review_id> --outcome <outcome>
```

