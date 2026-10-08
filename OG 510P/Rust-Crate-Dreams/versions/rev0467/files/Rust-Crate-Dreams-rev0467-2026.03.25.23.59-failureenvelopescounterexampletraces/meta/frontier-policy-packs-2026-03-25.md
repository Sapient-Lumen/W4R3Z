# Frontier policy-pack board — 2026-03-25

This pass keeps the broad frontier stable, but changes what the archive should now ask of the leading lanes:

**Which lane can define a shared policy-and-verdict contract that teams can actually act on after reading the evidence bundle?**

## Main judgment

The next practical build slice should be ranked by **policy leverage**:

1. how directly the lane answers a real adoption or release decision;
2. how cleanly it can consume reviewed bundles and conformance kits rather than raw substrate noise;
3. how well it can expose explainable rule outcomes, override paths, and recheck triggers;
4. and how reusable its verdict vocabulary will be across later lanes.

## Policy leverage board

### 1. P-0509 + P-0536 + minimal P-0535
**Role:** decision-policy front door

Why first under this lens:
- it is already the lane where teams ask “should we adopt or continue with this crate set?”;
- it can now import support bundles, continuity bundles, and lifecycle facts rather than inventing policy from prose;
- and it is the cleanest place to define a first stable verdict vocabulary.

What the crate should provide:
- reusable policy packs for named adopter postures,
- explainable verdict reports with rule-level outcomes,
- override tickets with expiry and review fields,
- and handoff summaries that distinguish evidence from policy.

### 2. P-0472 + P-0484
**Role:** evidence and support input ring

Why second:
- it should still define the shared evidence and conformance vocabulary;
- but under this lens it becomes the main policy input supplier rather than the policy owner;
- its strongest next value is to make policy-ready inputs boring and reliable.

What the crate should provide:
- policy-ready support bundles,
- stable dimension names and claim tiers,
- bundle verification that policy engines can trust,
- and degraded/refused outputs when evidence is insufficient.

### 3. P-0431 + P-0496 + P-0125
**Role:** continuity / parity / supply-chain trigger ring

Why third:
- this ring supplies many of the events that should trigger policy reevaluation;
- mirror parity, boundary drift, and SBOM precursor coverage all change decision posture over time;
- and this lane is the strongest next place to prove that a verdict system can survive release and environment drift.

What the crate should provide:
- trigger-bearing continuity bundles,
- parity and exposure rule inputs,
- override-invalidating change receipts,
- and portable policy recheck hooks.

### 4. P-0486
**Role:** debugger-support policy borrower

Why fourth:
- strong receiver need;
- but its best first move is to borrow the default policy/vocabulary and specialize only where debugger matrices truly require it.

What the crate should provide:
- debugger-suitability verdict reports,
- matrix-specific rule outcomes,
- manual-review escapes for partial coverage,
- and explicit non-claims by debugger, OS, version, and async surface.

### 5. P-0537
**Role:** compile-iteration policy later

Why fifth:
- compile-iteration is highly salient,
- but the first shared verdict doctrine should be proven on adoption/support decisions before it governs speed-path workflows.

### 6. P-0538
**Role:** scenario-heavy semantics lane

Why sixth:
- still highly salient,
- but it should borrow policy doctrine only after its scenario semantics are stable enough to deserve organization-wide verdicts.

## Policy doctrine in one sentence

A worthy crate should increasingly answer **“what decision packet can another team defend, override, and rerun?”** rather than only **“what evidence can this CLI dump?”**

## Promotion rule after this pass

Do not call a lane policy-ready until the archive can name:
1. the reviewed evidence inputs it consumes,
2. the policy pack vocabulary,
3. the verdict states,
4. the override / waiver path,
5. the recheck triggers,
6. and the explicit non-claim boundary.

## Sources

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://doc.rust-lang.org/rustc/target-tier-policy.html
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-semver-checks.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- https://rust-lang.github.io/rust-project-goals/2025h2/pub-priv.html
- https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html
