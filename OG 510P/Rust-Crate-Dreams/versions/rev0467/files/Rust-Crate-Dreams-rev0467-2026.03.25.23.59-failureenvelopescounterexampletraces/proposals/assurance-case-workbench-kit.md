---
id: P-0503
title: Assurance Case Workbench Kit — claim/evidence graphs, GSN/SACM exports, and change-impact review packs for safety-critical Rust
status: idea
domains: [safety-critical, assurance, verification, tooling, ci, interoperability, governance]
last_reviewed: 2026-03-21
evidence:
  - https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - https://rustfoundation.org/safety-critical-rust-consortium/
  - https://www.omg.org/spec/SACM/2.3/About-SACM
  - https://www.omg.org/spec/About
  - https://www.faa.gov/about/office_org/headquarters_offices/ang/redac/redac-sas-201503-gsn-community-standard-v1.pdf
  - https://github.com/safeautonomy/WebGSN
  - https://github.com/alan-turing-institute/AssurancePlatform
  - https://github.com/nasa/CertWare
---

# Problem

Rust’s safety-critical story is getting materially more real:

- the Rust Vision work says safety-critical users repeatedly run into a thinning ecosystem once they move beyond prototyping,
- the Rust Foundation’s Safety-Critical Rust Consortium is explicitly trying to develop guidelines, linters, libraries, static analysis tools, and formal-methods support,
- the 2026 Rust project flagships now name **certified tooling, specifications, and evidence for functional safety** as a first-class direction,
- and the standards world already has mature ways to *structure* assurance arguments, notably GSN and SACM.

Rust is also starting to gain real **evidence-producing substrate**:
coverage receipts, verification-campaign bundles, lint profiles, unsafe-audit ledgers, conformance bundles, reproducibility bundles, and safety-contract artifacts.

What is still missing is the boring review layer above them.
Teams still fall back to:

- slide decks,
- spreadsheets,
- screenshots of CI runs,
- hand-edited GSN diagrams,
- and tacit memory about which evidence is still fresh.

That is not a serious ecosystem default.

The missing crate is **not** another verifier, another coverage engine, or another generic diagram editor.
The missing crate is an **assurance-case workbench**:
a library and cargo-adjacent tool that imports Rust-native evidence, links it to explicit claims and assumptions, evaluates conservative status, emits diffable review packs, and optionally exports GSN/SACM-shaped views.

## Main judgment

A worthy crate contribution here would give other people one honest answer to:

> “What claims are being made, which evidence currently supports them, which assumptions and manual reviews remain in force, and what materially changed since the last assurance pack?”

That answer should be portable, reviewable, and explicit about uncertainty.

# What it provides

## 1. A small assurance profile
The crate should start from one compact profile, not a giant certification database.

`assurance-profile.toml` should declare:

- the subject under review,
- claim-pattern libraries in use,
- import adapters and bundle locations,
- redaction policy,
- freshness policy,
- what counts as blocking evidence drift,
- and which export lanes are enabled.

This keeps the product focused on **assembly and review**, not lifecycle-management sprawl.

## 2. A normalized claim graph
The crate should produce a diffable internal graph such as `claim-graph.json` with:

- claims,
- subclaims,
- strategies,
- contexts,
- assumptions,
- justifications,
- evidence references,
- and explicit support edges.

The graph should preserve status semantics in the internal model instead of hiding them inside visualization-only exports.

## 3. An evidence index above imported bundles
The workbench should import evidence from sibling Rust workflows without forcing every tool into one universal schema.

A useful `evidence-index.json` should capture at least:

- imported artifact ID,
- evidence class (`verification-campaign`, `conformance-bundle`, `coverage-receipt`, `lint-profile`, `unsafe-audit`, `spec-reference`, `manual-review-note`, etc.),
- provenance,
- freshness,
- trust level,
- supporting claim IDs,
- and whether the evidence is automated, manual, or assumed.

This is the main missing receiver-facing layer above **P-0256**, **P-0264**, **P-0485**, and other lower-level evidence producers.

