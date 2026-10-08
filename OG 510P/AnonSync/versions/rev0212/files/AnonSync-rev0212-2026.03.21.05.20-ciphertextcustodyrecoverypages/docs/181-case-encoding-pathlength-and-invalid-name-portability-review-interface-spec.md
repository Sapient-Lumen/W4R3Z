# Case, encoding, path-length, and invalid-name portability review interface spec

## Purpose

The archive already had filesystem portability, conflict provenance, and path-collision review.
What it still lacked was one concrete interface contract for the most operator-visible portability failure of all:

> when names, encoding, case-folding, invalid symbols, or path-length limits are the real reason a share diverges, what page tells the operator that *before* the product falls back to suffixed conflict artifacts and support ritual?

Current official Resilio docs make this seam sharper than the earlier portability pass.
They still say conflict artifacts appear when peers disagree about letter case or encoding, they still warn not to simply delete a `.Conflict` file because it corresponds to a real remote file, they still tell the operator to align letter case and remove invalid symbols/links manually, and their troubleshooting docs still point to UTF-8 expectations plus OS-specific filename/path-length ceilings.
That is candid support guidance.
It is not a good public operator contract.

## Core decision

AnonSync should treat **name portability** as a first-class reviewed surface, not as a side effect of conflict filenames.

That means:

- name portability must be checked explicitly at bind time, import time, and repair time
- collisions caused by case-folding, unicode normalization, invalid symbols, or target limits must become typed review cases
- the operator must be able to see whether the honest answer is rewrite, alias, block, quarantine, or separate-subject fork
- any rewrite or block must emit a receipt that later proves what was normalized, rejected, or kept distinct

If a user still has to infer the problem from `.Conflict` suffixes or from which peer happens to lose the race, the interface is not explicit enough.

## Why this matters

Current Resilio docs still expose five truths AnonSync should not clone:

- same-path truth can still fracture on letter-case mismatch alone
- unicode/encoding mismatch can still surface only as conflict fallout or `doesn't sync` troubleshooting
- invalid symbols and link-like entries can still be part of the same conflict/repair story
- path length ceilings still depend on target OS and appear as troubleshooting constraints rather than reviewed contract data
- conflict cleanup still depends on moving one healthy copy aside, deleting the conflict-named entries, and putting the healthy copy back

AnonSync should instead keep one public rule:

> if a pathname is not portable, the product must tell you *which portability class is violated, what rewrite or split would happen, and what evidence survives the decision*.

## Fixed review order

Every non-trivial name-portability case should render the same sections in the same order:

1. **Candidate path set and affected namespace**
2. **Portability evidence**
3. **Admissible normalization or split outcomes**
4. **Repair and receipt promise**

### 1) Candidate path set and affected namespace

This section should show:

- the original candidate names exactly as observed
- the target mount and filesystem profile
- whether the issue is local-only, cross-peer, or import-time
- whether the candidates currently map to one visible path, two distinguishable paths, or a blocked path class on this target

The operator must be able to answer: **what names are actually competing here, and where?**

### 2) Portability evidence

This section should show:

- case-fold result
- unicode normalization result
- invalid-symbol result
- path-length result
- reserved-name result where relevant
- whether the problem is merely cosmetic, namespace-colliding, or fundamentally blocked on this target

The operator must be able to answer: **what exact portability class is failing?**

### 3) Admissible normalization or split outcomes

This section should show only honest next actions, such as:

- `Preserve distinct names on a capable target`
- `Normalize into one canonical portable name`
- `Fork into separate local-only paths pending adjudication`
- `Block bind on this target`
- `Quarantine invalid entry class`
- `Open wider path repair review`

The operator must be able to answer: **what safe outcome is actually being proposed?**

### 4) Repair and receipt promise

This section should show:

- what portability receipt will be emitted
- whether the result preserves one namespace, forks it, or blocks it
- whether any loser path is copied aside, quarantined, or left untouched
- whether a later wider conflict-resolution review is still required

The operator must be able to answer: **what evidence will prove what the product did to these names?**

## Public objects

### Name portability case

Fields:

- `name_portability_case_id`
- `share_ref`
- `mount_ref`
- `candidate_names[]`
- `detected_classes[]` (`case-fold-collision`, `unicode-normalization-collision`, `invalid-symbol`, `path-too-long`, `reserved-name`, `encoding-unsupported`, `mixed`)
- `target_fs_profile_ref`
- `canonical_portable_rendering` nullable
- `severity` (`watch`, `guarded`, `high`, `blocked`)
- `suggested_outcomes[]`
- `generated_at`
- `provenance_ref` nullable

### Name portability review

Fields:

- `name_portability_review_id`
- `case_ref`
- `requested_action` (`bind`, `repair`, `import`, `rename`, `reconcile`)
- `outcome_options[]`
- `chosen_outcome` nullable
- `copy_aside_plan_ref` nullable
- `linked_conflict_ref` nullable
- `generated_at`
- `expires_at` nullable

### Name portability receipt

Fields:

- `name_portability_receipt_id`
- `review_ref`
- `applied_outcome`
- `canonical_name` nullable
- `preserved_variants[]`
- `quarantined_variants[]`
- `blocked_variants[]`
- `loser_handling`
- `completed_at`
- `provenance_ref` nullable

## Compact row contract

A truthful compact row should keep these facts in stable order:

1. subject or share
2. target mount
3. portability class
4. currently visible namespace effect
5. next honest action

Example:

```text
Design-Archive     /Volumes/NAS/Design     case-fold-collision + path-too-long     one visible path on target     Review canonicalization
```

The product should not reduce that to `Conflict file created`.

## CLI implications

A minimum public surface should include:

```text
anonsync name portability scan --share <share> --mount <mount>
anonsync name portability show <case_id>
anonsync name portability review <case_id> --plan
anonsync name portability apply <review_id>
anonsync name portability receipt show <receipt_id>
```

The CLI should let operators answer the portability question without opening hidden folders or reverse-engineering suffixes.
