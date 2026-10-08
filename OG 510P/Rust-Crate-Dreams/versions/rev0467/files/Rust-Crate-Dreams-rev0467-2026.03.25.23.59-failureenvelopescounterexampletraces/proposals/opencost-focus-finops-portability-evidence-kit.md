---
id: P-0417
title: OpenCost + FOCUS FinOps Portability & Evidence Kit — cost locks, allocation receipts, and explainable cloud-billing diffs
status: idea
domains: [finops, billing, cloud, cost, analytics, portability, evidence]
last_reviewed: 2026-03-06
evidence:
  - https://focus.finops.org/
  - https://focus.finops.org/wp-content/uploads/2025/05/FOCUS-spec-v1_2.pdf
  - https://www.linuxfoundation.org/press/finops-foundation-launches-focus-1.3-to-deepen-cloud-and-saas-billing-transparency-announces-expanded-vendor-support-for-focus-1.2
  - https://opencost.io/docs/
  - https://opencost.io/docs/specification/
---

# Problem

FinOps is no longer a hand-wavy spreadsheet culture. FOCUS now exists as a real cost-and-usage normalization contract, OpenCost exists as a real allocation model for Kubernetes and cloud infrastructure, and provider support for FOCUS keeps expanding.

But teams still lose huge amounts of time at the seam between:

- **provider-native billing exports and the normalized dataset people think they are analyzing**,
- **OpenCost allocation views and finance-facing invoices or contract datasets**,
- **shared-cost allocation policy and the exact transformation that produced a chargeback number**,
- **cost anomaly investigations and the pile of vendor CSVs / SQL notebooks / screenshots they currently rely on**,
- and **multi-provider FinOps portability stories that collapse as soon as a field, currency rule, or allocation assumption drifts.**

The missing Rust contribution is not another cloud-cost dashboard. It is a **portability-and-evidence kit** that pins FOCUS revision, source datasets, allocation rules, currency assumptions, shared-cost policies, and investigation receipts into one boring artifact.

# What it provides

- `focus.lock` — pins FOCUS version, provider export dialect, currency assumptions, contract-vs-usage dataset choices, and normalization policy.
- `allocation-receipt` — records how raw provider costs became team / service / namespace / SKU views.
- `reconcile.diff` — explains why two normalized datasets or OpenCost runs disagree.
- `chargeback-bundle` — portable bundle for finance, platform, and engineering review.
- `cargo finops-evidence` — emits `*.focusbundle.zip` with source manifests, transforms, allocation receipts, and redaction-safe evidence.

# What the crate should provide other people

1. **A boring handoff artifact for cost investigations**.
2. **A stable normalization contract** across provider exports, FOCUS revisions, and OpenCost views.
3. **Explainable diffs for cloud bills** instead of “someone changed the SQL.”
4. **A reviewable allocation layer** for chargeback, showback, and shared-cost policy.
5. **A Rust-native evidence core** that other dashboards, warehouses, and governance tools can build on.

# Persona / who it’s for

- platform-finance / FinOps engineers
- cloud-cost tooling teams
- platform SRE / infrastructure cost owners
- procurement / cloud-governance teams

# Users & user stories

- **FinOps analyst**: “Tell me whether this month-over-month jump is source-data drift, allocation-policy drift, or an actual spend increase.”
- **Platform owner**: “Package the exact cost inputs and allocation assumptions behind this chargeback report.”
- **Auditor / finance reviewer**: “See which values are observed from providers versus inferred or redistributed locally.”
- **Tool builder**: “Consume one stable Rust lockfile instead of every provider’s export quirks.”

# Prior art (and why it’s insufficient)

- FOCUS defines a shared billing-data vocabulary.
- OpenCost defines a Kubernetes/cloud cost allocation specification and implementation.
- Warehouses and BI tools can transform cost data.

What Rust still lacks is a **reviewable artifact layer** that pins provider exports, FOCUS normalization, allocation policy, reconciliation steps, and redaction-safe receipts together.

# Design goals

1. **Version-honest** — FOCUS revision and provider-export dialect must be explicit.
2. **Policy-explicit** — shared-cost and allocation logic must be reviewable, not hidden in notebooks.
3. **Reconciliation-first** — explain why totals diverge across runs and tools.
4. **Finance-safe** — distinguish observed billing facts from derived allocations.
5. **Portable-by-default** — bundle formats should survive tool and vendor churn.

# MVP surface

