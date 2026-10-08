# Doctest Extraction & Support Contract Kit — lane boundaries (2026-03-22)

Proposal: **P-0455 Doctest Extraction & Support Contract Kit**

## This lane owns

- extraction-basis truth for how a reviewable manifest was produced
- extraction of documentation examples into a reviewable manifest
- lineage of post-extraction rewrites or harness injections
- execution-mode truth (standalone / merged / wrapper / compile-only / ignored)
- grouping/comparison honesty across revisions
- per-example support-class reporting
- docs-example posture diffs across revisions
- portable doctest-support bundle shape

## This lane does not own

- full target/emulator runner-profile design (**P-0481**)
- hosted docs.rs parity / sandbox reproduction (**P-0472**)
- API-surface docs coverage review (**P-0476**)
- public item availability and `cfg` visibility semantics (**P-0451**)
- prose-style linting or general docs authoring UX

## Boundary checks future passes should ask

1. Is the hard problem **what authority produced the doctest inventory** or **how a target/emulator runner was configured**?
2. Is the hard problem **what docs.rs did** or **what the example means semantically**?
3. Is the hard problem **missing docs/examples** or **support-class honesty for existing examples**?
4. Is the hard problem **item availability in documentation** or **the example execution contract**?
5. Is the hard problem **trend/comparison honesty for grouped doctests** or a broader coverage / hosted-doc question?

## Failure modes to resist

Do not flatten these into one fake “docs support” verdict:

- docs.rs built successfully
- `cargo test --doc` passed once
- a wrapper runner exists
- the example is visible in rendered docs
- coverage totals improved
- the crate moved to Edition 2024 and doctests now merge

Each of those can be true while extraction basis, rewrite lineage, execution mode, grouping comparability, or support class remains unclear.
