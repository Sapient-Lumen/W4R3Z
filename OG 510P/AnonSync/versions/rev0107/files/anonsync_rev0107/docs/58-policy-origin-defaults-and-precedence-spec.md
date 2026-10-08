# Policy origin, defaults, and precedence spec

## Purpose

The archive now has many first-class policy objects: route policy, attention policy, transfer policy, filesystem policy, space policy, settlement policy, projection policy, release posture, and more.
What it still lacked was one public contract for a simpler operator question:

> why is *this* value in force *here*, which layer produced it, what would change if I altered the default, and which subjects are intentionally pinned away from inheritance?

This document answers that question.
It exists so AnonSync does not recreate a common sync-product failure mode where effective behavior is only reconstructable from preferences pages, per-share knobs, power-user keys, config-file overrides, platform-specific exceptions, or remembered “that one thing was set manually once” folklore.

## Resilio-derived motivation

Current Resilio docs still spread effective behavior across several different configuration layers:

- global Preferences carry scheduler, bandwidth, default paths, and device-level defaults
- Folder Preferences carry per-share relay/tracker/host/archive/overwrite/priority behavior
- synchronization mode can be changed per folder, while the device default connect-folder mode lives somewhere else
- power-user preferences can define defaults such as `folder_defaults.transfer_priority`, can change bandwidth semantics such as `rate_limit_local_peers`, and can even be ignored on some surfaces such as Linux WebUI for `disable_remove_from_all_devices`
- config mode can inject advanced-preference parameters again through startup config files
- at least one recent priority rule says a manually changed share stops following later global default changes even if the operator later sets it back to `None`

Those are real features.
They are not one trustworthy precedence contract.

## Core rule

Effective policy is explicit state.
A subject should never merely *have* a value.
It should have:

- an effective value
- an origin chain explaining where it came from
- a visible inheritance state saying whether it is following defaults or pinned away from them
- a previewable mutation path for changing that origin
- a receipt proving later why the value changed

If the operator cannot answer those five questions from one surface, the interface is still too implicit.

## Public objects

### Defaults profile

A named baseline bundle of policy defaults that can be attached to a scope such as a linked group, device class, or incoming-share class.
This exists so convenience presets remain explicit and inspectable instead of becoming scattered hidden defaults.

Fields:

- `defaults_profile_id`
- `name`
- `scope_kind` (`link-group`, `device-class`, `share-class`, `incoming-class`, `operator-profile`, `global`)
- `domains[]` (`route`, `transfer`, `attention`, `projection`, `space`, `activity`, `settlement`, `release`, `fs`, `access`)
- `default_values{}`
- `created_by`
- `created_at`
- `mutable` (`built-in`, `operator`, `imported`)
- `inherits_from[]`
- `notes` nullable

### Policy binding

A durable statement that one subject or scope follows one policy/default source for one domain.
This exists so inheritance can be inspected and changed without guessing whether a value is ambient, manual, imported, or stale.

Fields:

- `policy_binding_id`
- `subject_ref`
- `subject_kind`
- `domain`
- `binding_mode` (`inherit`, `pinned-policy`, `pinned-value`, `profile-derived`, `imported`, `override-derived`, `schedule-derived`)
- `source_ref` nullable
- `field_mask[]` nullable
- `applies_to_future_subjects`
- `created_at`
- `updated_at`
- `created_by`

### Effective policy explanation

A read object describing resolved policy for one subject and one domain, including per-field origin.
This exists so the operator can answer “why this value?” without leaving the main interface.

Fields:

- `effective_policy_id`
- `subject_ref`
- `domain`
- `resolved_values{}`
- `field_origins[]` where each item includes:
  - `field_path`
  - `resolved_value`
  - `origin_kind` (`built-in`, `defaults-profile`, `policy-binding`, `manual-pin`, `import`, `override-lease`, `schedule-window`, `compatibility-downgrade`)
  - `origin_ref` nullable
  - `superseded_candidates[]`
- `surface_gaps[]`
- `warnings[]`
- `computed_at`

### Policy receipt

A durable record proving that default/inheritance/precedence state changed or was explicitly reviewed.

