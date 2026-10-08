# Frontier salience scan — 2026-03-08 (seventeenth pass)

## Main judgment

This pass **did** add a new top-level proposal:

- **P-0503 Assurance Case Workbench Kit**

The archive already had many proposals that produce safety-relevant receipts.
What it still lacked was a clear crate for turning those receipts into one conservative, diffable, reviewable argument pack.

That is a real missing layer rather than just another domain-specific receipt bundle.

## Ranked frontier after this pass

1. **P-0469 Cargo Rebuild Explanation Kit**
2. **P-0468 Cargo Resolver Explanation Kit**
3. **P-0503 Assurance Case Workbench Kit**
4. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
5. **P-0486 Debuggability Support Contract Kit**
6. **P-0433 MC/DC Coverage Workbench Kit**
7. **P-0453 Safety Contract Consumer Kit**
8. **P-0490 Cargo Lock Contention Witness Kit**
9. **P-0046 buildscript-ux-kit**
10. **P-0465 BorrowSanitizer Workflow & Evidence Kit**

## Why P-0503 is salient

Five current facts make this more than a speculative niche:

- Rust’s safety-critical users explicitly report that ecosystem support thins out once they move beyond prototyping.
- Rust’s 2026 flagship goals now name **certified tooling, specifications, and evidence** as a top-level direction.
- The Safety-Critical Rust Consortium is explicitly trying to build guidelines, tooling, and practices for this space.
- Assurance-case standards already exist (GSN and SACM), so the archive should not pretend the representation layer is invented from scratch.
- The repo already contains strong lower layers for coverage, contracts, lints, and unsafe evidence, which means the missing value has shifted upward into **claim/evidence assembly and review-pack export**.

## What should happen next

The best next passes on this frontier should prefer:

1. import-contract planning between **P-0503** and evidence-producing sibling proposals,
2. tiny assurance fixtures that exercise `satisfied` / `assumed` / `manual-review` / `stale` transitions,
3. conservative GSN/SACM export planning,
4. and one reusable claim-pattern library for common Rust safety arguments.

They should **not** drift into:

- a giant certification workflow suite,
- a raw diagram editor detached from evidence,
- or vague “Rust for regulated industries” platform language.

## Sources

- Rust safety-critical vision post: https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- Rust 2026 flagship goals: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Safety-Critical Rust Consortium: https://rustfoundation.org/safety-critical-rust-consortium/
- Rust Foundation 2025 review: https://rustfoundation.org/2025/
- SACM: https://www.omg.org/spec/SACM/2.3/About-SACM
- GSN Community Standard v1 (FAA mirror): https://www.faa.gov/about/office_org/headquarters_offices/ang/redac/redac-sas-201503-gsn-community-standard-v1.pdf
