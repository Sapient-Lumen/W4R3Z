# Advanced override inventory page — source, precedence, and restart boundary interface spec

## Purpose

The archive already had route, cadence, and subject-state pages.
What it still lacked was one ordinary page for the simpler question:

> which hidden advanced or config-mode overrides are currently shaping this seat or subject, where did they come from, and which visible controls do they outrank?

Current official Resilio docs make this seam concrete.
They still keep active operator truth spread across Power user preferences, config mode, folder preferences, and special-case articles.
That is useful truth.
It should not remain hidden-source archaeology.

## Core decision

AnonSync must expose one first-class **Advanced override inventory** page whenever advanced settings, config files, or non-default low-level policy materially change safety, discovery, retention, resource use, or surface capability.

The page exists to answer five things in one place:

1. which hidden overrides are currently active
2. where each override came from
3. which one wins when sources disagree
4. which visible controls are shadowed or ignored
5. which changes require restart, reindex, or cache clearance

## Fixed page order

1. **Current override verdict**
2. **Source register**
3. **Effective precedence**
4. **Shadowed or ignored visible controls**
5. **Apply / restart / clearance boundary**

### 1) Current override verdict

Show:

- `advanced_override_inventory_page_id`
- seat and optional subject in scope
- current `override_verdict` (`none-active`, `active-visible`, `active-hidden`, `config-declared`, `mixed-source`, `surface-divergent`, `unknown`)
- strongest honest summary
- last evaluated time

The operator must be able to answer:

> are hidden overrides shaping this context right now?

### 2) Source register

List each active or materially relevant override with:

- override name
- current effective value
- source kind (`interactive-preference`, `folder-preference`, `advanced-preference`, `config-declared`, `runtime-default`, `imported-policy`)
- scope (`seat`, `subject-default`, `subject-specific`, `surface-only`)
- whether it is operator-editable here

The page must keep provenance visible beside value.
A raw key/value table is not enough.

### 3) Effective precedence

For every override whose value may compete across sources, show:

- higher-precedence source
- lower-precedence sources now shadowed
- whether the current source disables interactive editing
- whether the override is sticky across restart or only current-session visible

This section must answer:

> which source is actually in charge right now?

### 4) Shadowed or ignored visible controls

Show the controls, menus, and status badges whose ordinary meaning is narrowed by the active overrides.
Each row must say whether the visible surface is:

- fully honored
- honored but incomplete
- shadowed by hidden policy
- ignored on this surface
- disabled because control has moved to another source

### 5) Apply / restart / clearance boundary

For each override, show the least-misleading apply semantics:

- immediate
- after restart
- after rescan / reindex
- after peer-memory expiry or explicit clearance
- after moving to another surface

Actions may include:

- `Open override editor`
- `Open safety override`
- `Open peer memory override`
- `Open runtime bias override`
- `Export override receipt`
- `Accept current precedence`

## Public object

### Advanced override inventory page

Fields:

- `advanced_override_inventory_page_id`
- `seat_ref`
- `subject_ref` nullable
- `override_verdict`
- `override_rows[]`
- `source_precedence_rows[]`
- `shadowed_control_rows[]`
- `apply_boundary_rows[]`
- `safe_next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. override name
2. effective value
3. winning source
4. strongest shadowed control or side effect
5. apply boundary

Example:

```text
peer_memory_retention     7 days     advanced-preference     LAN-only claim still shaped by cached public endpoint     restart + explicit clearance
```

## Non-goals

This page does **not** replace full route repair, resource tuning, or release-line support review.
It proves only **which hidden overrides are active, where they came from, what they outrank, and how they take effect**.
