# Directory-admission lineage receipt page, requested path verdict, blocking authority, and roster authorship delta interface spec

## Purpose

Once the system has ruled on path admissibility or roster authorship, the operator needs a durable receipt that survives memory loss, team handoff, and later policy disputes.
Current official Resilio docs do not give one page that preserves the full answer.
AnonSync should.

## Core decision

Every meaningful path-admission or roster-authorship change must emit one durable **directory-admission lineage receipt**.
It must preserve:

- the requested path or import action
- the governing authority at decision time
- the exact blocking or allowing rule
- whether the outcome came from root ceiling, picker visibility, config-authorship, subject-class restriction, or storage-world mismatch
- what stronger sentence the product refused to say

## Receipt triggers

Emit this receipt when:

- a path add or create request is allowed
- a path add or create request is denied
- picker visibility and direct-entry verdicts differ
- a config-authored roster replaces an operator-authored one
- subject-class support narrows or expands

## Fixed receipt sections

1. **Request or import summary**
2. **Authority snapshot**
3. **Verdict basis**
4. **Authorship delta**
5. **Safe sentence and blocked overstatement**

### 1) Request or import summary

Show:

- requested path or import identifier
- requested action (`browse`, `direct-entry`, `add-subject`, `create-subject`, `apply-roster`)
- reviewing seat and runtime world
- timestamp

### 2) Authority snapshot

Show:

- admission authority class
- governing source locator
- root ceiling mode
- picker visibility posture
- supported subject classes

### 3) Verdict basis

Show one primary reason and any secondary reasons:

- `allowed under declared root`
- `denied by descendants-only ceiling`
- `hidden and blocked by allowlist`
- `direct entry allowed despite picker hide`
- `roster replaced by config-authored authority`
- `unsupported subject class under current mode`
- `storage-world mismatch`

### 4) Authorship delta

Show:

- prior roster authorship
- new roster authorship
- whether any prior subjects were displaced, archived, preserved, or left untouched
- where future edits must occur

### 5) Safe sentence and blocked overstatement

End with one safe sentence such as:

- `requested descendant path admitted under managed root`
- `requested root path denied by descendants-only ceiling`
- `path hidden from picker; direct entry remains allowed`
- `config-authored roster replaced prior operator-authored set`

And preserve a stronger blocked sentence such as:

- `the folder does not exist`
- `the picker is broken`
- `your subjects were unchanged`
- `you can add anything below this volume`

## Public objects

### `directory_admission_lineage_receipt`

Fields:

- `directory_admission_lineage_receipt_id`
- `seat_ref`
- `runtime_world_ref`
- `request_kind`
- `requested_path` nullable
- `requested_action`
- `admission_authority_class`
- `authority_source_locator`
- `root_ceiling_mode`
- `picker_visibility_posture`
- `supported_subject_classes`
- `primary_verdict_basis`
- `secondary_verdict_bases[]`
- `prior_roster_authorship` nullable
- `new_roster_authorship` nullable
- `subject_displacement_summary` nullable
- `future_edit_source`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `generated_at`

## Main surface

A compact row should read like one of these:

- `descendant path admitted · managed root`
- `direct-root request denied · descendants only`
- `picker-hidden path · direct entry allowed`
- `config-authored roster replaced local set`

## CLI shape

```text
anonsync subjects receipt show --latest
anonsync subjects receipt show --id sar_01J...
```

## Design tests

The receipt fails if:

- a denial does not say who blocked it
- picker-hide and admission-deny still collapse together
- roster replacement does not preserve prior and new authorship
- later operators must reopen setup docs to know what happened
