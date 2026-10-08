# Cargo script lane boundaries — 2026-03-16

This note exists to keep the archive honest now that cargo script is close to stabilization and single-file package semantics are explicit in official docs.

## The main split

A single-file package can now be a real Cargo input surface.
That does **not** mean every adjacent Cargo support problem belongs in the same crate.

## Lane 1: single-file package portability / handoff

**Proposal:** `P-0435 Cargo Script Workbench Kit`

This crate should own:

- inferred-versus-explicit frontmatter truth,
- target-dir and lockfile location for single-file packages,
- manifest-command / shebang invocation receipts,
- portability doctor findings,
- and conservative export plans for turning one-file packages into normal packages.

The central question is:

> “What exactly did Cargo infer for this one-file package, and how do I hand it to someone else honestly?”

## Lane 2: workspace membership and parent probing

**Proposal:** `P-0506 Cargo Workspace Boundary Doctor Kit`

This crate should own:

- parent-manifest probing,
- workspace membership diagnosis,
- cwd versus `--manifest-path` boundary splits,
- and config-probe traces.

The central question is:

> “Why did Cargo think this project belonged to *that* workspace/config boundary?”

Single-file packages can touch this lane, but **P-0435** should not become the universal workspace doctor.

## Lane 3: source roots, vendoring, and mirror parity

**Proposal:** `P-0496 Cargo Vendor & Source Parity Kit`

This crate should own:

- logical source IDs,
- replacement chains,
- offline/mirror coverage,
- and source parity / verification-import truth.

The central question is:

> “What source identities and trusted roots did this build really use?”

This is different from P-0435 even if a one-file package happens to download dependencies.

## Lane 4: broader project support surface

**Proposal:** `P-0484 Toolchain & Target Support Contract Kit`

This crate should own:

- toolchain-support posture,
- target support contracts,
- contributor setup drift,
- and support-surface reports.

It should not absorb one-file package export plans or frontmatter inference.

## Working rule

When a future pass touches cargo script, it must state explicitly whether the new value is about:

1. **single-file package inference / portability**,
2. **workspace/config discovery**,
3. **source parity / offline truth**,
4. or **broader project support posture**.

Do not let the archive flatten these into one vague “Cargo script support” bucket.
