# Cargo Feature Surface Contract Kit — lane boundaries (2026-03-20)

**P-0528** is about the receiver-facing support contract for Cargo features.

It answers questions like:

- Which feature names are public support surface versus internal dependency plumbing?
- Which named combinations are actually supported or tested?
- Which features compose, conflict, or choose one winner?
- Where can resolver or workspace unification behavior still surprise downstream users?

## It is not:

### Not `cfg-availability-ledger-kit`
That lane is about whether items are visible or usable under feature/target/doc conditions.
**P-0528** is narrower and earlier: what the crate’s feature *policy and combinations* mean before a user even reasons about item-level availability.

### Not `cargo-config-layer-receipt-kit`
That lane is about one invocation’s config/include/override basis.
**P-0528** is about feature declarations, feature classes, supported combinations, and unification risk.

### Not `msrv-workspace-lab`
That lane is about Rust-version support policy and lockfile/command floors.
**P-0528** is about feature activation/support truth.

### Not `crate-upgrade-pack-kit`
That lane is about moving from release N to N+1.
**P-0528** may feed upgrade notes when defaults or feature policies change, but it is not itself the migration pack.

### Not `cargo-resolver-explanation-kit`
That lane explains why a dependency/version/feature resolution happened.
**P-0528** is the crate-authored contract above that explanation layer: what support surface and risk posture another team should infer from it.

### Not `cargo-hack` / `cargo-feature-combinations`
Those tools help run combinations.
**P-0528** turns observed combinations into a maintained support contract with profile names, conflict policy, and unification warnings.

### Not `cargo hakari`
`cargo hakari` helps unify workspace features for faster builds.
**P-0528** keeps that build-optimization choice from masquerading as universal downstream support truth.