## 4. A conservative claim-status report
A good assurance tool should never silently equate “diagram exists” with “claim satisfied”.

`claim-status.report.json` should distinguish states such as:

- `satisfied`,
- `partial`,
- `assumed`,
- `manual-review`,
- `stale`,
- `unsupported`,
- `waived`,
- and `blocked`.

It should also preserve **why** a claim has that state:

- stale evidence,
- missing import,
- unresolved assumption,
- policy block,
- trust-surface increase,
- or manual-review requirement.

## 5. A change-impact diff
The real day-to-day gap is not only creating one assurance pack.
It is answering:

> “What became weaker, fresher, staler, newly assumed, newly waived, or newly blocked between releases?”

`assurance-diff.report.json` should highlight:

- changed claim states,
- new or removed evidence,
- freshness changes,
- changed assumptions or waivers,
- export / redaction drift,
- and top-level blocker deltas.

## 6. A compact review pack
The crate should emit a compact `review-pack/` for humans with:

- unresolved blockers,
- stale evidence summary,
- major assumption ledger,
- import provenance,
- generated exports,
- and a small narrative on “what changed materially”.

A good review pack is more important than a rich editor in the first release.

## 7. Optional standards-shaped export lanes
The internal representation should stay small and Rust-friendly.
But the workbench should be able to export:

- a **GSN-shaped** JSON/tree for common argument visualization workflows,
- and a **SACM-shaped** interchange view for teams that need standards-adjacent handoff.

These are export lanes, not the whole product.

## 8. One portable bundle
The canonical output should be `*.assurancepack.zip`, ideally as an `assurancepack@1` profile over **P-0256 Evidence Bundle Core Kit**.

That keeps deterministic packing, redaction receipts, signatures, and bundle diffing reusable while leaving assurance semantics to the higher layer.

# What the crate should provide other people

1. **A claim/evidence assembly layer** above Rust-native tooling.
2. **A boring interchange story** for suppliers, customers, auditors, and internal review teams.
3. **A conservative status model** that keeps automation, assumption, waiver, and manual review separate.
4. **A change-impact diff** so evidence churn does not silently invalidate the argument.
5. **A bridge** from Rust evidence bundles to standards-shaped assurance practice without pretending to automate certification.

# Persona / who it’s for

- safety-critical Rust teams in automotive, industrial, aerospace, medical, rail, and similar domains
- toolchain and verification engineers who need reviewable evidence handoff
- suppliers shipping Rust components into larger certified systems
- internal safety leads and external assessors reviewing Rust component evidence
- maintainers of adjacent Rust tooling that want to emit artifacts assurance teams can consume

# Users & user stories

- **Component supplier:** “Take our verification-campaign bundle, lint profile, unsafe-audit ledger, conformance bundle, and spec references, and hand our customer one compact pack showing the argument and the evidence behind it.”
- **Safety engineer:** “Show me exactly which top-level claim is still backed only by assumption, stale evidence, or manual review.”
- **Assessor:** “Diff the assurance pack for this release against the previous release and highlight what changed materially.”
- **Tool author:** “Emit evidence in a shape the assurance layer can import, without having to become an assurance-case editor ourselves.”

# Prior art scan (and why it’s insufficient)

## Existing assurance-case standards and tools

- **GSN** is a long-lived notation for structuring assurance arguments.
- **SACM** standardizes a metamodel and graphical notation for structured assurance cases.
- Tools such as **WebGSN**, **AssurancePlatform**, **D-Case Editor**, and **CertWare** show that assurance-case editing, visualization, and interchange already exist outside Rust.

These are important prior art, but they do not give Rust users the missing day-to-day substrate:

- importing Rust-native evidence bundles and receipts,
- preserving evidence freshness and provenance,
- diffing assurance posture across commits and toolchain revisions,
- keeping manual review and assumptions first-class,
- and producing a compact pack shaped for CI, code review, supplier handoff, and assessor prep.

## Existing Rust-side evidence producers

