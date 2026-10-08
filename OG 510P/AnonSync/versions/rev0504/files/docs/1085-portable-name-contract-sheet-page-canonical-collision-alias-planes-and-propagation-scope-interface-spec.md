# Portable-name contract sheet page: canonical collision, alias planes, and propagation scope

## Purpose

AnonSync already has lower-level portability and naming materials.
What it still lacked was one first page that turns `name` into a reviewed contract instead of an overloaded word.

This page exists to answer one ordinary question before any rename, bind, import, or repair action:

> what names exist here, what portable canonical form is admissible, what alias planes diverge, and what propagation scope is actually being requested?

## Core decision

The product must stop using one undifferentiated `Name` field for six different truths.
The contract sheet must always separate:

- **canonical portable name**
- **local disk basename**
- **local presented title**
- **portable artifact label**
- **peer-visible propagated alias**
- **alias-edge adjacency warning** when link-like entries could confuse target meaning

## Fixed page order

1. **Current name planes**
2. **Canonical portability verdict**
3. **Requested propagation scope**
4. **Target portability and alias-edge warnings**
5. **Available next actions**

### 1) Current name planes

Show one stable table with rows for:

- canonical portable name
- local disk basename
- local presented title
- portable artifact label
- peer-visible alias
- current root path / mount

Each row must show:

- current value
- observer audience
- propagation behavior
- continuity effect if changed

The operator must be able to answer: **which names already exist here, and who sees each one?**

### 2) Canonical portability verdict

Show:

- canonicalization status (`already-portable`, `portable-with-rewrite`, `collision-risk`, `blocked`)
- detected issues (`case-fold`, `encoding`, `invalid-symbol`, `path-budget`, `reserved-name`, `mixed`)
- loser/collision paths if any
- whether the verdict is global, target-specific, or pair-specific

The operator must be able to answer: **what portable name can actually survive?**

### 3) Requested propagation scope

Show a scope strip with exactly one selected class:

- `local title only`
- `local disk basename only`
- `artifact label only`
- `peer-visible alias`
- `canonical portable rename`
- `cross-root rehome review required`

The operator must be able to answer: **what is changing, and who will observe it?**

### 4) Target portability and alias-edge warnings

Show:

- per-target filesystem portability warnings
- whether alias edges exist in the renamed subtree
- whether any symlink/junction/hardlink semantics narrow the meaning of the proposed rename or move
- whether the action is safe only for the edge object, not the target tree

The operator must be able to answer: **is the target carrying the same meaning I think it is?**

### 5) Available next actions

Only honest actions may appear:

- `Apply local title change`
- `Apply artifact label change`
- `Review canonical rewrite`
- `Review blocked collision`
- `Open cross-root rehome`
- `Open alias-edge boundary review`
- `Emit receipt only / no mutation`

## Public objects

### Portable name contract sheet

Fields:

- `portable_name_contract_sheet_id`
- `subject_ref`
- `mount_ref` nullable
- `canonical_portable_name`
- `local_disk_basename`
- `local_presented_title` nullable
- `portable_artifact_label` nullable
- `peer_visible_alias` nullable
- `portability_verdict`
- `detected_portability_classes[]`
- `requested_scope_class`
- `alias_edge_warning_count`
- `generated_at`

### Name plane row

Fields:

- `plane` (`canonical`, `disk`, `presented`, `artifact`, `peer-visible`)
- `value`
- `audience`
- `propagates` boolean
- `continuity_effect`

## Compact summary strip

A truthful summary strip should read like:

```text
Canonical portable name is "Finance Reports". You are changing only the local presented title. Disk basename and peer-visible name will stay unchanged.
```

or:

```text
Requested canonical rename collides on case-folded target paths. Portable rewrite or block review is required before propagation.
```

## CLI implications

Minimum commands:

```text
anonsync names contract show --subject <subject>
anonsync names contract review --subject <subject> --scope <scope>
anonsync names planes list --subject <subject>
```

