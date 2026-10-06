# Chaos experiments and fault injection as leases (optional)

Chaos engineering is a discipline for discovering fragility by **injecting controlled failures**.
The ecosystem lesson is not “randomly kill things”, but that resilience improves when failure injection is:

- routine,
- bounded,
- observable,
- reversible,
- and tied to hypotheses.

DeriveBSD’s greenfield win is that failure injection can be treated as **temporary authority**:

> you should not be able to inject faults unless you hold a lease.

## The stance

- **Optional lane:** chaos tooling exists, but is policy-gated.
- **No ambient chaos:** no “root can run anything anywhere” assumptions.
- **Receipts everywhere:** experiments emit receipts that join to incidents/changes.

## Why bake this in

If we don’t standardize the lane early, people will reinvent it as:
- ad-hoc SSH scripts,
- bespoke kill loops,
- or production load tests with no audit trail.

A first-class lane means:
- experiments are reviewed like other changes,
- blast radius is explicit,
- results are durable evidence.

## Design: chaos is a typed plan + receipt

### Artifacts

- `chaos.experiment.plan` (reviewed, policy-checked)
- `chaos.experiment.receipt` (what happened, bounded evidence)

These integrate with:
- `authority.diff` (new ability to inject faults is a new authority edge)
- `trust.boundary.diff` (experiments cross boundaries)
- `blast_radius.diff` (fault type implies affected surfaces)

### Plan content (what must be explicit)

- target selector (fleet + class + labels)
- fault actions (kill, delay, packet drop, disk pressure, CPU pressure)
- budgets:
  - timebox (max duration)
  - volume (max affected instances)
  - safety stop conditions (SLO breach thresholds)
- hypothesis / steady state checks
- rollback / stop procedure

### Receipts

Receipts should record:
- the plan digest,
- which targets were affected,
- start/stop timestamps,
- observed outcomes (pass/fail + reason codes),
- safety stops triggered (if any),
- links to incident/change ids.

## Policy hooks (keep it sane)

- Require **two-person integrity** for high-impact experiments.
- Require *maintenance window* or explicit override receipts.
- Require “canary first” policies:
  - smaller subset first,
  - then broaden only if steady state holds.

## Ergonomics

- Make “practice failure” easy in test realms:
  - inject faults into `testrealm.plan` environments first.

- Make common faults reusable:
  - ship a small library of signed “fault bundles”.

## Non-goals

- Random failure injection without hypotheses.
- A monolithic “chaos platform”.

## References

- IBM overview of chaos engineering (history + goals):
  - https://www.ibm.com/think/topics/chaos-engineering
- Chaos Mesh project overview (Kubernetes-oriented, but useful fault taxonomy):
  - https://chaos-mesh.org/blog/chaos_mesh_your_chaos_engineering_solution/

Last updated: 2026-02-27r110