This archive already contains sharper lower layers that should remain separate:

- **P-0433 MC/DC Coverage Workbench Kit**
- **P-0453 Safety Contract Consumer Kit**
- **P-0459 Clippy Safety Profile & Waiver Kit**
- **P-0460 Unsafe Field Invariant Ledger Kit**
- **P-0465 BorrowSanitizer Workflow & Evidence Kit**
- **P-0256 Evidence Bundle Core Kit**
- **P-0264 Rust Conformance Harness Toolkit**
- **P-0485 Verification Campaign Workbench Kit**

Those crates should produce evidence.
They should **not** each grow their own half-baked assurance-case editor.

# Design goals

1. **Evidence-first** — claims should point to concrete imported artifacts, not only prose.
2. **Conservative status model** — `assumed`, `manual-review`, `stale`, and `blocked` must remain first-class states.
3. **Interchange, not lock-in** — GSN/SACM export matters, but the internal schema should stay smaller than the standards.
4. **Diffability** — assurance drift across releases should be reviewable just like API drift.
5. **Human+machine** — the tool should help teams think, not create decorative diagrams detached from evidence.
6. **Import-friendly** — useful even when evidence is produced elsewhere in CI.
7. **Bundle-first** — another person should be able to inspect the result without reverse-engineering the producer pipeline.

# Non-goals

- full certification workflow ownership
- requirements-management databases
- hazard-log lifecycle tooling
- regulator-specific submission workflows
- replacing standards-native editors for advanced authoring
- pretending that a passing assurance pack equals certification

# Architecture & API sketch

```text
assurance-case-core/          # claim graph, status taxonomy, diff model
assurance-case-import/        # import contracts for evidence families
assurance-case-gsn/           # GSN-shaped export lane
assurance-case-sacm/          # SACM-shaped export lane
assurance-case-bundle/        # assurancepack@1 profile on evidencekit
cargo-assurance-case/         # assemble, review, diff, export, redact
```

## Core types

- `AssuranceProfile`
- `ClaimGraph`
- `ClaimNode`
- `EvidenceIndex`
- `EvidenceRef`
- `ClaimStatusReport`
- `AssuranceDiff`
- `ReviewPackManifest`
- `AssurancePack`

## Core functions

- `load_profile()`
- `import_evidence()`
- `build_claim_graph()`
- `evaluate_claim_status()`
- `diff_assurance_packs()`
- `export_gsn()`
- `export_sacm()`
- `write_review_pack()`

## CLI surface

- `cargo assurance-case assemble`
- `cargo assurance-case review`
- `cargo assurance-case diff <old> <new>`
- `cargo assurance-case export --format gsn`
- `cargo assurance-case export --format sacm`
- `cargo assurance-case redact`

# Security / safety model

- Imported receipts are **untrusted input** until parsed, provenance-checked, and freshness-evaluated.
- Manual review notes and assumptions must remain explicit and policy-addressable.
- Export lanes must preserve the fact that evidence may be stale, assumed, or blocked.
- Redaction must avoid silently changing claim meaning; every redacted export should carry a redaction receipt.
- The tool must prefer `blocked` or `manual-review` over optimistic inference when evidence is malformed or ambiguous.

# Conformance & fixtures

The 0.1 fixture family should freeze a small, realistic import surface:

1. `mixed_campaign_and_conformance_import` — top-level claim imports a verification campaign bundle, a conformance bundle, and a manual review note.
2. `stale_verification_campaign_blocks_top_claim` — evidence remains parseable but becomes stale after a toolchain/profile change.
3. `manual_assumption_block` — one unresolved assumption blocks a release claim.
4. `mixed_evidence_pack` — coverage, lint profile, unsafe-audit, conformance, and spec reference evidence coexist.
5. `gsn_export_roundtrip` — internal graph exports to a GSN-shaped representation without dropping status semantics.

Goldens should verify:

