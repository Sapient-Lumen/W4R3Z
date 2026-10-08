# Verification campaign boundaries — 2026-03-09

This note exists to stop future passes from flattening Rust verification into one fake “proof status” layer.

## Main judgment

**P-0485 Verification Campaign Workbench Kit** should be read as a stack:

1. **tool-local lane receipts** — raw results from Miri, Kani, Creusot, Prusti, Flux, Verus, and similar tools,
2. **campaign inventory / trust / policy** — the shared layer that says which obligations matter, which evidence classes count, and whether the campaign is green,
3. **bundle substrate** — deterministic packaging, redaction, signing, and diffing from **P-0256 Evidence Bundle Core Kit**,
4. **assurance import** — optional higher-layer review or claim assembly from **P-0503 Assurance Case Workbench Kit**.

These layers should cooperate, but they should not be collapsed.

## Why this matters now

Rust now has enough verification substrate that the missing value is not merely “another verifier”.
It is often the boring layer that answers:

- what obligations were checked,
- which lane semantics apply,
- which trust assumptions exist,
- what policy allowed or blocked green,
- and whether two campaigns are comparable at all.

That is especially timely because Rust’s 2026 goals explicitly call out certified tooling, specifications, and evidence for functional safety, while the broader safety-critical Rust conversation says evidence and process demands rise sharply with criticality.

## Working rule

When a proposal touches Rust verification, force it to answer five separate questions:

1. what is the **tool-local receipt**,
2. what is the **campaign obligation/trust model**,
3. what is the **campaign policy gate**,
4. what is the **portable bundle substrate**,
5. and what is the **higher-layer assurance consumer**, if any.

If the proposal cannot answer all five, do **not** let it silently claim all five.

## Comparability rule

Verification campaigns must preserve at least these comparability dimensions:

- tool and version,
- target/toolchain context,
- evidence kind,
- soundness or scope boundary,
- trust surface,
- policy version.

If those dimensions drift too far, the crate should say `not-comparable` or `partially-comparable` instead of printing a misleading diff.

## False gap patterns to avoid

1. “We need another verifier” when the sharper missing layer is the **campaign workbench** above existing tools.
2. “This tool says proved, therefore the campaign is green” when the missing layer is actually the **policy gate**.
3. “These two reports can be diffed” when the underlying lanes or trust surfaces changed enough that they are **not honestly comparable**.
4. “Once it is in a verify bundle it is certification-ready” when the sharper result is only **portable evidence**, not an assurance claim.

## Best next archive moves in this stack

1. Freeze lane-semantics and policy vocabulary for **P-0485** before expanding adapter count further.
2. Keep **P-0256** as the shared bundle substrate rather than inventing a private verification zip grammar.
3. Let **P-0503** consume campaign bundles conservatively instead of flattening their lane semantics.

## Sources

- https://github.com/rust-lang/miri
- https://model-checking.github.io/kani/
- https://creusot-rs.github.io/creusot/guide/
- https://viperproject.github.io/prusti-dev/user-guide/verify/summary.html
- https://flux-rs.github.io/
- https://verus-lang.github.io/verus/guide/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
