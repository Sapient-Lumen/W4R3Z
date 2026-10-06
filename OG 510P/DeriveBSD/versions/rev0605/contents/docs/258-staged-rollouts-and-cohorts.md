# Staged rollouts + cohorts (update decisions as evidence)

A/B boot environments and automatic boot assessment help *recover* from bad updates,
but they don’t prevent the most common operational failure:

> “We offered a broken release to everyone at once.”

Mature ecosystems treat **rollout control** as a first-class system.
DeriveBSD should bake staged rollouts in early, and (critically) treat rollout decisions as **receipted evidence**.

## Goals

- Support percentage-based staged rollouts (canary → ramp → full).
- Support **cohorts** (stable user buckets) so a device sees consistent behavior.
- Treat “offer update / hold back / block” decisions as verifiable receipts.
- Bind rollout behavior to policy so it can’t silently drift.

## Prior art to steal

- **Omaha** (Chrome/Chromium updater) cohort-based server control.
- **Uptane**: separate “bytes authenticity” from “assignment decisions” (Director role).
- General staged rollout practice: start small, expand after observing health.

See also: `docs/127-uptane-director-targets.md`, `docs/231-ab-updates-and-recovery-semantics.md`, `docs/241-boot-try-counters-and-boot-assessment.md`.

## When you need multi-hop update paths (graph lane)

`rollout.policy` is the right default when the question is simply:

> “Should this device be offered the newest release capsule yet?”

Large fleets often need a second primitive: **an explicit, signed set of allowed transitions** (skip constraints, barriers, dead-ends, prerequisite receipts).

DeriveBSD models this as:

- `rollout.graph` (signed DAG of allowed transitions)
- optional `rollout.assignment` (explicit approvals / barrier overrides)
- `rollout.traversal.receipt` (host-side evidence of which edge was chosen and why)

See: `docs/177-fleet-coordinated-rollouts.md`.


## New artifact: `rollout.policy`

A `rollout.policy` is a small policy object that defines:

- the **release capsule** it applies to
- how to assign devices to cohorts (deterministic salted hashing)
- the rollout phases (percentages + minimum durations)
- guardrails (halt/abort triggers; freeze windows; manual overrides)

Schema: `spec/rollout.policy.schema.json`.
Example: `spec/examples/rollout.policy.json`.

### Cohort assignment: deterministic but steerable

DeriveBSD wants cohort assignment to be:

- stable for a given device id (no flapping)
- deterministic for audit (given a salt + device-id hash, the cohort is predictable)
- steerable by an update authority in emergencies

We do this by:

- defining cohort assignment as a pure function of `stable_id_hash` and a `salt_digest`
- allowing an optional *cohort hint* (server-set bucket label) only if it is covered
  by a signed/receipted decision

This mirrors how real-world update systems use cohorts while preserving audibility.

### Cohort privacy (don't invent a tracking ID)

Cohorts are operationally necessary but can become a long-lived identifier if the cohort space or hints are too specific.
DeriveBSD makes privacy constraints explicit via an optional `cohorting.privacy` block in `rollout.policy` (entropy budget, max cohorts, min bucket size, and salt rotation).

See: `docs/261-rollout-privacy-and-cohort-hygiene.md`, RFC-0193.

## New artifact: `rollout.receipt`

Every update check produces a `rollout.receipt` that records:

- which `rollout.policy` (digest) was used
- which `release.capsule` was under consideration
- the device cohort id (as a hash, not raw identifiers)
- the decision (`offer_update`, `hold_back`, or `blocked`) + reason codes

Schema: `spec/rollout.receipt.schema.json`.
Example: `spec/examples/rollout.receipt.json`.

Receipts can be attached to incident bundles to answer:

- “Was this device offered release X?”
- “Under which rollout phase and conditions?”
- “Did policy permit an override?”

## Integration sketch

1) Channel points to a `release.capsule` digest.
2) Update control-plane evaluates:
   - trust policy + evidence
   - rollout policy (phase/cohort)
3) Emit `rollout.receipt`.
4) If offered, host proceeds with:
   - apply change set
   - confirmable change-set semantics (`docs/242-confirmable-change-sets-and-auto-revert.md`)
   - boot assessment counters

## Non-goals

- This does not specify a single update server protocol.
- This does not mandate online-only: rollouts can be expressed offline by shipping a
  signed `rollout.policy` alongside the capsule.

See: `rfcs/RFC-0190-staged-rollouts-and-cohorts.md`.

Last updated: 2026-02-25
