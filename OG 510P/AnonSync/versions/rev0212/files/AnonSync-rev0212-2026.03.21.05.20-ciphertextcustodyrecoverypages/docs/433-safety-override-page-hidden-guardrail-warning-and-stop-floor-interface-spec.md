# Safety override page — hidden guardrail, warning, and stop floor interface spec

## Purpose

The archive already had destructive review pages and delete-scope pages.
What it still lacked was one ordinary page for the simpler question:

> which hidden advanced settings are currently hardening or weakening destructive guardrails, warnings, and stop thresholds for this seat or subject?

Current official Resilio docs make this seam concrete.
They still put destructive-action suppression, placeholder-delete protection, low-space stop thresholds, warning suppression, and related guardrails in low-level settings rather than one ordinary page.
That is useful truth.
It should not remain a power-user scavenger hunt.

## Core decision

AnonSync must expose one first-class **Safety override** page whenever hidden settings can materially change delete propagation, destructive availability, warning presence, or low-space stop behavior.

The page exists to answer five things in one place:

1. what current safety posture is active
2. which guardrails are hardened, weakened, or suppressed
3. which surfaces honor or ignore those guardrails
4. what thresholds will stop or permit work
5. which next action is safest

## Fixed page order

1. **Current safety posture**
2. **Guardrail matrix**
3. **Surface honor / ignore rows**
4. **Threshold floors and stop behavior**
5. **Safe next actions**

### 1) Current safety posture

Show:

- `safety_override_page_id`
- seat and optional subject in scope
- current `safety_posture_verdict` (`hardened`, `default`, `warning-suppressed`, `delete-guard-strengthened`, `delete-guard-weakened`, `low-space-stop-tightened`, `low-space-stop-relaxed`, `unknown`)
- strongest honest summary
- last evaluated time

The operator must be able to answer:

> is hidden policy currently making destructive behavior safer, riskier, or merely quieter?

### 2) Guardrail matrix

At minimum render rows for:

- global-delete availability
- placeholder-delete handling
- no-source warning visibility
- low-space stop threshold
- additional reserved free-space offsets
- archive / retention floor if it changes deletion recovery posture

Each row must classify the current state as `default`, `hardened`, `relaxed`, `suppressed`, or `surface-divergent`.

### 3) Surface honor / ignore rows

Show whether the relevant surface:

- fully honors the guardrail
- partially honors it
- ignores it
- cannot express it but still receives the consequence

The page must be able to say when a low-level safety override is ineffective or invisible on a specific surface.

### 4) Threshold floors and stop behavior

For threshold-bearing overrides show:

- exact current floor
- what event triggers the stop or warning
- whether work pauses, warns, or continues
- what bytes / actions are unaffected
- what explicit recovery or relief action clears the condition

This section must answer:

> what exact floor will actually stop or suppress work here?

### 5) Safe next actions

Actions may include:

- `Strengthen guardrail`
- `Restore default warning`
- `Raise stop floor`
- `Acknowledge riskier posture`
- `Open delete consequence`
- `Export safety receipt`

Each action must preview whether it changes visibility, behavior, or both.

## Public object

### Safety override page

Fields:

- `safety_override_page_id`
- `seat_ref`
- `subject_ref` nullable
- `safety_posture_verdict`
- `guardrail_rows[]`
- `surface_honor_rows[]`
- `threshold_rows[]`
- `safe_next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. guardrail
2. effective posture
3. honored / ignored surface note
4. strongest consequence
5. safest next action

Example:

```text
placeholder-delete propagation     delete-guard-strengthened     desktop honors, linux-web partial     local removal will recreate placeholder instead of deleting globally     Export safety receipt
```

## Non-goals

This page does **not** replace full delete-wave review or capacity planning.
It proves only **which hidden settings are currently changing destructive guardrails, warnings, or stop floors, and how those changes are actually honored**.
