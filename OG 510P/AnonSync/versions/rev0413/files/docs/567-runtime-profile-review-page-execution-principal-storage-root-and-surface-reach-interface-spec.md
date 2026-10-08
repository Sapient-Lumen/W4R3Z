# Runtime profile review page — execution principal, storage root, and surface reach

## Purpose

Give the operator one reviewed answer to:

- which runtime profile is actually in charge right now
- which execution principal owns it
- which storage root and profile lineage back it
- which control and observation surfaces are currently in effect
- whether the operator is still inside the same seat continuity or looking at a fresh runtime profile

This page is the runtime-level companion to seat-lineage, posture, and capability pages.
It should appear whenever the host has more than one plausible runtime locus or whenever the operator is about to switch runtime envelope.

## Inputs

- host / seat identifier
- runtime kind (`foreground-app`, `service-current-user`, `service-local-service`, `service-local-system`, `config-mode-cli`, `unknown`)
- execution principal / account label
- storage root path and whether it is default or configured
- current identity surface (name / fingerprint / profile id as available)
- share database presence and carryover evidence
- WebUI listen scope and bound interface state
- shell / notification / watcher affordance evidence if applicable
- migration history if known
- prior runtime profiles seen on this host

## Primary questions this page must answer

1. What runtime profile is currently active?
2. What principal is executing it?
3. What storage root is authoritative for this profile?
4. Is this the same seat continuity, a migrated profile, or a fresh runtime profile?
5. What surfaces or capabilities widened or narrowed because of this runtime envelope?

## Layout

### A. Runtime identity card

Fields:

- runtime profile class
- executing principal
- storage root
- profile lineage verdict (`same-profile`, `migrated-profile`, `fresh-profile`, `ambiguous`)
- identity surface verdict (`carried-forward`, `fresh`, `hidden`, `unknown`)

### B. Share carryover card

Fields:

- share catalog posture (`carried`, `empty-because-fresh-profile`, `partial`, `unknown`)
- reconnect / re-share expected? (`no`, `some`, `yes`)
- advanced-folder support posture if config mode applies

### C. Surface reach card

Fields:

- WebUI reach (`local-only`, `lan-reachable`, `bound-to-specific-interface`, `unreachable-risk`)
- shell affordance posture (`present`, `narrowed`, `not-applicable`, `unknown`)
- observation posture (`native notifications`, `rescan-biased`, `unknown`)

### D. Continuity sentence block

Three stacked lines:

- **What this profile is**
- **What it inherited**
- **What it did not inherit or may have changed**

Example:

- `This host is currently operating the Local System service profile.`
- `Its storage root is the service-system profile root, not the former foreground-app root.`
- `Old shares were not carried here; manual re-share / reconnect work is still required.`

## Required interactions

- `Review storage lineage forecast`
- `Switch runtime profile`
- `Compare with previous profile`
- `Export runtime profile receipt`
- `Open seat lineage`

## Guardrails

- Never treat runtime kind as cosmetic if principal or storage root changed.
- Never imply `same seat` when a fresh storage root and empty share catalog indicate a new runtime profile.
- Never hide a widened WebUI reach behind a generic `service enabled` sentence.
- Never hide observation narrowing behind a generic `running in background` sentence.

## Output

A reviewed runtime-locus verdict that downstream switch, migration, uninstall, and control-surface pages must inherit without reinterpretation.
