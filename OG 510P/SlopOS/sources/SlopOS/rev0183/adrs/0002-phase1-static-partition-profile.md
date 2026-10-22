# ADR-0002: Phase 1 deliverable is the static partition profile (D-PART)

Status: Accepted

## Context
We are still evaluating three long-lived architectures:
- A) hypervisor-first
- B) microkernel-first
- C) separation-kernel-first

This choice is not just about engineering—it strongly determines proof strategy and early evidence.
At the same time, the archive needs a Phase 1 deliverable that:
- meaningfully exercises boot/provenance + capability-mediated authority + isolation,
- keeps the privileged surface small and budgetable,
- yields an early “assurance plateau” without committing the long-term architecture prematurely.

Several candidate strands already converge on the same early slice:
- **D-PART / CH-PART** (static partition policy) for strong isolation with minimal emulation.
- **D-ADDRNET / CH-ADDRNET** (translation graph + table generation) for a pinned, auditable DMA/mapping story.
- **CH-KABI + CH-LOG** for a closed privileged action set + replayable transcript.

## Decision
We adopt **D-PART (static partition profile)** as the Phase 1 assurance deliverable, independent of the eventual A/B/C architecture decision.

Phase 1 scope:
- Boot applies **CH-PART** (+ optional CH-ADDRNET) and reaches a stable running configuration.
- Runtime privileged behavior remains intentionally narrow:
  - minimal scheduling/timers for partitions,
  - strict resource isolation (CPU sets, RAM ranges, device resources),
  - minimal, explicit cross-partition channels.

Phase 1 explicitly does **not** attempt:
- rich device emulation,
- dynamic creation of partitions,
- general SMP concurrency claims beyond the declared D-CONC profile.

## Consequences
- **Progress without premature lock-in:** we can write/verify a tractable abstract-machine slice and still keep A/B/C open.
- **Early DMA pressure relief:** CH-ADDRNET becomes the preferred mechanism to avoid “IOMMU required” as a hand-wave; where the platform lacks an IOMMU we downgrade claim scope explicitly.
- **Governance:** any expansion of exit/ABI/driver surface beyond the Phase 1 budget requires explicit RFC→ADR promotion.

## Evidence
- EVID-2026-022 (CH-PART seam)
- EVID-2026-023 (CH-ADDRNET seam)

## Affected claims/invariants
- Claims: C-ISO-1 (isolation), C-BOOT-1 (boot integrity), C-OBS-1 (audit/replay)
- Invariants: I-PART-1/I-PART-2, I-DMA-1 (conditional), I-BOOT-1, I-LOG-1

## Links
- RFC-0021 (static partition profile)
- RFC-0022 (address decoding nets)
- docs/30-architecture/exit-surface-budget.md
- docs/30-architecture/hypervisor-first-evaluation.md
