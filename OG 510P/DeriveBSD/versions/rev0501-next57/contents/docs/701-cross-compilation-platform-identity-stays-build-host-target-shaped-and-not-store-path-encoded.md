# Cross-compilation platform identity stays build/host/target-shaped and not store-path encoded

**Tier:** A (Core)  
**Profiles:** A, B, C, D  
**Pillars:** reproducibility, supply-chain, operability  
**Patterns:** Plan→Apply→Receipt, Adapter→Shadow→Replace

The archive had one remaining expensive ambiguity near the core store/closure boundary:

> do we encode cross-compilation identity into store paths, or do we keep store identity purely content-addressed and carry platform truth somewhere else?

This page closes that question.

See also:
- ADR: `adrs/ADR-0291-cross-compilation-platform-identity-stays-build-host-target-shaped-and-not-store-path-encoded.md`
- store basics: `docs/03-store.md`, `docs/56-store-layout-and-digests.md`
- closure proof: `docs/90-closure-proof.md`
- base sets: `docs/526-derived-base-sets-and-pkgbase-adapter-boundary.md`
- optional cross-compilation wedge: `docs/398-zig-toolchain-wedge-and-cross-compilation.md`
- helper specs: `spec/platform.identity.schema.json`, `spec/platform.roles.schema.json`

## Accepted boundary

### 1) Store paths stay digest-only

DeriveBSD keeps the store-path rule simple:

- `/derive/store/<digest>-<name>/...`
- digest is authoritative
- name is a human hint only
- platform identity is **not** encoded into the path spelling

This preserves the archive’s content-addressed center.
A path is about bytes, not about a parser remembering how some ecosystem happened to spell a target triple.

### 2) Platform roles are explicit typed data

The canonical role model is:

- `build_platform`
- `host_platform`
- optional `target_platform`

These roles mean exactly what established cross-build practice already implies:

- `build_platform`: where the producing tool executes
- `host_platform`: where the produced artifact executes
- `target_platform`: only for compiler/toolchain/code-generator artifacts that emit code for some later platform

The archive now treats those roles as first-class typed metadata rather than ambient build variables or store-path folklore.

### 3) target triples are aliases, not authority

LLVM triples, GNU-config strings, and FreeBSD `TARGET` / `TARGET_ARCH` pairs are still useful.
They are how real toolchains and adapters talk.
But they do **not** become the archive’s authority object.

Why not?
Because they solve different interoperability problems and are not one perfect universal identity:

- FreeBSD itself already splits platform knobs across `TARGET` and `TARGET_ARCH`
- LLVM uses triple-shaped target strings
- GNU-config style strings are historical compatibility selectors rather than a uniquely canonical platform identity

So DeriveBSD records those values as **aliases** under the structured platform object when useful, while keeping review/policy/closure decisions on the typed fields and explicit role assignment.

### 4) Runtime closure and activation bind `host_platform`

The archive’s anti-mixing rule is now crisp:

- build-time tools belong to derivation/evidence
- runtime closure authority belongs to `host_platform`
- activation/launch must verify that the closure root’s `host_platform` matches the consuming environment unless an explicit compat/emulation adapter says otherwise

This is the first concrete answer to “how do we stop accidental host/target mixing?”
We do it by making the execution role explicit at the artifact/closure boundary, not by overloading store paths.

### 5) `target_platform` defaults to `host_platform` outside toolchains

Most deployable artifacts do **not** need three independent platform roles.
For ordinary packages, base sets, system images, host generations, and workload bundles:

- `build_platform` may differ from `host_platform`
- `target_platform` is omitted unless the artifact is itself a compiler/toolchain/code generator
- consumers should read omitted `target_platform` as “same as host” rather than inventing a third hidden default

That keeps the common case small while preserving the real third role where it matters.

## First concrete spec cut

The archive now introduces two helper schemas:

- `spec/platform.identity.schema.json`
- `spec/platform.roles.schema.json`

And the first concrete artifact updated to use them is:

- `spec/base.set.schema.json`

That is enough to make the decision implementation-shaped without pretending every older schema must be rewritten in one pass.

## Why this is the right A–D decision

- **A / fleet host:** builders and promotion systems can cross-build for multiple fleets without turning cache names into hidden policy.
- **B / workstation:** human explain/support surfaces can tell “built on X, runs on Y” directly instead of reverse-engineering path strings.
- **C / general-purpose OS:** broad package ecosystems and foreign-arch builder pools remain viable, but the core closure/admission logic stays typed and auditable.
- **D / appliance / regulatory:** exported evidence can prove exactly which platform role mattered at build time versus runtime, which is better for long-lived audits than a store-path convention.

## Small hard decisions made here

This page intentionally decides a few things and leaves the rest open.
It decides:

- store paths stay digest-only
- platform identity is typed data
- platform roles are `build_platform` / `host_platform` / optional `target_platform`
- runtime closure/admission keys on `host_platform`
- target triples stay aliases rather than authority

It does **not** decide:

- every future platform taxonomy field
- emulator/compatibility adapter semantics
- every cache-index projection
- every older schema migration timeline

That is the right cut for getting from archive prose to buildable specs.

## Related docs

- `adrs/ADR-0291-cross-compilation-platform-identity-stays-build-host-target-shaped-and-not-store-path-encoded.md`
- `docs/03-store.md`
- `docs/56-store-layout-and-digests.md`
- `docs/90-closure-proof.md`
- `docs/526-derived-base-sets-and-pkgbase-adapter-boundary.md`
- `docs/398-zig-toolchain-wedge-and-cross-compilation.md`
- `spec/platform.identity.schema.json`
- `spec/platform.roles.schema.json`
- `spec/base.set.schema.json`

## References

- FreeBSD `build(7)` / `arch(7)` cross-build variable model: https://man.freebsd.org/build and https://man.freebsd.org/arch%287%29
- Nix cross-compilation roles (`buildPlatform`, `hostPlatform`, `targetPlatform`) and config-string caveats: https://nix.dev/tutorials/cross-compilation.html and https://nixos.org/manual/nixpkgs/stable/
- Clang target triples (`--target=`) as tooling-facing selectors: https://clang.llvm.org/docs/UsersManual.html

Last updated: 2026-03-23r432
