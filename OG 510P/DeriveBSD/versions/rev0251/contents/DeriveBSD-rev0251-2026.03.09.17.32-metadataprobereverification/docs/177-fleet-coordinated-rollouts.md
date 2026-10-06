# Fleet-coordinated staged rollouts (optional lane)

DeriveBSD already has:
- atomic switch + rollback (ZFS boot environments)
- health-gated updates (`docs/112-health-gated-updates.md`, `docs/335-boot-assessment-greenboot-and-health-gated-rollback.md`)
- Uptane director lessons for separating “bytes authenticity” from “assignment decisions” (`docs/127-uptane-director-targets.md`)

At fleet scale, we need one more *boring primitive*:

> **A deterministic, explainable way to stage updates across many nodes** without requiring a full orchestration system.

This doc focuses on the **graph-based** and **assignment** primitives used by real ecosystems (Cincinnati/Zincati, OSUS, Omaha), and maps them onto Derive artifacts.

Product-shape note: this is the natural default A-story now that `docs/472-update-delivery-and-release-posture-by-profile.md` fixes `fleet_host` updates as `health-gated`; C may adopt the same machinery explicitly, but it is not the hidden baseline for broad-compat general-purpose installs.

If you only need *single-release phasing* (“offer the newest capsule slowly”), start with:
- staged rollouts + cohorts: `docs/258-staged-rollouts-and-cohorts.md`
- privacy constraints for cohorts: `docs/261-rollout-privacy-and-cohort-hygiene.md`

## Why bake this in now

Phased rollouts are an OS ecosystem feature, not a tooling afterthought.
If we don’t specify it early, every operator will invent incompatible rollout controllers and ad-hoc “update windows” behavior.

DeriveBSD’s greenfield advantage is to make rollout intent **data**, and rollout decisions **receipted evidence**.

## Prior art worth stealing

- **Fedora CoreOS**: Cincinnati (update graph protocol) + Zincati (host agent) + *rollout wariness* steering.
- **OpenShift Update Service (OSUS)**: graph-based update recommendations built on the Cincinnati protocol.
- **Omaha** (Chrome/Chromium updater): cohorting + server control + client backoff and reporting.
- **Bottlerocket**: wave schedules encoded as data alongside signed repository metadata.

Pointers: see `docs/32-curated-references.md` (Update rollout + cohorting).

## DeriveBSD mapping

### Level 1: Single-release phasing (`rollout.policy` + `rollout.receipt`)

For the most common operational need (“offer the latest release gradually”), DeriveBSD already standardizes:

- `rollout.policy` (phases + cohort assignment + guardrails)
- `rollout.receipt` (offer/hold/block decision evidence per update check)

See: `docs/258-staged-rollouts-and-cohorts.md`.

### Level 2: Multi-hop update paths (`rollout.graph`)

Real fleets often need more than “latest release”:

- supported upgrade paths (skip constraints)
- barriers (“don’t cross until telemetry says OK”)
- dead-ends (withdrawn releases)
- required prerequisites (boot gate policy, attestation receipts, etc.)

A `rollout.graph` is a signed DAG of allowed transitions:

- node = `release.capsule` digest (deployment payload handle)
- edge = allowed transition, optionally guarded by constraints

Schema: `spec/rollout.graph.schema.json`.
Example: `spec/examples/rollout.graph.json`.

This is intentionally close to Cincinnati’s “DAG of releases + edges as valid transitions” mental model, but expressed as a content-addressed Derive artifact.

### Level 3 (optional): Explicit assignment receipts (`rollout.assignment`)

Some environments want a *director-like* service to emit explicit approvals:

- “this host may move to capsule X now”
- “this host may cross barrier Y (emergency hotfix)”

`rollout.assignment` is a signed object binding:
- host identity (hash)
- approved next `release.capsule` digest
- optional linkage to a `rollout.graph` digest (and/or a `rollout.policy` digest)

Schema: `spec/rollout.assignment.schema.json`.
Example: `spec/examples/rollout.assignment.json`.

This is compatible with Uptane’s Director role and provides an auditable “override” lane.

### Host-side behavior (`rollout.traversal.receipt`)

A minimal host agent can stay deterministic and inspectable:

1) Fetch + verify `rollout.graph`.
2) If present, verify `rollout.assignment` and treat it as a constraint relaxer (e.g., barrier override).
3) Evaluate candidate edges under local policy:
   - update windows
   - reboot coordination lock (optional)
   - health gate requirements
4) Emit `rollout.traversal.receipt` recording:
   - chosen edge (from→to)
   - why others were rejected
   - which prerequisites were validated

Schema: `spec/rollout.traversal.receipt.schema.json`.
Example: `spec/examples/rollout.traversal.receipt.json`.

## Evidence and explainability

The point of this lane is not “automation for its own sake”, but **auditability**:

- `derive explain rollout` should answer:
  - why was this node offered this update?
  - which graph edge (or assignment) authorized the transition?
  - what constraints applied (barrier, required receipts, boot gate policy)?

Attach rollout receipts to incident bundles to make “update archaeology” unnecessary.

## Non-goals

- building a Kubernetes operator in-tree
- requiring a central coordinator for small deployments

Last updated: 2026-03-06r201
