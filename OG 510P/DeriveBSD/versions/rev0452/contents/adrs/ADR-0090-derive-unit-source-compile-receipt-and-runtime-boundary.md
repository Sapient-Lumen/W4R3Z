# ADR-0090: Derive unit source / compile receipt / runtime boundary

- Status: Accepted
- Date: 2026-03-08

## Context

Risk 27 identified an expensive ambiguity in the archive:
DeriveBSD already had `derive.unit`, `svcdb`, `preopen.map`, `mount.view`, `devfs.view.plan`, `authority.budget`, and `runtime.manifest`,
but it did not say crisply which object was the reviewed source, which objects were compiled runtime outputs, and where the source→compiled provenance join should live.

If left fuzzy, teams would drift toward one of two bad outcomes:

1. `runtime.manifest` or other compiled outputs become hand-authored shadow sources.
2. different teams invent bespoke component/runtime mini-manifests that silently widen authority.

The archive already had a strong precedent in ADR-0085 for frontend-source vs compiled-authority boundaries.
We apply the same discipline here to component runtime intent.

## Decision

1. `derive.unit` is the authoritative human-authored source for one runnable component runtime contract.

2. `derive.unit` must name runtime bytes through exactly one authored field:
   - `rootfs`, or
   - `strata`

   A single-tree `rootfs` source normalizes to a compiled `stratum.stack`; explicit `strata` remain explicit.

3. Compilers emit the runnable runtime lane.
   `runtime.manifest`, `stratum.stack`, `mount.view`, `preopen.map`, `devfs.view.plan`, `authority.budget`, and similar low-level artifacts remain compiled outputs rather than primary hand-authored config.

4. `runtime.manifest` remains the backend-facing launch authority object.
   Its `runtime_contract` must bind back to:
   - `derive_unit_digest`
   - `stratum_stack_digest`
   - `mount_view_digest`

5. `derive.unit.compile.receipt` is evidence-only.
   It records:
   - source `derive.unit` digest
   - source runtime mode (`rootfs` or `strata`)
   - compiler artifact/profile
   - compiled output digests

   The schema carries `authority_semantics = derive-unit-compilation-evidence-only`.

6. `derive.unit` scope stays narrow: runtime contract only.
   It must not become the dumping ground for arbitrary mutable service config or unrelated product policy.

## Consequences

- reviewers have one clear starting point for “how this component runs”
- launchers still consume machine-emitted runtime contracts instead of trusting hand-authored low-level manifests
- source→compiled provenance becomes explainable without turning evidence into authority
- A/B/C/D can share one runtime-authoring model without product-shape forks

## Why this is narrow enough

This ADR does not redesign service supervision, capability routing, or launch backends.
It only fixes the source / compiled-output / evidence join boundary and one source-scope rule (`rootfs` xor `strata`).

That is a small but high-leverage decision with clear implementation consequences and low archive-entropy cost.
