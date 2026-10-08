# MSRV lane boundaries — 2026-03-16

This note exists so future passes do **not** flatten all MSRV discussion into one fake “minimum Rust version”.

## Keep these lanes separate

1. **Declared policy lane**
   - what `package.rust-version` and repo policy claim
2. **Resolver policy lane**
   - whether Cargo was effectively using `allow`, `fallback`, or another future policy shape
3. **Active build lane**
   - the toolchain floor for one selected command, target, and feature set that actually got built
4. **Metadata / tooling lane**
   - whether `cargo metadata`, editor tooling, or other non-build commands still require a newer floor
5. **Inactive target-edge lane**
   - dependencies or editions that only show up on targets/features the main build did not activate
6. **Workspace promise lane**
   - whether a lower MSRV is being promised only for selected members (for example libraries) while products or examples float higher

## Working rule

Do not let the archive imply that a green `cargo build` proves a single repo-wide MSRV promise.
A worthy crate in this lane should report:

- what policy was claimed,
- what Cargo policy ran,
- which command family was checked,
- which target and feature profile mattered,
- and which dependency or edition floor actually moved the result.

## Current neighboring proposals

- **P-0036 MSRV Workspace Lab** should own policy receipts, matrix planning, blame, and lane diffs.
- **P-0468 Cargo Resolver Explanation Kit** may explain graph/version choices, but it should not silently swallow MSRV support promises.
- **P-0034 Cargo Update Policy** may influence upgrade policy, but it is not the same thing as MSRV evidence.

## Anti-collapse reminder

Future revisions must not collapse:

- declared `rust-version`,
- active build floor,
- metadata floor,
- inactive target-edge pressure,
- and workspace support promises

into one fake “MSRV result”.