- Minimal types: `FocusLock`, `ProviderExportReceipt`, `AllocationReceipt`, `ReconcileDiff`, `FocusBundle`
- Minimal functions:
  - `capture_provider_export()`
  - `normalize_focus()`
  - `allocate_shared_costs()`
  - `reconcile_runs()`
  - `write_bundle()`
- Feature flags:
  - `focus`
  - `opencost`
  - `contracts`
  - `currency`
  - `redaction`

# Compatibility story

- Treats FOCUS and OpenCost as sibling contracts, not as one merged ontology.
- Allows offline evidence capture from completed warehouse or billing runs.
- Supports raw provider exports, normalized FOCUS datasets, and allocation overlays.
- Keeps dashboard/rendering layers out of the core.

# Conformance & fixtures

- Goldens for provider-column drift, currency normalization drift, invoice-vs-usage mismatches, and allocation-policy changes.
- Tiny corpora for shared-cost, RI/SP commitment, credit/refund, and multi-currency scenarios.
- Redacted example bundles safe for bug reports and CI.
- Fixtures showing when totals must match exactly and when they are intentionally derived.

# Path to boring stability

- Stabilize the lockfile and reconciliation schema before building adapters for every provider.
- Start with offline bundle generation from existing exports.
- Keep SQL/notebook integrations thin and optional.
- Resist drift into becoming a full FinOps platform.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A Rust library and CLI that pin a provider export plus FOCUS revision, record one allocation policy, emit explainable reconciliation diffs, and package the result as a compact `*.focusbundle.zip`.

# De-risk plan

1. Start with static datasets and offline reconciliation.
2. Treat provider adapters as importers, not the core schema.
3. Pilot with one OpenCost-shaped dataset and one FOCUS-normalized dataset.
4. Add redaction and finance-review notes early.

# Non-goals

- Not a replacement for OpenCost.
- Not a warehouse or BI product.
- Not a cloud billing collector.
- Not a generic accounting ledger.

# Architecture & API sketch

```rust
pub struct FocusLock {
    pub focus_version: String,
    pub provider: String,
    pub export_dialect: String,
    pub currency_policy: String,
    pub allocation_policy_digest: String,
}

pub fn capture_provider_export(path: &std::path::Path) -> Result<ProviderExportReceipt>;
pub fn normalize_focus(raw: &ProviderExportReceipt) -> Result<FocusBundle>;
pub fn reconcile_runs(a: &FocusBundle, b: &FocusBundle) -> ReconcileDiff;
pub fn write_bundle(bundle: &FocusBundle, out: &std::path::Path) -> Result<()>;
```

Bundle draft: `focus.lock`, `source-manifest.json`, `normalized.parquet`, `allocation-receipt.json`, `reconcile.diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Redact account IDs, contract terms, invoice attachments, and custom tags by policy.
- Keep derived allocations distinct from provider-observed billing facts.
- Track sensitive business metadata separately from portable aggregates.
- Support hashed or bucketed identifiers for public bug bundles.

# Maintenance & governance plan

- Track FOCUS revisions explicitly and treat OpenCost mappings as adapters.
- Publish a tiny fixture corpus that captures common allocation disagreements.
- Keep provider-specific quirks in data packs, not in the core schema.
- Avoid vendor-specific product creep.

# Milestones

## 0.1
- `focus.lock`
- provider export receipt
- offline reconciliation bundle writer

## 0.2
- OpenCost allocation receipt adapter
- shared-cost policy diffs
- redacted example corpus

## 1.0
- stable `*.focusbundle.zip`
- compatibility policy for FOCUS revisions
- CI-friendly chargeback approval gates

# Open questions

- What is the smallest useful common denominator between FOCUS-normalized datasets and OpenCost allocation outputs?
- Which allocation policies belong in the portable core versus optional overlays?
- How should contract datasets and invoice evidence be referenced without forcing sensitive data into every bundle?

# Sources

- FOCUS home: https://focus.finops.org/
- FOCUS v1.2 spec PDF: https://focus.finops.org/wp-content/uploads/2025/05/FOCUS-spec-v1_2.pdf
- Linux Foundation announcement for FOCUS 1.3 and vendor support: https://www.linuxfoundation.org/press/finops-foundation-launches-focus-1.3-to-deepen-cloud-and-saas-billing-transparency-announces-expanded-vendor-support-for-focus-1.2
- OpenCost docs: https://opencost.io/docs/
- OpenCost spec: https://opencost.io/docs/specification/
