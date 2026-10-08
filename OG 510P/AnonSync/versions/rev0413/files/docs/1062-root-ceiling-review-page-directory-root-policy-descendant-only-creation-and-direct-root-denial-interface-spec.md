# Root-ceiling review page, directory-root policy, descendant-only creation, and direct-root denial interface spec

## Purpose

The directory admission contract sheet says who governs path admission.
The next question is narrower and more operational:

> if this seat is constrained to a declared root, does the rule permit creating or adding directly at that root, or only beneath it?

Current official Resilio docs make that distinction explicit enough to borrow and still too implicit in workflow form.
They still say `directory_root_policy` can be `all` or `belowroot`, and that `belowroot` denies attempts to use `adddir` directly within `directory_root` while still allowing subdirectories.

AnonSync should therefore make **root ceiling** a separate review object rather than burying it inside help text.

## Core decision

A product must distinguish at least four states:

- no declared root ceiling
- root itself and descendants allowed
- descendants allowed but root creation denied
- root authority present but current claim unproven

It must never flatten these into `path allowed`.

## Review triggers

Open this page when:

- a managed seat first declares a subject root
- the root ceiling changes
- the operator tries to create directly at the root
- an import or policy bundle converts free selection into descendant-only selection
- an existing path falls outside the newly declared ceiling

## Fixed review order

1. **Declared root**
2. **Creation mode**
3. **Examples and counterexamples**
4. **Migration and fallback**
5. **Commit sentence**

### 1) Declared root

Show:

- declared root path
- source of the root declaration
- whether the root itself is already a subject or merely a ceiling anchor
- whether the path exists and is reachable from this seat

### 2) Creation mode

Show one explicit verdict:

- `root-and-descendants allowed`
- `descendants only`
- `existing-subjects only`
- `ceiling uncertain`

Also show the concrete behavioral rule:

- add existing root path allowed or denied
- create new subject directly inside root allowed or denied
- add/create below root allowed or denied

### 3) Examples and counterexamples

The page must render concrete paths, not abstract policy prose.
For example:

- `/srv/projects` → denied as direct-root subject creation
- `/srv/projects/team-a` → allowed as descendant subject
- `/srv/archive` → denied because outside declared root

The operator must be able to answer: **what would actually pass right now?**

### 4) Migration and fallback

Show:

- what existing subjects would survive the new ceiling
- what current subjects become out-of-policy but tolerated temporarily, if any
- what safer next step exists when the requested root-level action is denied
- whether direct manual entry can help, or whether the policy itself must change

### 5) Commit sentence

End with one safe sentence such as:

- `subjects may be created at the root and below it`
- `subjects may be created only below the declared root`
- `requested root-level subject denied; choose or create a descendant`
- `root rule unresolved; add/create withheld`

And the blocked stronger sentence it refuses, such as:

- `everything under this drive is fair game`
- `the requested path is invalid`
- `the picker is broken`

## Public objects

### `root_ceiling_review`

Fields:

- `root_ceiling_review_id`
- `seat_ref`
- `declared_root`
- `declared_root_source`
- `creation_mode`
- `requested_path` nullable
- `requested_action` nullable
- `requested_path_verdict` nullable
- `example_allowed_paths[]`
- `example_denied_paths[]`
- `migration_summary`
- `safe_next_step`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `generated_at`

## Main surface

A compact row should read like one of these:

- `declared root · root and descendants allowed`
- `declared root · descendants only`
- `requested path denied · choose descendant`
- `root ceiling uncertain · no safe add/create claim`

## CLI shape

```text
anonsync subjects root-ceiling review --seat self
anonsync subjects root-ceiling test --seat self --path /srv/projects
```

## Design tests

The page fails if:

- descendants-only and full-root admission still share one badge
- the operator must mentally simulate examples to know what passes
- a denied root-level create can still be misread as `no access anywhere below`
- migration consequences of a ceiling change remain hidden
