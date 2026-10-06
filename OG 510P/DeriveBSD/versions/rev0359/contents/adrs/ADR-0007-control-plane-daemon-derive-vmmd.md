# ADR-0007: Control plane remains `derive-vmmd`

Status: Accepted

## Context

DeriveBSD needs a minimal authority boundary for launching and managing microVMs.
Existing managers (vm-bhyve, libvirt, etc.) can be integrated via adapters, but DeriveBSD requires a **policy-governed** control plane that can:
- verify artifacts
- enforce policy decisions
- emit structured evidence

## Decision

The primary runtime control plane daemon is `derive-vmmd`.

- External systems are supported as adapters.
- `derive-vmmd` remains the enforcement point for:
  - artifact verification
  - policy decision record enforcement
  - runtime blast-radius contract

## Consequences

- Backends can vary; enforcement semantics remain consistent.