Fields:

- `policy_receipt_id`
- `action` (`create-defaults-profile`, `bind-policy`, `pin-field`, `return-to-inheritance`, `apply-defaults-change`, `accept-surface-gap`, `record-imported-policy`)
- `subject_refs[]`
- `domain`
- `changed_fields[]`
- `before_summary`
- `after_summary`
- `applied_scope` (`future-only`, `eligible-existing`, `selected-subjects`)
- `created_at`

## Rules

1. **Per-field origin must be visible.**  
   Showing only the final value is not enough. A policy surface should say whether the value comes from built-in default, defaults profile, pinned domain policy, imported config, temporary override, or compatibility downgrade.

2. **Inheritance and explicit null are different.**  
   `inherit`, `clear`, `disable`, and `pin to none` must never collapse into one ambiguous reset action.

3. **Manual pinning must be explicit and reversible.**  
   A value should not accidentally stop following later defaults merely because it was inspected or briefly set. Returning to inheritance must be its own visible action.

4. **Defaults changes need scoped previews.**  
   Changing a defaults profile should preview whether it affects future subjects only, existing inheriting subjects, or a reviewed explicit subset.

5. **Imports/config files do not get secret precedence.**  
   Imported or startup-provided values may exist, but they must render as origin-bearing state instead of silently outranking interactive surfaces.

6. **Surface gaps must be named, not shrugged away.**  
   If one client cannot apply or honor a policy change, the effective-policy view should show a surface-gap warning instead of pretending the action worked everywhere.

7. **Override/schedule truth remains separate from durable policy.**  
   Temporary runtime change should explain current effective behavior, but should not masquerade as the new durable default.

## CLI contract

Minimal commands:

```text
anonsync defaults profile list
anonsync defaults profile show personal-strict
anonsync defaults profile apply personal-strict --to link:personal --future-only --plan
anonsync defaults profile apply travel-lite --to share-class:incoming --eligible-existing --plan
anonsync policy explain --share media
anonsync policy explain --share media --domain transfer
anonsync policy binding list --subject share:media
anonsync policy pin --share media --domain transfer --field priority --value newer-first --plan
anonsync policy inherit --share media --domain transfer --field priority --plan
anonsync policy receipt show por_01J...
```

These commands should answer:

- which defaults profile or policy binding currently governs this subject
- which fields are still inheriting versus intentionally pinned
- whether a temporary override or schedule is affecting the current effective value
- what an upcoming defaults change would actually touch
- which receipt proves that the subject returned to inheritance or was intentionally pinned away from it

## Workbench contract

The workbench should expose a `Policies` page distinct from `Releases`, `System State`, and per-share details.
Its job is not to add another settings maze.
Its job is to answer:

- what policy domains exist for this subject
- what the resolved value is for each important field
- where that value came from
- what would change if the default/profile changed
- which subjects are outliers because they are pinned or imported

The page should support:

- a per-subject effective-policy table with origin chips on every important field
- filtering by domain, origin kind, pinned-versus-inheriting, and surface-gap warnings
- a side-by-side preview of “current effective policy” versus “after proposed defaults/profile change”
- quick jumps from a share, peer, or report into the exact field origin drawer
- receipts for return-to-inheritance, mass defaults updates, and imported-policy acknowledgement

## Design tests

The model is not explicit enough if any of the following remains true:

- an operator still needs to remember whether a value came from Preferences, Folder Preferences, a power-user key, a config file, or a one-off manual tweak
- “set back to none” or “reset” still fails to say whether the subject is inheriting again or is pinned to an explicit null
- a defaults/profile change can touch large subject sets without a preview of which subjects are eligible and which are pinned out
- one surface silently ignores or cannot honor a policy while the shared model still presents the change as universally effective
- later audit cannot prove which field was pinned, which returned to inheritance, or which defaults/profile change touched existing subjects

## Outcome

A mature AnonSync surface should let the operator move from `what is this value?` to `why is this value here?` to `what else would change if I move the default?` without leaving the public model or re-learning one product-specific settings hierarchy.
That is what this document locks in.
