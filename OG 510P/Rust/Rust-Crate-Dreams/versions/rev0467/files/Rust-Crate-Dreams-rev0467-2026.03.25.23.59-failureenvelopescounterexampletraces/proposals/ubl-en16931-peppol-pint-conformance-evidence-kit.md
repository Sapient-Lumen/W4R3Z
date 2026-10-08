---
id: P-0323
title: UBL + EN16931 + Peppol/PINT Conformance & Evidence Kit — profile-pinned e-invoice validation, explainable rule failures, and portable trading-partner bundles
status: idea
domains: [commerce, einvoicing, ubl, en16931, peppol, pint, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://docs.oasis-open.org/ubl/UBL-2.4.html
  - https://docs.peppol.eu/poacc/billing/3.0/
  - https://peppol.org/documentation/technical-documentation/post-award-documentation/
  - https://docs.peppol.eu/poac/eu/
  - https://crates.io/crates/faktura
  - https://docs.rs/einvoice
---

# Problem

Rust now has enough e-invoicing and UBL movement that a new XML data model alone is not the highest-leverage contribution. The painful breakages happen at the **document-profile seam**:

- UBL payloads that are schema-valid but business-rule-invalid,
- EN16931 vs BIS vs PINT assumptions getting mixed,
- country and jurisdiction overlays changing underneath trading partners,
- code-list drift that looks like a tiny field problem but becomes a network outage,
- and support tickets that still travel as full invoices, screenshots, and opaque validator dumps.

The worthy crate contribution is a **document-profile conformance and evidence kit** that makes UBL-derived trading documents deterministic, diffable, and explainable across EN16931, Peppol BIS, and PINT surfaces.

# What it provides

- `einvoice-ir` — canonical IR for invoices, credit notes, identifiers, tax breakdowns, monetary totals, line semantics, and profile metadata.
- `einvoice-profile` — lockfiles pinning UBL version, EN16931 assumptions, Peppol BIS release, PINT flavor/jurisdiction, and code-list snapshots.
- `einvoice-verify` — schema, cardinality, code-list, arithmetic, and business-rule verification with explainable findings.
- `einvoice-diff` — semantic diffs: “invoice type code left profile”, “line/tax totals no longer reconcile”, “country overlay now requires field X”, “specification identifier changed profile family”.
- `einvoice-redact` — deterministic redaction and tokenization for supplier/customer identifiers and monetary values where needed.
- `cargo einvoice` — emit `*.einvoicebundle.zip` for partner onboarding, regression suites, and compliance support.

# What the crate should provide other people

1. **Explainable profile failures** instead of “validator says no” logs.
2. **Pinned validation behavior** tied to exact BIS/PINT/code-list snapshots.
3. **Semantic diffs** between invoice versions and profile migrations.
4. **Redactable support bundles** that preserve failure semantics without leaking full documents.
5. **A neutral Rust layer above generation, parsing, and business-app stacks**.

# Persona / who it’s for

- E-invoicing platform teams
- ERP and procurement integrators
- AP/AR middleware vendors
- National/jurisdictional profile implementers
- QA teams maintaining invoice compliance suites

# Users & user stories

- **Platform engineer**: “Tell me why this invoice passed last quarter’s PINT but fails this quarter’s rules.”
- **Integrator**: “Diff our last-known-good invoice against the rejected one in business terms.”
- **Compliance lead**: “Pin the exact rule pack and code lists used for this onboarding run.”
- **Support engineer**: “Redact parties and amounts but keep the arithmetic and code-list failure reproducible.”

# Prior art (and why it’s insufficient)

- OASIS UBL 2.4 keeps the generic business-document substrate current.
- Peppol Billing 3.0 and the growing PINT family provide concrete rule-rich implementation surfaces with frequent release cadence.
- Rust substrate exists in projects like `faktura` and `einvoice`.
- But Rust still lacks a shared **profile lockfile + explainable rule engine + semantic diff + portable evidence bundle** story for real trading-partner support.

# Design goals

1. **Profile-first** — validation without explicit profile pinning is not enough.
2. **Explainability** — findings must map to business terms, rule IDs, and document paths.
3. **Deterministic arithmetic** — totals and tax checks must be reproducible bit-for-bit.
4. **Redaction-first** — make supportable bundles possible for regulated environments.
5. **Additive profile evolution** — new BIS/PINT releases should plug in without rewriting the world.

# MVP surface

- Minimal types: `InvoiceDoc`, `InvoiceProfile`, `RuleFinding`, `InvoiceReport`, `RedactionPlan`
- Minimal functions:
  - `parse_invoice()`
  - `verify_invoice()`
  - `diff_invoice()`
  - `redact_invoice()`
  - `write_bundle()`
- Feature flags:
  - `ubl-2-1`
  - `ubl-2-4`
  - `en16931`
  - `peppol`
  - `pint`
  - `redaction`

# Compatibility story

- Interoperates with UBL XML and rule packs first.
- Targets invoice and credit-note flows before broader procurement documents.
- Intentionally avoids becoming a full AP/AR workflow engine or transport stack.

# Conformance & fixtures

- Golden invoices for schema-valid / rule-invalid / arithmetic-invalid cases.
- Profile migration fixtures across BIS and PINT releases.
- Country/jurisdiction overlay examples.
- Redaction tests that preserve rule reproducibility.

# Path to boring stability

- Freeze IR around invoice/credit-note first.
- Pin code lists and rule packs by content hash, not only release name.
- Prove deterministic arithmetic on a public fixture corpus.
- Add new document families only after the bundle/report format stabilizes.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 26/30**

# Minimum lovable MVP

A validator and diff tool for UBL invoices/credit notes that pins a Peppol BIS or PINT profile, reports explainable rule failures with IDs and business-language hints, and emits a redactable `*.einvoicebundle.zip`.

# De-risk plan

1. Limit MVP to invoice/credit note and a narrow set of currently active profiles.
2. Use existing rule sources and code lists rather than inventing new semantics.
3. Build a deterministic arithmetic core before broad XML feature work.
4. Validate redaction and diffing with a synthetic corpus first.

# Non-goals

- Not a full ERP or e-procurement platform.
- Not a network access point / transport implementation.
- Not a tax-law expert system.

# Architecture & API sketch

```rust
pub struct InvoiceReport {
    pub profile_id: String,
    pub verdicts: Vec<Verdict>,
    pub rule_findings: Vec<RuleFinding>,
    pub arithmetic_findings: Vec<ArithmeticFinding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn verify_invoice(profile: &InvoiceProfile, doc: &InvoiceDoc) -> InvoiceReport;
```

Bundle draft: `profile.toml`, `document.xml`, `normalized.json`, `verdicts.json`, `diff.json`, `rule-trace.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Deterministic redaction for party IDs, addresses, bank accounts, and amounts when requested.
- Guard against XML entity/resource abuse in parsers.
- Preserve enough structure for arithmetic and rule replay after redaction.
- Record exact rule-pack/code-list/profile hashes.

# Maintenance & governance plan

- Ship profile packs as versioned data bundles.
- Keep the IR document-family-neutral but invoice-first.
- Prefer generated rule metadata from official sources where practical.
- Publish synthetic corpora for every supported profile revision.

# Milestones

## 0.1
- Invoice/credit-note IR
- Profile lockfiles
- Explainable rule and arithmetic validation

## 0.2
- Semantic diffing
- Redaction support
- Profile-pack and code-list pinning

## 1.0
- Stable `*.einvoicebundle.zip`
- Multiple active BIS/PINT adapters
- CI-ready regression corpus for partner onboarding

# Open questions

- Should the rule engine be generic enough to cover non-invoice UBL documents later, or invoice-first forever?
- How much XML fidelity belongs in the IR versus normalization layers?
- Can country overlays be represented as composition over a base profile cleanly enough to stay boring?

# Sources

- OASIS UBL 2.4: https://docs.oasis-open.org/ubl/UBL-2.4.html
- Peppol BIS Billing 3.0: https://docs.peppol.eu/poacc/billing/3.0/
- Peppol post-award docs/release table: https://peppol.org/documentation/technical-documentation/post-award-documentation/
- Peppol PINT EU: https://docs.peppol.eu/poac/eu/
- `faktura`: https://crates.io/crates/faktura
- `einvoice`: https://docs.rs/einvoice
