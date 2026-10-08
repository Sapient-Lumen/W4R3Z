---
id: P-0485
title: Verification Campaign Workbench Kit — multi-tool proof receipts, trust ledgers, policy gates, and verification-drift bundles
status: idea
domains: [verification, safety, testing, miri, kani, creusot, prusti, flux, verus, devtools]
last_reviewed: 2026-03-21
evidence:
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
  - https://rustfoundation.org/safety-critical-rust-consortium/
  - https://github.com/rust-lang/miri
  - https://rust-lang.github.io/rustup/concepts/components.html
  - https://model-checking.github.io/kani/
  - https://model-checking.github.io/kani/reference/experimental/contracts.html
  - https://creusot-rs.github.io/creusot/guide/
  - https://viperproject.github.io/prusti-dev/user-guide/verify/summary.html
  - https://flux-rs.github.io/
  - https://verus-lang.github.io/verus/guide/tcb.html
  - https://verus-lang.github.io/verus/guide/modes.html
---

# P-0485 — Verification Campaign Workbench Kit

**Codename:** `verifycampaign`

**Primary surface:** a crate workspace plus `cargo verify-campaign`.

**Canonical artifact:** `*.verifybundle.zip` built on the `evidencekit` core profile.

## Problem

Rust now has a serious verification substrate, but it is split across materially different lanes:

- **Miri** gives dynamic undefined-behavior evidence over executed programs and tests.
- **Kani** gives model-checking results over proof harnesses, contracts, stubs, and bounded search.
- **Creusot** gives deductive proof workflows over generated verification conditions and prover sessions.
- **Prusti** gives contract-style verification with trusted functions, assumptions, and partial-correctness boundaries.
- **Flux** gives refinement-type checking at compile time.
- **Verus** gives theorem-oriented proof workflows with explicit trusted / external components and spec/proof/exec mode structure.

That is good news.
The remaining pain is not “there are no verification tools.”
The pain is that maintainers and reviewers still lack one boring answer to questions like:

- which obligations were actually checked,
- which evidence kinds were considered acceptable,
- which trust assumptions or external components were in force,
- what policy decided green/yellow/red,
- whether two campaigns are even comparable,
- and what changed in the trust or coverage posture since the last run.

The missing crate is therefore **not another verifier**.
It is a **verification campaign workbench** that keeps raw tool lanes, trust surfaces, policy, and drift analysis reviewable without pretending those lanes mean the same thing.

## Main judgment

A worthy crate contribution here would give other people one honest answer to:

> “What did we verify, with which lane semantics, under which trust assumptions and campaign policy, and how has that campaign changed?”

That answer should be:

- portable,
- diffable,
- explicit about trust,
- explicit about incomparability,
- and narrow enough that another team can review it without re-running every prover.

## What the crate should provide other people

### 1. An obligation inventory
The crate should let teams declare **review objects** instead of relying on informal memory:

- safety preconditions,
- absence-of-overflow requirements,
- panic-freedom expectations,
- aliasing / UB-sensitive invariants,
- API contracts,
- refinement obligations,
- theorem-proof targets,
- and explicit `manual-review-required` obligations.

Each obligation should carry at least:

- a stable `obligation_id`,
- subject path / scope,
- obligation kind,
- accepted evidence classes,
- blocking vs non-blocking posture,
- and review importance.

### 2. Tool-lane receipts with explicit lane semantics
Every imported lane should keep its own semantics explicit.
The crate should normalize results **without flattening them**.

Examples:

- **Miri lane:** dynamic execution, interpreter context, unsupported operations, executed-path scope.
- **Kani lane:** proof harness identity, unwind / solver / stub context, bounded-search posture, counterexamples.
- **Creusot lane:** prover session / replay posture, generated obligations, Why3 context, proof-search results.
- **Prusti lane:** checked properties, trusted functions, assumptions, external specs, partial-correctness boundaries.
- **Flux lane:** refined items, compile-time checking scope, unsupported annotations, package enablement.
- **Verus lane:** verified items, proof mode / exec mode boundaries, external items, trusted assumptions.

Every lane receipt should include a compact `lane_semantics` block such as:

- `evidence_kind` (`dynamic-execution`, `bounded-proof`, `deductive-proof`, `refinement-check`, `theorem-proof`),
- `soundness_scope` (`executed-paths`, `harness-bounded`, `spec-bounded`, `module-bounded`, `proof-bounded`),
- `trust_surface`,
- `unsupported_surface`,
- and `manual_review_required` when the lane cannot sustain a stronger claim.

### 3. A trust ledger
The crate should export one explicit trust ledger covering things that usually get buried in prose:

