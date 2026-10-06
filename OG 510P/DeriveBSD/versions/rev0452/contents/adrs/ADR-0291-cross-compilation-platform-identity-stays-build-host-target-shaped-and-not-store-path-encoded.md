# ADR-0291: Cross-compilation platform identity stays build/host/target-shaped and not store-path encoded

- Status: Accepted
- Date: 2026-03-23

## Context

The archive still left one expensive core ambiguity open in `docs/266-open-questions-and-risk-register.md`:

> how should DeriveBSD represent cross-compilation identity, and how do we keep host/target mixing out of closures without turning store paths into platform folklore?

There are three different useful facts in play:

- **build platform** — where the producing tool runs,
- **host platform** — where the produced artifact runs,
- **target platform** — only relevant when the produced artifact is itself a compiler or similar code generator.

FreeBSD’s own source build already models cross-building with distinct `TARGET` and `TARGET_ARCH` knobs rather than one magical ambient string, and `arch(7)` explicitly warns that those names are top-level build inputs rather than general downstream truth. Meanwhile LLVM, GNU-config, and Nix-style ecosystems all expose target-triple/config strings, but those strings are adapter-facing conveniences rather than a uniquely trustworthy authority object.

If DeriveBSD answers this with “just bake the triple into the store path”, two problems follow:

- content-addressed identity stops being purely about bytes and starts depending on naming folklore,
- and platform-safety moves into ad-hoc parsing rules instead of typed policy/closure evidence.

If DeriveBSD answers this with “platform is just some external note”, different failures appear:

- cross-built artifacts can be cached or promoted without their execution role being obvious,
- runtime closure proofs can silently mix build-host tools with host-runtime objects,
- and A/B/C/D inherit cache/debug stories that are difficult to explain or audit.

## Decision

1. **DeriveBSD platform identity is explicit typed metadata, not store-path syntax.**
   Store paths stay content-addressed and digest-first. Platform roles must be carried in typed artifacts, plans, manifests, receipts, and indexes instead of being inferred from path spelling.

2. **The canonical platform-role model is `build_platform`, `host_platform`, and optional `target_platform`.**
   - `build_platform` names where the producing tool executes.
   - `host_platform` names where the produced artifact executes.
   - `target_platform` is only authoritative for compiler/toolchain/code-generator artifacts.

3. **`target_platform` defaults to `host_platform` outside toolchain/compiler lanes.**
   Ordinary deployable artifacts, base sets, workloads, and closures do not need a third independent platform role unless they are themselves code generators.

4. **Target triples and ecosystem-specific selectors stay alias metadata, not the authority object.**
   LLVM triples, GNU config strings, and FreeBSD `TARGET` / `TARGET_ARCH` values may be recorded as adapter aliases for tooling interoperability, but the archive’s authority stays on the structured platform object plus role assignment.

5. **Runtime closure and activation decisions bind `host_platform`, not `build_platform`.**
   Build-only tools may participate in derivation, but they do not become runtime closure authority unless separately declared as host-runtime artifacts.

6. **The first concrete schema cut is helper-first and base-set-wired.**
   The archive introduces helper schemas for structured platform identity and platform roles, and the first concrete artifact updated to use them is `base.set`.

## Consequences

- Store identity remains cleanly content-addressed.
- Cross-building becomes explainable without making path names semantic.
- Runtime promotion/admission can mechanically reject host/target mix-ups by checking `host_platform` at the closure/root boundary.
- Compiler/toolchain artifacts still get the third role they actually need.
- Adapter ecosystems can keep their familiar strings, but those strings stop being hidden authority.

## Why this is narrow enough

This ADR does **not** define every future platform taxonomy.
It does **not** settle emulator/compatibility adapters, foreign-ABI import lanes, or every cache-index field.
It only closes the core ambiguity that blocks coherent specs:

- platform roles are explicit,
- store paths stay digest-only,
- runtime closes over `host_platform`,
- and target triples are aliases, not authority.
