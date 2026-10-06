# RFC-0062: Runtime blast-radius contract

Status: Draft

## Summary

Define a **runtime blast-radius contract** for microVM launches:
- secure defaults
- explicit opt-ins that increase authority
- a small set of invariants that every backend must enforce

## Motivation

DeriveBSD is hypervisor-centric to reduce runtime blast radius.
But “microVM-first” is not a guarantee unless the runtime has explicit invariants.

We need a contract that:
- prevents accidental privilege expansion
- makes risk-relevant choices explicit (bridging, passthrough, persistence)
- is enforceable by the runtime daemon

## Proposal

Introduce `docs/94-runtime-blast-radius-contract.md` as the canonical definition.
Planning and runtime must reject manifests that violate defaults without policy opt-in.

## Enforcement points

- Plan-time: policy evaluation produces effective constraints and denies forbidden modes.
- Run-time: `derive-vmmd` applies constraints and refuses unsupported fields.

## Non-goals

- defining a full MAC policy model
- solving all side channels (timing, shared CPU caches)

## Open questions

- Should we require a dedicated bhyve user per instance or per tenant by default?
- What minimum set of device models must every backend support?

