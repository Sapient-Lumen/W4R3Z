## rev0415 addendum
Treat this proposal as the proposal-layer expression of the newly explicit **Native Edge Contract** in `design/native-edge-contract-2026Q1.md`.
The epic is now best read as a thin `cargo native-edge` / `native-edge-pack/v0` layer above imported boundary truth, provider/link truth, host-vs-target context, and foreign-build handoffs rather than as a generic “interop tooling” proposal.


# Epic proposal: Native Edge Stack (`cargo native-edge`, `native-edge-pack/v0`)

## One-line thesis
Build a thin Rust companion layer for **mixed-language and native-library adoption** that links **FFI boundary truth**, **native-provider/link truth**, **host/target/build-handoff context**, and **bounded downstream conclusions** into one portable review boundary without pretending one generator, one provider crate, one C++ bridge, or one build system has already won.

## Why this is now worth doing
Rust’s native-adoption story is now strong enough that the missing contribution looks like a **joined product/adoption boundary above the ingredients** rather than one more ingredient:
- the accepted 2025H1 Rust goal **Evaluate approaches for seamless interop between C++ and Rust** explicitly targets adoption inside projects that must use large, rich C++ APIs;
- the 2025H2 **C++/Rust Interop Problem Space Mapping** effort says there are billions of lines of C++ representing enormous value, that rewrites are often infeasible, and that today’s external libraries solve the space in different ways requiring significant end-user investment;
- the July 2025 project-goals update says Rust should evolve toward a **first-class C++ interop story**, while also noting that different groups have different interop needs;
- Cargo’s roadmap issue to **reduce the need for users to write build scripts** names build time, bug risk, and dependency-review scope as reasons to move common build-script uses into more structured surfaces, with `-sys` / FFI territory explicitly remaining relevant;
- the sandboxed build-script goal makes native probing part of the long-term governance problem around determinism and least privilege;
- Cargo’s build-script/reference docs show that `links` is useful but still limited to one package per `links` value with immediate-dependent metadata rather than a broader native-adoption contract;
- the ecosystem already has plural, serious point tools: `system-deps` for declarative system-library intent, `pkg-config` for build-script probing, CXX for a safe Rust/C++ common regime, and `autocxx` for heavily automated use of existing C++ headers.

What is still missing is the **stack-level boundary that says one native-edge subject was reviewed with these boundary artifacts, these provider decisions, this host/target context, these downstream handoff notes, and these bounded conclusions**.

## Working name
- CLI: `cargo native-edge`
- primary artifact: `native-edge-pack/v0`

## Scope
### This epic should own
- native-edge subject identity
- imported `ffi-pack/v0` and `native-pack/v0` references
- host/target/build-handoff context notes
- diffable review points across boundary, provider, and handoff truth
- bounded release / support / audit / external-build handoffs
- integrity checks on aggregate references

### This epic should not own
- a universal Rust ABI
- a universal C++ bridge generator
- a native package manager
- an external-build-system replacement
- a fake one-number “interop readiness” score
- flattening mixed-language adoption, shipped product identity, and safety claims into one schema

## Candidate artifact family
### `native-edge-brief/v0`
Why the subject exists, intended integration lane, supported environments, reviewed scope, and freshness/review status.

### `native-edge-subject/v0`
The exact crate/workspace/release/integration subject, imported `ffi-pack` / `native-pack` references, host/target/toolchain context, external-build lanes in scope, and comparison base.

### `native-edge-pack/v0`
The portable review bundle linking:
- imported `ffi-pack/v0` references
- imported `native-pack/v0` references
- host/target/build-handoff notes
- local waivers, caveats, and integrity metadata

### `native-edge-diff/v0`
What changed between two review points, with separate sections for:
- boundary surface / generated-artifact drift
- provider / lock / link-plan drift
- host/target/toolchain-context drift
- external-build handoff drift
- downstream conclusion drift

### `native-edge-handoff/v0`
Bounded consumer summaries for:
- external build systems
- release review
- support / incident intake
- audit / safety review
- ecosystem atlas / guidance consumers

## Recommended rollout
1. C ABI export lane
2. system-library consumer lane
3. C++ bridge lane
4. external build handoff lane
5. support / audit consumer lane

This should be driven by [`design/native-edge-pilot-program.md`](../design/native-edge-pilot-program.md).

## What makes this epic “epic” rather than incremental
An incremental tool would improve one lane:
- a nicer binding generator,
- a nicer `-sys` helper,
- a nicer CMake bridge,
- or a nicer provider-specific lockfile.

An epic contribution here instead gives Rust one **portable native-edge adoption contract** above those lanes.
That is strategically different because it can:
- make FFI review, native-provider review, and build-handoff review share the same subject boundary;
- let generators, provider crates, and external build systems stay specialized without pretending any one defines the whole adoption story;
- keep boundary truth, provider/link truth, host/target context, and downstream conclusions distinct but linked;
- and give downstream tooling a bounded artifact to import instead of re-scraping `build.rs`, generated headers, package-manager state, CMake glue, and issue-thread archaeology.

## Design principles
- **Boundary truth is not provider truth.**
- **Provider truth is not toolchain-context truth.**
- **Cargo success is not the same as external-build success.**
- **Support/audit conclusions are consumer views, not source truth.**
- **Consumer summaries are lossy on purpose and say so.**
- **The stack remains thin.**

## Success conditions
This epic is succeeding when Rust teams can say:
- “this is the exact mixed-language/native-integration subject,”
- “these are the boundary artifacts and ownership contracts we actually reviewed,”
- “these are the provider locks and link plans that actually shaped the build,”
- “this is the host/target/build-handoff context that mattered,”
- “this is what changed since the prior review,”
- and “this is what external-build, release, support, and audit consumers may safely conclude,”

without inventing a bespoke interop report for every `bindgen`, `cbindgen`, CXX, `autocxx`, `pkg-config`, `system-deps`, `cmake`, or distro-integrated repository.

## Read this with
- `gaps/native-edge-adoption-boundaries-provider-locks-and-build-handoffs.md`
- `design/native-edge-stack.md`
- `design/native-edge-pilot-program.md`
- `design/native-edge-cpp-lane-map.md`
- `design/ffi-boundary-kit.md`
- `design/native-dependency-kit.md`
- `design/build-interop-kit.md`
- `design/cross-toolchain-kit.md`
- `design/support-envelope-kit.md`
- `design/release-truth-stack.md`
