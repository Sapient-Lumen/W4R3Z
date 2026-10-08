# Top-lane policy verdict plans — 2026-03-25

This pass assumes the archive’s frontier remains broadly stable.
The new question is:

**Which leading lanes should define or consume the shared policy-pack and explainable-verdict contract first?**

## 1. P-0509 + P-0536 + minimal P-0535
**Role:** decision and adoption policy front door

Why first:
- it is where teams actually need a decision object;
- it can import support, continuity, and lifecycle bundles rather than infer policy from vibes;
- and it is the best place to make rule IDs, verdict words, overrides, and handoff semantics visible.

What the crate should provide:
- `policy-pack.json` for named adopter postures,
- `verdict-request.json` for bundle evaluation sessions,
- `verdict-report.json` for explainable decisions,
- `override-ticket.json` for temporary exceptions,
- `recheck-plan.json` for expiry and trigger semantics,
- and `policy-explain.md` for human review.

Likely `0.1` package family:
- `policy-frontdoor-core`
- `policy-frontdoor-schema`
- `policy-frontdoor-verify`
- `cargo-policy-frontdoor`
- bounded import adapters for support / continuity bundles

## 2. P-0472 + P-0484
**Role:** policy-ready evidence supplier

Why second:
- it still owns the most reusable evidence/conformance vocabulary;
- but under this lens it should provide the clean inputs policy engines need rather than claim to own the policy layer itself;
- and it is the best place to keep dimensions, basis, and claim tiers boring.

What the crate should provide:
- support bundles with stable field semantics,
- conformance tiers that policy packs can reference,
- verifier results with degraded/refused states,
- and claim summaries that separate hosted imports from local replay.

Likely `0.1` package family:
- `support-envelope-core`
- `support-envelope-schema`
- `support-envelope-verify`
- `cargo-support-envelope`
- bounded docs.rs / rustc / cargo adapters

## 3. P-0431 + P-0496 + P-0125
**Role:** continuity and supply-chain trigger ring

Why third:
- this ring generates many of the events that should invalidate or rerun decisions;
- public-boundary drift, source-parity changes, and coverage gaps are exactly the sort of things policy should react to;
- and this lane is the best next proof that verdicts can carry forward honestly across time.

What the crate should provide:
- trigger-bearing continuity bundles,
- parity and boundary change receipts,
- override-invalidating change classes,
- and portable recheck hooks that downstream policy can import.

Likely `0.1` package family:
- `continuity-core`
- `continuity-schema`
- `continuity-verify`
- `cargo-continuity`
- bounded registry / mirror / boundary adapters

## 4. P-0486
**Role:** debugger-suitability policy borrower

Why fourth:
- strong receiver need,
- but should borrow the shared verdict vocabulary first and specialize only where matrices demand it.

What the crate should provide:
- debugger suitability verdicts,
- rule-level matrix explanations,
- manual-review escapes for incomplete probe coverage,
- and explicit non-claims by debugger / OS / version / async surface.

## 5. P-0537
**Role:** compile-iteration policy later

Why fifth:
- highly salient,
- but best to borrow the first shared decision doctrine after support/adoption lanes make it boring.

What the crate should provide later:
- policy packs for latency budgets and restart ceilings,
- verdict reports for claimed fast paths,
- and explicit degraded/manual states when workflow evidence is incomplete.

## 6. P-0538
**Role:** scenario-heavy concurrency policy later

Why sixth:
- still highly salient,
- but should not define the first shared verdict vocabulary until its scenario semantics stabilize further.

What the crate should provide later:
- scenario-scoped verdicts,
- rule-level semantic explanations,
- manual-review states for unresolved semantics,
- and explicit non-claims around fairness, cancellation, and observation.

## Shared rule after this pass

The archive should now prefer:
- **one shared policy and verdict doctrine**
over
- many barely compatible “recommendation” outputs.

A later lane may specialize the doctrine, but it should not reinvent it without a concrete reason.

## Sources

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://doc.rust-lang.org/rustc/target-tier-policy.html
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-semver-checks.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- https://rust-lang.github.io/rust-project-goals/2025h2/pub-priv.html
- https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html