- explicit `satisfied` vs `partial` vs `assumed` vs `blocked` states,
- stable diff output when only freshness changes,
- preservation of import provenance and trust level,
- redaction of internal paths and private identifiers,
- and conservative behavior when imported artifacts are malformed or ambiguous.

# Compatibility story

- Should consume bundle/receipt outputs from Rust-native tools without forcing one universal evidence schema.
- Should integrate especially well with **P-0256**, **P-0264**, and **P-0485**, while remaining adapter-driven.
- Should export to standards-shaped representations like GSN and SACM, but keep the internal schema smaller and easier to diff.
- Should preserve provenance for every imported artifact: producer, toolchain, evidence date, freshness status, trust level, and whether the result was automated or manual.

# Path to boring stability

- Stabilize `assurance-profile.toml`, `claim-graph.json`, `evidence-index.json`, `claim-status.report.json`, and `assurance-diff.report.json` before adding rich visual tooling.
- Start with import + link + status + diff + review-pack generation.
- Keep standards-shaped exports optional in 0.x.
- Publish a tiny library of reusable claim patterns for common Rust safety arguments only after the core import/status contracts settle.

# Maintenance & governance plan

- Keep the core schema compact and versioned.
- Maintain only a few high-value import adapters in-tree; keep the rest pluggable.
- Track standards evolution conservatively and treat export adapters as compatibility surfaces, not the whole product.
- Prefer reusable example corpora and scenario packs over a giant built-in editor surface.

# Milestones

## 0.1
- internal profile / claim-graph / evidence-index / claim-status schemas
- import adapters for 2–3 evidence families
- text review pack
- one GSN-shaped export prototype

## 0.2
- assurance diffing
- redaction receipts
- conservative SACM-shaped export lane
- reusable claim-pattern snippets

## 1.0
- stable review-pack schema
- curated example corpus for safety-critical Rust teams
- a documented adapter contract for external evidence producers

# Open questions

- Which minimal claim vocabulary is enough to be useful without becoming a full assurance metamodel?
- How should the tool represent evidence freshness and partial invalidation when only some imported receipts go stale?
- Which export adapter deserves first-class support first: GSN-shaped JSON or SACM-shaped interchange?
- How should the crate record human review and assessor comments without turning into a workflow platform?


## 2026-03-21 product-shape refinement

The archive now has enough lower-layer evidence substrate that **P-0503** should stop reading like a persuasive essay and start reading like a build-shaped support contract.
This pass keeps five more truths explicit:

1. **claim-library basis** — which reusable claim patterns and local argument profiles are actually in force;
2. **import-policy truth** — which evidence classes are admissible, what freshness/trust minima apply, and what becomes manual review;
3. **assumption-ledger truth** — which unresolved assumptions still exist and which top-level claims they block;
4. **review-gate truth** — what keeps a pack green/yellow/red and why;
5. **export-projection truth** — what a GSN/SACM-shaped export preserves, redacts, or cannot faithfully carry.

A worthy `0.1` crate in this lane should therefore provide more than a claim graph and more than a pretty export.
It should also provide one compact `import-policy.receipt.json`, one compact `assumption-ledger.report.json`, one compact `review-gate.report.json`, and one compact `export-projection.receipt.json` so another team can review the pack without reverse-engineering hidden policies.

# Sources

- What does it take to ship Rust in safety-critical?: https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- Rust 2026 flagship goals: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Safety-Critical Rust Consortium: https://rustfoundation.org/safety-critical-rust-consortium/
- Safety-Critical Rust Coding Guidelines: https://github.com/rustfoundation/safety-critical-rust-coding-guidelines
- Structured Assurance Case Metamodel (SACM): https://www.omg.org/spec/SACM/2.3/About-SACM
- GSN Community Standard v1 (FAA mirror): https://www.faa.gov/about/office_org/headquarters_offices/ang/redac/redac-sas-201503-gsn-community-standard-v1.pdf
- WebGSN: https://github.com/safeautonomy/WebGSN
- AssurancePlatform: https://github.com/alan-turing-institute/AssurancePlatform
- CertWare: https://github.com/nasa/CertWare
