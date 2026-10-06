# Vision

DeriveBSD aims to make BSD hosts and workload stacks **reproducible, rollbackable, inspectable, and distributable** from a cleanly planned derivation pipeline—while defaulting to **small blast radius** at runtime (microVM-first).

## One-sentence definition

DeriveBSD derives **signed**, reproducible **host generations** and **microVM workload images** from typed manifests, built in jailed sandboxes, switched atomically on ZFS boot environments, and rolled back instantly.

## The core idea

We win by designing the **Derive core** first:

- **Spec → Lock → Plan → Artifact → Activate/Launch**
- Store + Sandbox + Trust + Cache (verifiable distribution)
- Introspection + UX + Policy (explainable decisions)

BSD then multiplies value via:

- **jails** as the default hermetic build sandbox
- **bhyve** as the default runtime isolation boundary (microVM-first)
- **ZFS** boot environments and snapshots as the activation/rollback substrate
- **pf anchors** as a composable, per-instance networking primitive
- capability hardening (Capsicum/Casper) to shrink ambient authority

## Day-0 behavioral contract

The “must be true by default” behaviors live in:
- `docs/97-non-negotiable-behaviors.md`

(That file is the checklist we defend whenever we consider “convenience” features.)

## Success criteria

- A new host can be reproduced from a pinned spec in one command (no implicit inputs).
- Every deployed bit is explainable (“why is this here?”, “who signed it?”, “where did it come from?”).
- Upgrades are reversible by default (fearless switching).
- Builders are treated as hostile; compromise is contained to the sandbox and detected by verification.
- Runtime isolation is strong by default: most workloads run as signed microVM artifacts, not host mutations.

Last updated: 2026-02-23