- trusted functions,
- axioms,
- external specifications,
- proof stubs,
- contract substitutions,
- ignored / externalized modules,
- waivers,
- and manual-review overrides.

Every entry should record:

- stable trust ID,
- kind,
- scope,
- reason,
- owner,
- status,
- introduced-by lane,
- and review due / review note metadata.

### 4. A policy gate
The crate should evaluate campaigns against a declared policy instead of forcing reviewers to mentally reconstruct the rules.

The policy layer should answer:

- which evidence kinds count for which obligations,
- which obligations are blocking,
- which trust items are allowed or forbidden,
- whether new trust surface blocks green,
- whether incomparability downgrades the verdict,
- and what must be manually reviewed.

This yields a small `policy-evaluation.report` rather than “CI passed, probably fine.”

### 5. A comparability / drift report
The crate should make campaign drift explicit:

- tool version changes,
- target or toolchain drift,
- changed trust surface,
- changed obligation inventory,
- changed policy version,
- and changed coverage scope.

If the drift is too large, the crate should say `not-comparable` instead of bluffing a clean diff.

## Why existing tools are not enough

The underlying tools are real and valuable, but they remain **tool-shaped**:

- Miri is a UB detector over executed runs, not a cross-tool assurance ledger.
- Kani is a model checker with harnesses, contracts, and stubs, not a policy/diff workbench.
- Creusot has Cargo and Why3 workflows, including replay, but not a neutral campaign manifest.
- Prusti exposes trusted functions and assumptions, but not a cross-tool trust ledger.
- Flux gives compile-time refinements, but not a shared policy/evidence bundle.
- Verus gives strong proof structure, but not a cross-tool campaign verdict model.

The missing layer is therefore a **receiver-facing support contract above those tools**.

## `0.1` artifact vocabulary

`0.1` should standardize a very small vocabulary:

- `campaign-manifest.json`
- `obligation-record.json`
- `lane-result.json`
- `trust-ledger.json`
- `policy-evaluation.report.json`
- `campaign-diff.report.json`
- `verify-campaign.json`
- `campaign.summary.md`

That is enough to be genuinely useful without inventing a universal verification language.

## Commands worth shipping first

- `cargo verify-campaign init`
- `cargo verify-campaign collect-miri`
- `cargo verify-campaign collect-kani`
- `cargo verify-campaign collect-creusot`
- `cargo verify-campaign collect-prusti`
- `cargo verify-campaign collect-flux`
- `cargo verify-campaign collect-verus`
- `cargo verify-campaign evaluate`
- `cargo verify-campaign diff`
- `cargo verify-campaign bundle`
- `cargo verify-campaign inspect`

## What to import, not reinvent

- raw Miri findings and interpreter context,
- Kani harness / contract / stub context,
- Creusot proof-search and replay facts,
- Prusti trusted-function / assumption facts,
- Flux refinement-check scope,
- Verus trusted/external component facts,
- and the shared bundle substrate from **P-0256 Evidence Bundle Core Kit**.

Do **not** reinvent those toolchains.

## First adopters / users

- unsafe-library maintainers mixing Miri and a proof tool,
- safety-critical teams building reviewable evidence packs,
- verification engineers comparing lane posture across releases,
- platform teams trying to explain why a campaign is green or blocked,
- and consortium / standards-facing groups that need explicit trust and comparability language.

## Success criteria

A good `0.1` release should let another reviewer answer all of the following from one compact bundle:

1. what obligations existed,
2. which lanes contributed,
3. what each lane really meant,
4. which trust assumptions existed,
5. what policy produced the verdict,
6. and whether the new run is actually comparable to the last one.

If the crate can do that honestly, it is already worthy.

## Non-goals

- not a replacement for Miri, Kani, Creusot, Prusti, Flux, or Verus,
- not a universal proof language,
- not an assurance-case authoring system,
- not a hosted prover farm,
- not a claim that all verification lanes are equivalent,
- and not a promise that every campaign diff is comparable.

## Adoption plan

Start with importers for the tool lanes that already expose the clearest machine-readable posture.
Keep the first release small and policy-first.
Make `not-comparable` normal.
Publish tiny scenario bundles that show why dynamic evidence, bounded proof, refinement checks, and theorem-proof lanes must remain separate.

## Maintenance plan

- keep schemas small and versioned,
- treat tool-specific adapters as optional features,
- prefer conservative claim downgrades when adapters lose detail,
- and document lane-specific blind spots instead of smoothing them over.

## Open questions

- Which policy defaults are strict enough to be useful without pretending to be standards guidance?
- How should the crate model obligations that accept multiple evidence classes but require at least one proof-shaped lane?
- Which tool-local outputs are stable enough for direct machine import versus manual summary import?
- How should campaign diffs represent changed trust surface when the raw proof result improved?
