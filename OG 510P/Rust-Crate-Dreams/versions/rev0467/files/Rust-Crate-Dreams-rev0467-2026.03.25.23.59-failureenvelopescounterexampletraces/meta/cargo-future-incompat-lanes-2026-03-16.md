# Cargo future-incompat triage lane boundaries — 2026-03-16

This note keeps **P-0478 Cargo Future-Incompat Triage Kit** from collapsing into every other Cargo warning / upgrade / fix / build-history idea.

## Main boundary

The official Cargo substrate already does three real things:

1. detects future-incompatible warnings in dependencies,
2. stores enough information to recall a report later,
3. and exposes report display / package filtering / frequency controls.

**P-0478** is the missing layer **above** that substrate:

- capture locks,
- owner maps,
- waiver ledgers,
- release-gate reports,
- evidence-source receipts,
- and snapshot diffs across time, branch, and toolchain.

## Keep these lanes separate

### 1. Official Cargo report substrate

This includes:
- detection of future incompatibility warnings,
- live `--future-incompat-report` output,
- `cargo report future-incompat` recall,
- and Cargo config for notification frequency.

That is upstream Cargo behavior, not the missing crate.

### 2. P-0478 — triage memory and release policy

This lane owns:
- snapshot normalization,
- owner assignment,
- waiver expiry,
- release-window status,
- evidence-source receipts,
- and branch/toolchain diffs.

This is the actual missing crate contribution.

### 3. Cargo build-analysis history warehousing

This lane is about:
- timing history,
- rebuild reasons,
- build session ids,
- and performance / invocation history.

Do not flatten that historical build-analysis lane into future-incompat triage.
A future-incompat bundle can *import* run identity, but it is not a general build warehouse.

### 4. Cargo fix / lint-edit orchestration

This lane is about:
- automatic edits,
- multi-pass fix campaigns,
- rollback plans,
- and edit-orchestration receipts.

Future incompatibility triage may point at a likely remediation path, but it does not own edit execution.

### 5. Resolver explanation / dependency-cause analysis

This lane is about:
- why a dependency or feature was selected,
- duplicate-build causes,
- and exactness around resolver reasoning.

Future-incompat triage may consume resolver evidence, but it should not silently become another resolver-explanation crate.

### 6. Dependency-update planning / semver witness work

This lane is about:
- API breakage review,
- public/private dependency migration,
- and dependency update proofs.

Future-incompat triage may include remediation candidates, but those must stay labeled as candidate paths, not full semver or upgrade proof.

## What a worthy P-0478 bundle must be able to say

A good bundle should be able to say:

- “this snapshot came from a live build with `--future-incompat-report`”,
- “this one came from recalling Cargo report id 27 later”,
- “this warning persists but is covered by an active waiver until 2026-05-01”,
- “this release branch now fails because the waiver expired”,
- and “this toolchain upgrade reclassified the finding surface, so manual review is still required”.

That boring honesty is the product.
