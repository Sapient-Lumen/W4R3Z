# Store view minimization: performance & caching

Store view minimization improves security by ensuring each build step only sees its declared inputs.

This document acknowledges and addresses the operational costs.

## Costs

Per-step view composition (e.g., nullfs mount sets) can be expensive:

- many mount operations per derivation step
- large input closures imply large mount sets
- high-churn graphs amplify the overhead

## Mitigations

### 1) View pooling

Treat a store view as a content-addressed object:

- key: `H(sorted(storepaths) || view_policy || mount_strategy)`
- result: a reusable, precomposed view (directory tree / mount namespace)

If two steps share the same closure view, reuse it.

### 2) Prefix compaction

Many paths share common prefixes. Maintain a *view index* so that mounting `…/store/abcd-*` can be expressed as:

- mount the store RO
- expose only whitelisted entries via a generated directory of symlinks/hardlinks

This trades mount syscalls for filesystem operations.

### 2b) sandboxfs-style virtual views

Instead of many `nullfs` mounts or a large symlink forest, optionally use a sandboxfs-style virtual filesystem (FUSE) to present the per-step view as a single mount.

This can reduce view creation to “write a mapping file + mount once”, while keeping the visibility invariant unchanged.

See: `docs/167-sandboxfs-accelerated-storeviews.md`.

### 3) Batch composition per subgraph

When policy permits, compose a view per *subgraph* (phase) rather than per tiny step, while still binding the exact view digest into the Plan.

### 4) Instrumentation

Every build should record:

- `storeview.compose_time_ms`
- `storeview.entries`
- `storeview.reuse_hit`

These feed back into planner heuristics.

## Correctness invariant

Optimizations MUST NOT widen visibility:

- reuse must be exact-match on view hash
- subgraph batching must not include non-inputs
