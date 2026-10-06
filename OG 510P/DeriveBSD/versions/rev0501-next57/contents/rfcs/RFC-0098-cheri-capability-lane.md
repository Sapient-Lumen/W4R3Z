# RFC-0098: CHERI capability lane (optional)

Status: **draft**

## Problem

DeriveBSD wants to minimize TCB and limit blast radius. Many critical failures are memory-safety failures.
When CHERI-capable stacks exist (e.g., CheriBSD), DeriveBSD should be able to take advantage without changing its core model.

## Proposal

Add an optional target attribute:
- `abi_profile: { native | cheri_purecap | cheri_hybrid }`

When `cheri-*` is selected:
- toolchain identity is pinned in Lock
- Plan and artifact metadata include the ABI profile
- the resulting artifacts can be consumed only by compatible hosts/guests

## Initial integration points

- microVM guest images (CheriBSD guest lane)
- selected control-plane binaries (where feasible)
- microVM DevShell isolation mode (optional)

## Evidence

Emit `cheri.lane.evidence.json`:
- abi profile
- toolchain bundle digest
- artifact digest

## Tradeoffs

- Adds complexity to the target matrix.
- Does not eliminate the need for sandboxing and policy boundaries.

## References

- CheriBSD: https://www.cheribsd.org/
- CHERI overview: https://www.cl.cam.ac.uk/research/security/ctsrd/cheri/

See: `docs/163-cheri-capability-lane.md`.
