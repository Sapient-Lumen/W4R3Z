# Store view minimization (hide non-required store paths from builders)

Most Nix-like systems treat the store as globally readable.
That is convenient, but it breaks “treat builders hostile” in multi-tenant scenarios: a build can **read** unrelated store paths (potentially containing proprietary sources or other sensitive material).

DeriveBSD should make **input visibility** a derived, enforceable property:
> a build step can only see the store paths in its declared input closure.

## Why now

This is easiest to bake in at day-0 because it shapes:
- store layout + mount strategy
- sandbox construction
- evidence objects for explainability

## DeriveBSD direction

### 1) Derive a per-step store view

From the Plan, derive a list of required store objects:
- direct inputs
- transitive runtime/build-time dependencies (closure)

Emit:
- `storeview.manifest` (ordered list of store object digests + mount points)
- hash it and bind it into the Plan digest

### 2) Enforce via mount composition

Implementation sketch (FreeBSD-friendly):
- build runs in a **jail root** (or microVM builder)
- only the declared store objects are mounted into the jail (e.g., `nullfs` mounts for each store object directory)
- the *rest* of the store is not present in the jail namespace

This is the same core principle Bazel emphasizes for hermetic actions:
- only explicitly declared inputs enter the sandbox
- no extraneous data crosses the boundary

### 2b) (Optional) Enforce via a virtual view filesystem

Mount-per-input can be expensive for large closures.
As an optimization, DeriveBSD can optionally materialize the per-step view using a sandboxfs-style virtual filesystem (FUSE), backed by the real store, driven directly by `storeview.manifest`.

See: `docs/167-sandboxfs-accelerated-storeviews.md`.

### 3) Make violations visible

- If a build attempts to access missing paths, it should fail loudly (and produce a small `sandbox.violation.json`).
- `derive explain` can say “this artifact was built with storeview X” and show exactly which store objects were visible.

## Relationship to other hardening

- Complements “deny network”: both remove hidden input channels.
- Complements reproducibility checks: if an artifact *only* sees declared inputs, rebuilders have a fair chance.

References:
- Bazel sandboxing rationale (undeclared inputs break correctness): https://bazel.build/docs/sandboxing
- Bazel remote execution sandbox notes (only declared inputs/outputs cross the boundary): https://bazel.build/remote/sandbox
- Nix community discussion on hiding non-required `/nix/store` paths from builds: https://discourse.nixos.org/t/nix-build-hide-non-required-path-in-nix-store/65313
