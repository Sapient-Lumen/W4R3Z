# Hardware support conditions and known limitations boundary

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt

`docs/533-hardware-support-qualification-status-boundary.md` fixed whether a support proof is current.
This doc fixes the next small but expensive ambiguity:
**what exactly makes a hardware support claim `conditional`, `canary-only`, or `maintenance-only` must be typed and published, not left in release-note prose.**

See also:
- ADR: `adrs/ADR-0124-hardware-support-conditions-and-known-limitations-boundary.md`
- support catalog boundary: `docs/528-hardware-support-matrix-and-bundled-admission-boundary.md`
- promotion semantics: `docs/529-hardware-support-promotion-and-qualification-boundary.md`
- qualification receipt boundary: `docs/530-hardware-support-qualification-receipt-boundary.md`
- qualification profile boundary: `docs/531-hardware-support-qualification-profile-boundary.md`
- qualification freshness boundary: `docs/532-hardware-support-qualification-freshness-boundary.md`
- qualification status boundary: `docs/533-hardware-support-qualification-status-boundary.md`
- hardware compatibility preflight: `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`
- workstation viability: `docs/410-desktop-viability-checklist.md`
- support catalog shape: `spec/hw.support.matrix.schema.json`
- qualification receipt shape: `spec/hw.support.qualification.receipt.schema.json`
- compatibility report shape: `spec/hw.compat.report.schema.json`

## Why this needs a hard decision

The archive can already answer several support questions with typed artifacts:

- which catalog entry matched,
- which standard and receipt back it,
- whether the proof is fresh enough to count,
- and whether the proof is still the current published evidence.

But it still could not answer one practical question cleanly:

- **what exact published limitation or prerequisite makes this claim less than fully supported?**

Without that boundary, `conditional` support quietly degrades back into prose:

- a workstation warning can say “trusted UI floor risk” without naming the actual published caveat,
- a fleet host can inherit a conditional support class without a stable reason code for why breakglass is needed,
- and a factory bundle can say “approved with caveats” while the real prerequisite lives in ticket notes.

That is too mushy for a release-shaped archive.

## Accepted boundary

Across all profiles:

- `hw.support.matrix.entries[].conditions[]` is now the tiny typed publication surface for non-fully-supported hardware claims,
- `conditions[]` is required for `conditional`, `canary-only`, and `maintenance-only` entries,
- each condition carries `condition_id`, `reason_code`, optional `affected_roles`, `summary`, and `required_posture`,
- `hw.support.qualification.receipt.support_claim.condition_ids` snapshots those published ids for the evidence object backing the claim,
- and `hw.compat.report` may now emit `support-condition-triggered` and record `support_matrix.matched_condition_ids` when one of those published conditions is part of the report outcome.

The point is narrow:
**the archive now has a typed answer for why a claim is not simply `supported`.**

## Minimal v0 contract worth implementing

### `hw.support.matrix.entries[].conditions[]`

Each published condition is intentionally small:

- `condition_id` = stable join id
- `reason_code` = compact category such as `topology-variant-unverified`, `firmware-cohort-unverified`, or `recovery-prerequisite`
- `affected_roles` = optional role subset the caveat touches
- `summary` = human-readable statement of the limitation/prerequisite
- `required_posture` = typed operational answer such as `trusted-ui-consent`, `verified-recovery-required`, `breakglass`, `maintenance-window-only`, or `deny-until-qualified`

This is enough to keep the published caveat reviewable without inventing a live advisory engine.

### `hw.support.qualification.receipt.support_claim.condition_ids`

The receipt remains evidence-only, but it now snapshots the condition ids for non-fully-supported claims.
That keeps the proof object tied to the same published caveats the matrix entry declared, instead of leaving the matrix and receipt to drift independently.

### `hw.compat.report`

Preflight/reporting gets a direct join for published caveats:

- `support-condition-triggered` in `findings[]`
- `support_matrix.matched_condition_ids`

The exact portable join token is `matched_condition_ids`; the point is that support caveats now have a stable id-level review surface rather than hiding in prose.

That is intentionally distinct from broader findings like `trusted-ui-floor-risk` or `qualification-stale`.
One says *which published caveat fired*; the others say *what sort of system risk or support-drift consequence follows*.

## Product-shape fit

### A) Secure fleet host

- cohorts can distinguish “supported except under this known variant/prerequisite” from a generic warning blob
- breakglass reviews get stable condition ids instead of cargo-cult notes

### B) Secure workstation

- trusted-UI consent can name the actual caveat behind a `conditional` claim
- dock/display/topology or verified-recovery prerequisites stop hiding inside prose

### C) General-purpose OS

- explicit local override still exists
- typed caveats make the review surface more honest without forcing factory-style hard gates

### D) Appliance factory / regulatory

- offline bundles can publish the caveat/prerequisite alongside the claim and its proof
- support paperwork becomes easier to audit because “conditional” is no longer folklore

## What this does **not** decide yet

This doc does **not** freeze:

- a universal topology matcher for every dock, monitor, or peripheral path,
- the final long-term taxonomy of every possible condition reason code,
- or a live notification service that pushes post-publication advisories.

The decision is smaller:
**support claims now have typed caveats and prerequisites.**

## Why this is the right small hard decision

This is not a giant certification subsystem.
It is a coherence move:

- the matrix stays the compact published catalog,
- the receipt stays the typed evidence object,
- the profile still defines the qualification floor,
- freshness and status still answer whether the proof is current,
- and conditions now answer *why the published claim is not simply `supported`*.

That is enough to make future implementation work more honest without forcing the archive to solve every topology-matching or remediation detail up front.

## External practice that shaped this cut

- Android compatibility is release-shaped and device/SKU-specific rather than a timeless universal support bit.
- Ubuntu’s certified hardware guidance distinguishes tested listed devices from “try it and verify on your own hardware.”
- Red Hat certification is model-specific and test-plan-specific rather than a vague evergreen badge.

Last updated: 2026-03-17r263
