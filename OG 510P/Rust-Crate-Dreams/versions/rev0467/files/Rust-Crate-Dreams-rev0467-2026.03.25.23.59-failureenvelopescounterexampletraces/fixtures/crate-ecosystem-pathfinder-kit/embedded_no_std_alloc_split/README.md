# Embedded `no_std` baseline with `alloc` split

Simulates a task lane where `no_std`, optional `alloc`, proc-macro tolerance, and host-tool requirements sharply divide the candidate field.
The artifact should make those boundaries explicit instead of burying them in feature tables.

Why this matters:
- embedded teams often need strong negative information: which crates are *not* viable under their floor constraints;
- cargo metadata alone does not explain whether a candidate really fits a `no_std` baseline, an `alloc`-enabled profile, or a host-assisted workflow.

What this scenario should force:
- hard-veto handling for `no_std` and proc-macro/build-script policy
- role coverage that can distinguish “works in `alloc` mode” from “fits the strict baseline”
- a decision summary that records where the starter set intentionally narrows to a stricter environment than the broader ecosystem default
