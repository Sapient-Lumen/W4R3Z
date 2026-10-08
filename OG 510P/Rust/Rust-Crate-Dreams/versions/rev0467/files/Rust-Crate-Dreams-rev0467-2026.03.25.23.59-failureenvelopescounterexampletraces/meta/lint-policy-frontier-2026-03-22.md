# Lint-policy frontier — 2026-03-22

The archive already had lint-adjacent proposals, but the current Rust/Cargo substrate now makes one sharper shared frontier visible.

## Current stack

1. **P-0459 Clippy Safety Profile & Waiver Kit**
   - Owns the reviewable contract layer for:
     - policy authority,
     - checked scope,
     - diagnostic channel,
     - waiver decisions,
     - and lint-policy drift.
2. **P-0473 Cargo Lints Adoption Receipt Kit**
   - Owns workspace rollout, package inheritance, and staged adoption around Cargo manifest lint policy.
   - Use this when the hard problem is workspace rollout and inheritance cleanup more than safety-review evidence.
3. **P-0042 Cargo Future-Incompat Triage Kit**
   - Owns future-incompatibility triage and migration surfaces.
   - Use this when the hard problem is compiler/Cargo forward-compat warnings, not the current lint contract.
4. **P-0120 Unsafe Contract Auditor Kit**
   - Owns broader unsafe obligations and witness fidelity.
   - Use this when the hard problem is unsafe evidence overall, not lint policy posture.
5. **P-0455 Doctest Extraction & Support Contract Kit**
   - Owns documentation-example support.
   - Use this when the hard problem is docs execution support rather than lint policy.

## Shared judgment after this pass

The strongest missing crate in this sub-frontier is not another lint engine and not another quality dashboard.
It is a **policy-and-waiver evidence layer** that lets maintainers, reviewers, adopters, and auditors inspect what a lint claim really means in practice.

## Design guardrails

When working in this frontier, keep these truths separate:

1. **authority truth** — where the effective lint level came from;
2. **scope truth** — what packages / features / targets / tests / private-item surfaces were actually checked;
3. **channel truth** — which findings came from stable rustc/Clippy versus nightly Cargo linting;
4. **waiver truth** — which exceptions exist, who owns them, and when they expire;
5. **drift truth** — what changed across revisions.

Do not let any of the following stand in for an honest lint-policy answer:

- “we run `cargo clippy` in CI”
- “the root workspace forbids `unsafe_code`”
- “there are no warnings on this branch”
- “the waiver is documented in the PR”
- “nightly found more issues so we are stricter now”

Those are useful signals, not a full lint-policy contract.
