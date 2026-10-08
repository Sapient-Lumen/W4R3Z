# Gap: formal verification workflows and proof artifacts

## What is missing
Rust’s formal-methods story has matured enough that the missing piece is no longer “invent the first verifier”.
The ecosystem now has multiple serious lanes:
- Rust’s own project goals are investing in verification-adjacent foundations such as the standard-library verification challenge, contracts in `std`, and `a-mir-formality`.
- Safety-Critical Rust is now an explicit roadmap area tied to evidence-heavy adoption.
- Tool authors already provide distinct verification workflows: `cargo kani`, `cargo creusot prove`, `cargo prusti`, and Verus’ specification-first proof style.
- The Rust Foundation is explicitly expanding the verification ecosystem around ESBMC and aiming for backend alignment with Kani.

Sources:
- https://rust-lang.github.io/rust-project-goals/2024h2/std-verification.html
- https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
- https://rust-lang.github.io/rust-project-goals/2025h2/a-mir-formality.html
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://rustfoundation.org/media/expanding-the-rust-formal-verification-ecosystem-welcoming-esbmc/
- https://model-checking.github.io/kani/usage.html
- https://creusot-rs.github.io/creusot/guide/
- https://viperproject.github.io/prusti-dev/user-guide/basic.html
- https://verus-lang.github.io/verus/guide/

## The current seam is still awkward
Today, formal verification in Rust is real but fragmented.
Each backend has its own:
- harness and annotation conventions,
- proof / counterexample output format,
- CI story,
- vocabulary for assumptions, unsupported features, and partial coverage,
- way of expressing “what exactly got proved”.

That means teams can often *run* a verifier, but they still struggle to:
- compare results across tools or across releases,
- attach proof results cleanly to CI and release evidence,
- publish counterexamples in a replayable format,
- state limitations honestly instead of advertising vague “verified” status,
- combine deductive proofs, bounded model checking, and symbolic analyses in one reviewable workflow.

The standard-library verification challenge makes the gap more obvious: upstream now has representative challenge problems, but there is still no shared artifact boundary for recording which properties, backends, assumptions, and outcomes were involved in a given run.

Source:
- https://rust-lang.github.io/rust-project-goals/2024h2/std-verification.html

## Why this matters
Without a common substrate, formal verification remains harder to adopt than it needs to be.
That hurts several strategically important audiences:
1. **Safety-critical and regulated teams** need attachable evidence, scoped claims, and replayable failures.
2. **Library authors** need a sane way to publish proof results without forcing users onto one backend.
3. **Tool builders** need a thinner interop boundary than “scrape each verifier’s bespoke logs”.
4. **Researchers and ecosystem maintainers** need comparable artifacts to track progress on the standard library, unsafe abstractions, and proof-friendly subsets.

Rust’s safety-critical roadmap is increasingly about evidence, qualification, and adoption reality rather than just language marketing. A good proof-artifact layer would directly support that.

Sources:
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/

## What “good” looks like
A worthy ecosystem contribution here is **not** “build one verifier to replace them all”.
It is a shared workflow and artifact layer:
- one `verify-intent/v0` that declares scope, properties, backends, assumptions, and proof budgets;
- one `verify-capabilities/v0` that states what a backend can and cannot currently reason about;
- one `verification-report/v0` that records proved / falsified / unknown / skipped outcomes with reason codes;
- one `counterexample-pack/v0` for replayable failing inputs, traces, and minimization metadata;
- and one `verify-pack/v0` bundle that can be attached to CI, releases, or broader safety evidence packs.

That would make Rust verification much easier to operationalize without flattening the real differences between Kani, Creusot, Prusti, Verus, ESBMC, and future tools.
