# Derive unit source / compile receipt / runtime boundary

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** reproducibility, isolation, operability  
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate  

DeriveBSD already knew that component runtime intent should be explicit.
What stayed too fuzzy was the expensive question behind risk 27:

> when a human reviews “how this component runs”, which object actually has authority, which objects are compiled outputs, and where does the source→compiled join live?

This doc fixes that boundary for v0.

See also:
- ADR: `adrs/ADR-0090-derive-unit-source-compile-receipt-and-runtime-boundary.md`
- component-runtime source sketch: `docs/297-component-descriptors-and-compiled-runtime-manifests.md`
- capability-routing stance: `docs/344-derive-unit-manifests-and-capability-routing.md`
- runtime-composition boundary: `docs/485-stratum-stack-and-runtime-composition-boundary.md`
- runtime manifest schema: `docs/33-runtime-manifest-schema.md`

## Accepted boundary

The authoritative human-authored source is:

- `derive.unit`

The authoritative backend-facing launch object is:

- `runtime.manifest`

The evidence-only source→compiled join object is:

- `derive.unit.compile.receipt`

That means:

- reviewers start from `derive.unit`
- compilers emit runnable runtime wiring and launch authority
- `runtime.manifest` stays the launch-time contract rather than a second hand-authored source
- `derive.unit.compile.receipt` preserves the provenance join without becoming policy or launch authority

## Source scope stays tight

`derive.unit` is the runtime contract for one runnable component instance.
It is not an umbrella for arbitrary service config, mutable operator preferences, or hidden policy DSLs.

In v0 it is allowed to express:

- executable identity and argv
- runtime-byte source
- mounts/state/runtime intent
- high-level capability/promises/health/evidence hooks
- diagnostics and trust dependencies that naturally compile into runtime IR

It is not the place to hide unrelated product policy.
That remains in dedicated policy/spec lanes.

## Runtime bytes must be named exactly one way

To keep “what bytes are intended to run?” reviewable, a `derive.unit` must name runtime bytes through exactly one authored field:

- `rootfs` for a single digest-bound tree
- `strata` for ordered multi-origin composition

The source must not try to author both simultaneously.
Single-tree `rootfs` inputs normalize to a compiled `stratum.stack`; explicit `strata` stay explicit.
Either way, the compiler emits one runtime-composition lane instead of letting source semantics fork.

## The compiler owns runnable wiring

`derive.unit` compiles to bounded runtime artifacts such as:

- `stratum.stack`
- `mount.view`
- `preopen.map`
- `devfs.view.plan`
- `authority.budget`
- `runtime.manifest`

This is the critical anti-folklore move:
**only compiled outputs are consumed by launchers and low-level enforcers.**
Humans review the source and the diffs, but the runnable contract is always emitted mechanically.

## `runtime.manifest` must bind back to the reviewed source

`runtime.manifest.runtime_contract` should carry:

- `derive_unit_digest`
- `stratum_stack_digest`
- `mount_view_digest`

That gives incident review and offline verification one compact answer to:

- which reviewed source drove this launch?
- which runtime composition was in force?
- which launch contract was actually handed to the backend?

## `derive.unit.compile.receipt` stays evidence-only

`spec/derive.unit.compile.receipt.schema.json` carries `authority_semantics = derive-unit-compilation-evidence-only`.

The receipt records:

- which `derive.unit` digest was compiled
- whether the source named bytes via `rootfs` or `strata`
- which compiler artifact/profile ran
- which compiled outputs came out

This is exactly enough provenance to support review, incident forensics, and reproducibility without creating a second hidden source of authority.

## Product-shape fit

- **A / fleet host:** reviewers need one small source plus explicit compiled launch/runtime joins; that keeps host authority narrow and auditable.
- **B / workstation:** AppVM/service runtimes still benefit from one reviewed source and one launch contract, instead of per-tool manifest folklore.
- **C / general-purpose OS:** the contract stays useful even when broader compatibility adapters exist, because adapters still compile to the same runtime lane.
- **D / appliance / regulatory:** long-lived audit and rebuildability improve because the source object, compiled launch contract, and provenance receipt all stay separate and digest-bound.

## Why this is the right small hard decision

This does **not** invent a new runtime subsystem.
It only fixes the boundary that reviewers, launchers, and evidence tooling rely on:

- one reviewed human source (`derive.unit`)
- one launch authority object (`runtime.manifest`)
- one evidence-only join receipt (`derive.unit.compile.receipt`)
- one explicit authored runtime-byte choice (`rootfs` xor `strata`)

That is small enough to implement, but high leverage enough to keep the archive from drifting back into “many mini-manifests” folklore.

## Related artifacts

- `spec/derive.unit.schema.json`
- `spec/runtime.manifest.schema.json`
- `spec/derive.unit.compile.receipt.schema.json`
- `spec/examples/derive.unit.web.service.json`
- `spec/examples/runtime.manifest.json`
- `spec/examples/derive.unit.compile.receipt.json`
- `tools/check_derive_unit_contract.py`

Last updated: 2026-03-08r229
