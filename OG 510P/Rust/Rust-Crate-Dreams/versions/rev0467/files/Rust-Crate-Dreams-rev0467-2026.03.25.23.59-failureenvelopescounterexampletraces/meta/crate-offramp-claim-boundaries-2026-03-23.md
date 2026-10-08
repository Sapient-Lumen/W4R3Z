# Crate off-ramp claim boundaries — 2026-03-23

This note keeps **P-0515 Crate Off-Ramp Pack Kit** from collapsing four different claims into one fake “migration support exists” story.

## Keep these separate

### 1. Successor class is not successor authority
`successor-map.report.json` can say a crate points at a `drop_in_successor`, `partial_replacement`, or `security_only_stopgap`.
That still does not say whether the claim came from:
- maintainer-authored pack data,
- a rustdoc deprecation note,
- a docs page,
- an advisory-driven stopgap,
- or third-party inference.

### 2. Successor authority is not stopgap horizon
A claim can be authoritative and still temporary.
Examples:
- “use crate X for now while Y matures,”
- “pin the last safe version until the replacement lands,”
- “this shim will be removed in the next major release.”

### 3. Declared recipe is not witnessed recipe scope
An `offramp-recipe.manifest.json` is a promise about a migration path.
A `recipe-witness.report.json` is the evidence for what was actually exercised.
Do not let a declared recipe silently become a broad proof.

### 4. Witnessed recipe scope is not broad replacement equivalence
A recipe may be witnessed on one target, one feature set, or one happy-path test.
That does not settle:
- behavior equivalence,
- resource/perf equivalence,
- async/runtime equivalence,
- or all feature/target lanes.

## Working rule

When touching **P-0515**, keep the archive layered as:
1. successor class,
2. successor authority,
3. stopgap horizon,
4. declared recipe,
5. witnessed recipe scope,
6. remaining manual-review boundaries.

Do not rephrase all of that as one generic “deprecation support” or “migration supported” claim.

## Sources

- https://doc.rust-lang.org/reference/attributes/diagnostics.html
- https://doc.rust-lang.org/rustc/lints/listing/warn-by-default.html#deprecated
- https://doc.rust-lang.org/cargo/reference/semver.html
- https://doc.rust-lang.org/cargo/commands/cargo-yank.html
