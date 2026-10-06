# ADR-0006: No PCI passthrough by default

Status: Accepted

## Context

PCI passthrough materially increases blast radius:
- expands the TCB (device firmware, drivers)
- increases DMA risks
- complicates portability and reproducibility

## Decision

DeriveBSD defaults to **no PCI passthrough** for workload microVMs.

- If passthrough is needed, it must be:
  - explicit in Spec/Plan
  - policy-approved
  - surfaced in blast-radius diffs

## Consequences

- Default microVM posture remains “minimal hardware surface”.
- Most workloads use virtio devices only.
