# Picker visibility authority page, allowlisted browse surfaces, hidden paths, and direct-entry boundary interface spec

## Purpose

The archive already had browser-control, headless audience, and control-surface exposure pages.
What it still lacked was one explicit contract for this narrower UX truth:

> what paths is the picker allowed to reveal, and does hidden-from-picker mean inadmissible, merely undiscoverable, or governed by a stronger rule elsewhere?

Current official Resilio docs make the missing distinction unusually obvious.
They still say `dir_whitelist` defines which directories may be used to store sync shares and that others will not be visible in the folder picker.
That is not mere browse polish.
It is visibility authority.

AnonSync should therefore render one first-class **picker visibility authority page** whenever browse surfaces are filtered.

## Core decision

A browse surface must distinguish:

- visible and admissible
- hidden but admissible by direct entry
- hidden and inadmissible
- visible but later-denied by stronger policy
- browse unavailable because config/headless authority owns the roster

The product must never let `not shown` stand in for the whole truth.

## Review triggers

Open this page when:

- picker results are filtered by allowlist or policy
- a direct path entry disagrees with picker visibility
- a seat becomes config-authored or headless-only
- the picker hides entire roots or volumes
- a user reports `folder missing` inside the add flow

## Fixed review order

1. **Picker authority source**
2. **Visibility classes**
3. **Direct-entry boundary**
4. **Examples**
5. **Strongest safe sentence**

### 1) Picker authority source

Show:

- who filtered the picker
- source locator
- whether the filter is local preference, managed policy, config import, or headless-only posture
- whether the filter is mutable here

### 2) Visibility classes

The page must bucket locations into classes such as:

- `visible and admissible`
- `visible but subject to stronger admission test`
- `hidden but direct-entry allowed`
- `hidden and blocked`
- `not shown because picker disabled`

### 3) Direct-entry boundary

Show:

- whether manual path entry is available
- whether direct entry can nominate hidden paths
- whether direct entry is checked against the same root ceiling or a stricter rule
- what denial reason appears if direct entry fails

### 4) Examples

Render concrete examples like:

- `/work/team-a` → visible and admissible
- `/work/team-secret` → hidden and blocked by allowlist
- `/archive/import-drop` → hidden in picker, direct entry allowed
- `/mnt/external` → visible but later denied by root ceiling

### 5) Strongest safe sentence

End with one safe sentence such as:

- `picker is intentionally allowlisted; hidden locations are not all invalid`
- `picker shows only admissible roots; direct entry cannot widen scope`
- `browse is suppressed because the roster is config-authored`
- `visibility authority unclear; path claim withheld`

And show the blocked stronger sentence it refuses, such as:

- `the missing folder does not exist`
- `everything visible is addable`
- `manual entry bypasses policy`

## Public objects

### `picker_visibility_authority`

Fields:

- `picker_visibility_authority_id`
- `seat_ref`
- `authority_class`
- `authority_source_locator`
- `picker_posture`
- `direct_entry_posture`
- `visibility_buckets[]`
- `example_paths[]`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `generated_at`

## Main surface

A compact row should read like one of these:

- `allowlisted picker · hidden paths remain policy-shaped`
- `picker suppressed · config-authored roster`
- `visible set narrower than admissible set`
- `picker visibility ambiguous · browse claims withheld`

## CLI shape

```text
anonsync subjects picker show --seat self
anonsync subjects picker explain --seat self --path /archive/import-drop
```

## Design tests

The page fails if:

- the operator cannot tell whether a missing path is hidden versus inadmissible
- direct entry and picker visibility silently diverge
- a headless/config-only posture still looks like a broken picker
- hidden-path examples are missing
