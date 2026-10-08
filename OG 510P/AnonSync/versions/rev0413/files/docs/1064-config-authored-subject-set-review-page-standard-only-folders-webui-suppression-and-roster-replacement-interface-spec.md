# Config-authored subject-set review page, standard-only folders, WebUI suppression, and roster replacement interface spec

## Purpose

The admission contract sheet says who governs subject addition.
The next question is more structural:

> did a config-authored subject roster just replace an operator-authored one, and what edit surfaces and subject classes remain after that switch?

Current official Resilio docs make this seam explicit enough to borrow and still too diffuse to clone.
They still say that in config mode only Standard folders may be set up, and that if shared folders are defined in the config file, WebUI is disabled and those shared directories override folders previously added from WebUI.

AnonSync should therefore review **config-authored roster replacement** as one world-class mutation rather than a startup footnote.

## Core decision

Config-authored subject import is not a passive preload.
It can change all three of these at once:

- the current subject roster
- the mutation surface allowed afterward
- the subject classes available

The product must review those together.

## Review triggers

Open this page when:

- a config or bootstrap bundle contains an explicit subject roster
- a managed-seat import would replace or lock existing subjects
- the product suppresses browser/UI mutation because config authorship now governs
- subject-class availability narrows from mixed or advanced-capable to standard-only

## Fixed review order

1. **Incoming authored roster**
2. **Replaced local roster**
3. **Mutation surface after apply**
4. **Subject-class consequences**
5. **Commit sentence**

### 1) Incoming authored roster

Show:

- source of the roster
- number of subjects to be installed
- whether paths are absolute, templated, or unresolved
- whether the roster is advisory or authoritative

### 2) Replaced local roster

Show:

- current locally authored subjects at risk of displacement
- whether they will be removed from active control, hidden, archived as lineage, or preserved as inert residue
- whether the resulting runtime should be understood as `same roster adopted` or `roster replaced`

### 3) Mutation surface after apply

Show:

- whether Web, local GUI, and CLI subject mutation remain enabled
- which surface becomes read-only or suppressed
- where future edits must occur (policy bundle, config source, local override lane, none)

### 4) Subject-class consequences

Show:

- supported classes after apply (`standard-only`, `advanced-enabled`, `mixed`, `unknown`)
- which existing subjects become unsupported or need successor conversion
- whether apply narrows capabilities silently or with explicit migration

### 5) Commit sentence

End with one safe sentence such as:

- `config-authored standard roster will replace current operator-authored roster`
- `config-authored roster adopted; local mutation surface becomes read-only`
- `incoming roster is advisory only; local roster remains authoritative`
- `roster consequences unresolved; import withheld`

And show the blocked stronger sentence it refuses, such as:

- `this only adds a few defaults`
- `your current folders stay editable as before`
- `all folder types remain supported`

## Public objects

### `config_authored_subject_set_review`

Fields:

- `config_authored_subject_set_review_id`
- `seat_ref`
- `incoming_roster_source`
- `incoming_roster_subject_count`
- `incoming_roster_authority_class`
- `replaced_subjects_summary`
- `post_apply_mutation_surface`
- `post_apply_edit_source`
- `post_apply_subject_classes`
- `continuity_class`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `generated_at`

## Main surface

A compact row should read like one of these:

- `config-authored roster · replaces local set`
- `config-authored roster · local UI mutation suppressed`
- `standard-only roster · subject class narrowed`
- `advisory import only · local roster remains authoritative`

## CLI shape

```text
anonsync subjects import review --source managed-config
anonsync subjects authorship diff --seat self --incoming managed-config
```

## Design tests

The page fails if:

- roster replacement can happen without naming the displaced set
- WebUI or local mutation suppression is learned only after apply
- subject-class narrowing is treated as a footnote
- a config-authored roster still reads like an ordinary `startup preference`
