# Shell-extension loss, context-menu dependence, and in-app capability equivalence interface spec

## Purpose

The archive already had projection-parity, local-web-first, and shell/workspace language.
What it still lacked was one explicit contract for a very practical failure mode:

> the operating system's file-browser integration disappears or degrades, and the user suddenly loses the actions they thought defined the product.

Current official Resilio docs make this seam sharper than a simple `relaunch Finder` workaround.
They still say sync-related context menus on Mac and Windows appear only for shares with Selective Sync enabled, that Finder extensions may need manual re-enable plus Finder relaunch, that other apps can conflict with the same extension mechanism, and that on Windows context-menu items appear only on NTFS because they depend on alternate data streams.
The same troubleshooting flow also points users to shell-extension DLL presence and extension commands rather than to one in-app explanation of what capability actually remains.

That is not just OS annoyance.
It is a product-contract problem if the shell affordance has silently become the semantic source of truth.

## Core decision

AnonSync should treat file-browser integration as a **projection accelerator**, never as the primary home of capability truth.

Every shell-surface action must have a first-class in-app equivalent that remains available and semantically identical even when shell integration is missing.
The interface contract must distinguish:

- capability truly unavailable
- capability available but shell projection missing
- capability available only for certain subject postures
- capability available, but shell projection unhealthy on this seat

## Why this matters

Current Resilio docs still reveal five interface mistakes AnonSync should not clone:

- actions can appear to exist only when a particular subject posture (for example placeholder-capable posture) is active
- extension health becomes part of the user's mental model before the app ever explains the same action in-app
- file-system class (such as NTFS) can unexpectedly decide whether shell affordances exist at all
- extension conflicts with other products can erase actions from the user's normal workflow
- recovery advice can become shell-specific maintenance lore instead of a clear statement that the underlying capability still exists elsewhere

AnonSync should therefore keep one stronger rule:

> shell loss may cost convenience, but it may not cost semantic clarity.

## Fixed review order

Every shell-integration incident should render the same sections in the same order:

1. **Action equivalence now**
2. **Shell health and cause**
3. **In-app continuation**
4. **Shell restore receipt**

### 1) Action equivalence now

This section should show:

- which action the operator expected in the shell
- the same action's in-app location
- whether the action depends on subject posture (for example placeholder-capable or materialized-only)
- whether any capability is truly unavailable or only absent in the shell

The operator must be able to answer: **can I still do the thing, and where?**

### 2) Shell health and cause

This section should show:

- extension enabled/disabled state
- file-browser/OS support state
- filesystem support state for shell affordances
- known conflicts or blockers
- most recent shell health sample time

The operator must be able to answer: **why did the shell entry disappear?**

### 3) In-app continuation

This section should show direct continuation actions such as:

- `materialize here`
- `evict local copy`
- `share from workspace`
- `open capability review`
- `repair shell projection`

The operator must be able to answer: **how do I continue right now without fixing the shell first?**

### 4) Shell restore receipt

This section should show:

- extension state before/after
- conflicts found
- filesystem limitations noted
- whether restoration succeeded
- whether the operator chose to keep working without shell integration

The operator must be able to answer: **did the shell get repaired, and was any capability ever actually lost?**

## Main surface

The shell/workspace should expose a visible **Shell integration** card on seats where browser/file-manager affordances exist.
The card should say things like:

- `shell actions healthy`
- `shell actions unavailable on this filesystem`
- `shell extension disabled; in-app actions remain available`
- `subject posture does not currently expose shell materialization actions`

The product should never make the operator infer from missing context-menu entries that the underlying share capability vanished.

## Object model implications

AnonSync should add or strengthen these objects:

- `shell_projection_state`
- `shell_action_equivalence_record`
- `shell_health_incident`
- `shell_restore_receipt`

Suggested fields for `shell_projection_state`:

- `seat_id`
- `file_browser_kind`
- `extension_enabled`
- `filesystem_support_tier`
- `subject_posture_requirements[]`
- `conflict_hints[]`
- `equivalent_actions[]`

## Event language

Use explicit phrases such as:

- `shell action missing; in-app equivalent available`
- `shell integration disabled on this seat`
- `filesystem does not support shell affordance class`
- `subject posture does not expose shell materialization actions`
- `shell projection restored`

Avoid vague lines such as:

- `menu missing`
- `sync not integrated`
- `try restarting explorer`

## CLI shape

Example commands:

```text
anonsync shell status
anonsync shell explain-action materialize
anonsync shell repair review
anonsync shell receipt <id>
```

The CLI must make it obvious whether the issue is shell convenience, subject posture, filesystem support, or actual capability loss.

## Failure and edge cases

### Filesystem cannot host shell affordances

The product must say `shell affordance unsupported on this filesystem` rather than offering a fake repair loop.

### Extension conflict with another app

The product must treat this as a shell-health incident, not as disappearance of share semantics.

### Subject posture gates shell affordance

If shell actions only make sense for placeholder-capable or materializable subjects, the app must explain that posture link explicitly.

## The non-clone reason

This is another clean example of why AnonSync should not merely copy Resilio's surface.
Current official Resilio docs still leave too much meaning about shell actions, posture dependence, filesystem dependence, and extension health scattered across Finder/Explorer troubleshooting pages.
AnonSync should instead make shell integration an explicit accelerator layered on top of a complete in-app capability surface.
