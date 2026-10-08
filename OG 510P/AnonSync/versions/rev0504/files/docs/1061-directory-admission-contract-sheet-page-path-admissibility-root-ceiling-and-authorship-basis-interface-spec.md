# Directory admission contract sheet page, path admissibility, root ceiling, and authorship basis interface spec

## Purpose

The archive already had storage-world, invocation-profile, and control-substrate pages.
What it still lacked was one explicit contract for the narrower workstation question:

> can this seat nominate or create this path as a sync subject at all, and whose authority currently governs that answer?

Current official Resilio docs make the missing contract unusually obvious.
They still expose config-driven path admission fields, path-visibility controls, and a config-authored folder set that can replace WebUI authorship.
That is not just setup trivia.
It is subject-admission truth.

AnonSync should therefore render one first-class **directory admission contract sheet** before the operator is allowed to assume that a browseable path is admissible.

## Core decision

Every seat capable of adding or creating sync subjects must expose one explicit **directory admission contract**.
It must say:

- who currently governs admissible paths
- what root ceiling applies
- what browse surfaces are filtered
- whether the current subject roster is operator-authored or config-authored
- what stronger sentence the product must refuse

The product must never let `choose folder`, `browse`, or `add directory` stand in for this truth.

## Fixed review order

Every directory admission contract sheet should render the same sections in the same order:

1. **Admission authority**
2. **Root ceiling**
3. **Visibility authority**
4. **Subject authorship**
5. **Strongest safe sentence**

### 1) Admission authority

This section should show:

- authority class (`operator-local`, `policy-managed`, `config-authored`, `imported`, `unknown`)
- governing source locator
- who last changed the admission rules
- whether the current reviewing user can change them from this surface

The operator must be able to answer: **who decides whether a path is admissible?**

### 2) Root ceiling

This section should show:

- nominated root path
- ceiling mode (`unbounded`, `root-and-below`, `below-root-only`, `subject-class-limited`, `unknown`)
- whether direct creation at the root is allowed
- whether only descendants are allowed

The operator must be able to answer: **where may I add or create subjects, and where may I not?**

### 3) Visibility authority

This section should show:

- picker visibility mode (`full`, `allowlist`, `denylist`, `config-only`, `headless-only`, `unknown`)
- whether hidden paths may still be admissible by direct entry
- whether visible paths can still be denied later by a stronger rule
- which locations are intentionally hidden from browse surfaces

The operator must be able to answer: **what is the picker allowed to reveal, and does that equal what is admissible?**

### 4) Subject authorship

This section should show:

- roster authorship (`operator-authored`, `config-authored`, `policy-authored`, `mixed`, `unknown`)
- whether a config import replaced earlier operator-authored subjects
- whether Web or local UI mutation is enabled, suppressed, or read-only
- supported subject classes (`standard-only`, `advanced-enabled`, `unknown`)

The operator must be able to answer: **who authored the current subject set, and can I change it here?**

### 5) Strongest safe sentence

The page must end with one sentence such as:

- `operator may nominate any descendant below the managed root`
- `paths are addable only below the declared root; direct root creation denied`
- `picker shows an allowlisted subset; hidden paths are not currently nominatable`
- `subject roster is config-authored; UI mutation suppressed`
- `admission authority unclear; path claim not yet safe`

And it must also show the stronger blocked sentence it refuses, such as:

- `you can add any folder on this machine`
- `anything visible in the picker is safe to add`
- `the current roster is still operator-owned`

## Public objects

### `directory_admission_contract`

Fields:

- `directory_admission_contract_id`
- `seat_ref`
- `authority_class`
- `authority_source_locator`
- `authority_last_changed_at` nullable
- `root_path` nullable
- `root_ceiling_mode`
- `visibility_mode`
- `hidden_locations_summary`
- `hidden_paths_direct_entry_policy`
- `roster_authorship`
- `ui_mutation_posture`
- `supported_subject_classes`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `generated_at`

## Main surface

A compact row should read like one of these, not just `Add folder enabled`:

- `operator-authored admission · unrestricted descendants`
- `managed root · below-root only`
- `allowlisted picker · hidden paths blocked`
- `config-authored roster · UI mutation suppressed`
- `admission authority ambiguous · safe claim withheld`

## Event language

Use phrases such as:

- `directory admission policy changed`
- `root ceiling narrowed to descendants only`
- `picker visibility now allowlisted`
- `config-authored roster replaced prior operator set`

Avoid phrases such as:

- `folder picker updated`
- `browse fixed`
- `you can add folders again`

Those lines are too weak and too flattening.

## CLI shape

```text
anonsync subjects admission show --seat self
anonsync subjects admission explain --seat self
anonsync subjects authorship show --seat self
```

## Design tests

The model is not explicit enough if any of these remain true:

- the operator can see a picker without seeing the authority that filtered it
- root-ceiling denial and picker-hiding still read as the same thing
- config-authored subject replacement can happen without the contract sheet surfacing it
- the product can still say `add folder` without owning subject class and authorship basis

## Non-clone reason

Current official Resilio docs still make directory admission truth feel like config-file trivia rather than one ordinary product contract.
AnonSync should instead render admission authority, root ceiling, visibility, and authorship as a stable reviewed object.
