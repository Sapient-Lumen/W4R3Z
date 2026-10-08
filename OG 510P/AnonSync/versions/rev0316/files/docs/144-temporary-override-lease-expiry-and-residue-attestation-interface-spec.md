# Temporary override lease expiry and residue attestation interface spec

## Purpose

Once the product can distinguish an **incident overlay** from a **standing mutation**, one more seam immediately appears:

- how does a temporary override stay temporary?
- how does the operator know whether it really expired, rolled back, or left residue behind?
- how does the system avoid the classic outcome where a debugging tweak, route override, or path exception silently becomes the new normal?

This document defines the interface contract for **temporary override leases**, **expiry review**, and **residue attestation**.

## Core rule

Every approved incident overlay must carry a lease with:

1. a start condition
2. a stop or expiry condition
3. a rollback path
4. an expiry review
5. a residue attestation

The product must not rely on operator memory to turn temporary troubleshooting state back into baseline state.

## Why this needs its own spec

Current Resilio docs again sharpen the need for this boundary.

They currently document things like:

- enabling debug logging, reproducing the issue, and leaving logging on for a while
- profiler capture that requires restart
- enlarged log size
- share-level network behavior controls like relay, tracker, LAN search, and predefined hosts
- host-level or config-file parameters that can persist across launches and across machines
- synchronization-mode and default-root choices that continue affecting future arrivals until changed again

Each of those may be used temporarily for diagnosis or mitigation.
But the docs mostly leave the operator to remember when to undo them or to notice later that behavior remained changed.

AnonSync should instead make every temporary override a leased object whose end state is reviewable.

## Public objects

### Temporary override lease

The durable object that tracks one incident-bounded override.

Suggested fields:

- `temporary_override_lease_id`
- `incident_ref`
- `origin_recipe_ref`
- `overlay_scope_summary`
- `started_at`
- `lease_kind` (`time-boxed`, `until-proof-observed`, `until-next-restart`, `until-subject-settles`, `manual-close-required`)
- `lease_deadline` nullable
- `rollback_plan_ref`
- `expiry_state` (`active`, `expiring-soon`, `expired-awaiting-review`, `rolled-back`, `residue-detected`, `closed-cleanly`)
- `residue_risk_class` (`low`, `medium`, `high`)

### Lease trigger row

One event that can start, extend, or close the lease.

Suggested fields:

- `lease_trigger_row_id`
- `trigger_kind` (`approved`, `proof-observed`, `deadline-hit`, `manual-close`, `restart-observed`, `policy-replaced`, `rollback-failed`)
- `trigger_summary`
- `effect_on_lease`

### Residue check row

One concrete thing the product must verify after expiry or rollback.

Suggested fields:

- `residue_check_row_id`
- `check_kind` (`setting-restored`, `path-default-restored`, `network-override-removed`, `logging-disabled`, `config-overlay-absent`, `future-simulation-unchanged`, `share-default-cleared`)
- `check_scope`
- `freshness_requirement`
- `result_state` (`pending`, `clean`, `drifted`, `inconclusive`)
- `evidence_ref` nullable

### Residue attestation object

The summary object shown after expiry review.

Suggested fields:

- `residue_attestation_id`
- `lease_ref`
- `attestation_verdict` (`clean-expiry`, `clean-rollback`, `residue-present`, `could-not-prove-clean`)
- `remaining_residue_summary`
- `future_effects_if_ignored`
- `followup_recipe_ref` nullable
- `closed_at` nullable

## Fixed inspection order

Every lease-expiry surface should preserve this order:

1. **Why this override exists**
2. **When and how it is supposed to end**
3. **What must be restored or cleared**
4. **What the system observed at expiry**
5. **Whether residue remains**
6. **Close cleanly, extend with review, or promote to standing draft**

### 1) Why this override exists

The surface should restate the incident and the bounded scope.
Examples:

- `temporary route override for one member while disambiguating relay dependence`
- `elevated logging for one reproduction window`
- `one-share download-order override to test settlement impact`

### 2) When and how it is supposed to end

This section should state the lease rule plainly:

- `ends in 20 minutes unless extended`
- `ends after next restart`
- `ends once convergence verdict changes from overdue to expected`
- `ends when all named subject/member cells settle or when deadline hits`

### 3) What must be restored or cleared

The operator should see a checklist such as:

- disable elevated logging
- restore prior host or share default
- remove temporary predefined host or route override
- revert arrival exception
- clear temporary config overlay
- recompute future simulation to prove no new standing effect remains

### 4) What the system observed at expiry

This section should present evidence, not optimism:

- `logging flag no longer present`
- `download-priority override still present on share S`
- `future-arrival simulation unchanged from baseline`
- `host launched with temporary config overlay on latest restart`

### 5) Whether residue remains

The verdict should be explicit:

- `clean expiry`
- `clean rollback`
- `residue detected`
- `could not prove clean because host was not observed after restart`

### 6) Close cleanly, extend with review, or promote to standing draft

The call to action should match what was observed:

- `Close lease`
- `Extend lease with reason`
- `Open cleanup recipe`
- `Promote to standing mutation draft`

## Public rules

### Rule 1 — every overlay must have a lease

No incident overlay may be approved without an explicit ending model.

### Rule 2 — expiry without attestation is incomplete

A timer reaching zero is not enough.
The system must still check whether the override actually stopped affecting behavior.

### Rule 3 — residue must describe future consequence

If residue remains, the product must explain what future behavior is still changed.

### Rule 4 — extension is a new review event

Extending a lease must not be a silent keepalive.
It requires a new reason and a fresh deadline or stop condition.

### Rule 5 — promotion to standing scope must be explicit

If the operator wants to keep the override, the product should open a standing-mutation draft instead of quietly letting the lease drift forever.

### Rule 6 — cleanup evidence must be local-first

Whenever possible, residue attestation should rely on observed local state and fresh simulation rather than assumptions about what probably got restored.

## Dense row contract

A dense lease row should preserve these labels in this order:

- `Override`
- `Lease kind`
- `Ends when`
- `Residue checks`
- `Current verdict`
- `Next action`
- `State`

## Example prompts

- `When is this override supposed to end?`
- `Did the temporary logging or route tweak really clear?`
- `What residue is still changing future behavior?`
- `Should this be extended, cleaned up, or promoted to a standing draft?`
- `What could not yet be proven clean?`

## Anti-goals

- do not treat elapsed time as proof of cleanup
- do not let temporary overrides disappear into generic activity history
- do not let `still seems needed` replace a real extension review
- do not close an incident while leased residue still changes future behavior invisibly
