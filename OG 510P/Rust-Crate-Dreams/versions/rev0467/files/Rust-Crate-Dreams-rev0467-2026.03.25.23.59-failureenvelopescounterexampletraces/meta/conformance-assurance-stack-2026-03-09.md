# Conformance → evidence → assurance stack — 2026-03-09

This note exists to stop future passes from flattening three different missing layers into one vague “testing/certification” idea.

## Main judgment

Rust now has enough substrate that the missing value is increasingly a **stack**:

1. **P-0264 Rust Conformance Harness Toolkit** — stable suite/case/result contracts and shareable `*.conformbundle.zip` artifacts.
2. **P-0256 Evidence Bundle Core Kit** — deterministic packing, redaction, signing, diffing, and shared bundle semantics.
3. **P-0503 Assurance Case Workbench Kit** — claim/evidence assembly, conservative status, and review packs.

These layers should cooperate, but they should not be collapsed.

## Why this matters now

- Rust already has custom-harness substrate in Cargo, nextest, `libtest-mimic`, and data-driven harness patterns.
- Rust’s 2026 goals now explicitly include **better test tooling** and **certified tooling, specifications, and evidence for functional safety**.
- The safety-critical Rust conversation is no longer hypothetical enough to treat evidence handoff as an afterthought.

So a good archive pass should ask whether the missing crate is:

- a reusable **suite/runner contract**,
- a shared **bundle substrate**,
- or a higher-layer **assurance review workbench**.

## Working rule

When a domain proposal says “interop”, “conformance”, “validation”, or “certification”, force it to answer three separate questions:

1. what is the **stable case/suite contract**,
2. what is the **portable evidence artifact**,
3. and what is the **higher-layer review or argument surface**, if any.

If a proposal cannot answer all three, do **not** let it silently claim all three.

## Practical layering guidance

### Conformance layer
Best for:
- case discovery,
- execution,
- capability gates,
- environment receipts,
- failing-case bundles,
- cross-implementation comparison.

Should **not** pretend to prove a larger assurance claim by itself.

### Evidence bundle layer
Best for:
- deterministic packing,
- redaction,
- signing,
- semantic diffing,
- profile registration.

Should **not** invent domain-specific verdicts that belong to a suite or assurance graph.

### Assurance layer
Best for:
- claims, assumptions, strategies, and contexts,
- freshness and provenance across multiple evidence families,
- conservative “satisfied / assumed / stale / unsupported / manual-review” status,
- GSN/SACM-shaped export,
- review packs and change-impact diffs.

Should **not** turn into the execution engine for every protocol suite.

## False gap patterns to avoid

1. “We need certification support” when the real missing layer is just a **stable conformance bundle**.
2. “We need a new harness” when the sharper missing layer is **shared bundle semantics** above existing harness substrate.
3. “We need GSN export” when the real problem is still **case IDs, capability tags, and honest environment receipts**.
4. “A conformance run passed, therefore the assurance claim is satisfied” when the sharper result is just **one evidence import lane**.

## Best next archive moves in this stack

1. Add concrete fixture/schema stubs to **P-0264**.
2. Keep **P-0256** as the shared bundle substrate rather than letting every lab/tool invent a private zip grammar.
3. Expand **P-0503** only through conservative import adapters and review-pack vocabulary, not through workflow-platform sprawl.

## Sources

- https://doc.rust-lang.org/cargo/commands/cargo-test.html
- https://nexte.st/docs/design/custom-test-harnesses/
- https://nexte.st/docs/machine-readable/junit/
- https://docs.rs/libtest-mimic/latest/libtest_mimic/
- https://docs.rs/datatest-stable
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://rustfoundation.org/safety-critical-rust-consortium/
- https://www.omg.org/spec/SACM/2.3/About-SACM
