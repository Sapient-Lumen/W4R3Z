# Cargo Script Workbench Kit — product plan (2026-03-22)

## Product shape

Deliver **P-0435** as:

1. a library for capture / normalize / classify / explain / diff / pack;
2. a cargo-adjacent CLI for local repro capture, portability review, and export planning;
3. a compact schema family that issue templates, CI jobs, editors, and docs pipelines can import.

## Receiver-facing promise

Given a single-file Cargo package, another engineer should be able to tell:

- what frontmatter was explicit versus inferred or rejected,
- what workspace/config discovery rules applied,
- how Cargo interpreted the invocation,
- where target-dir and lockfile state actually lived,
- and how to export the script into a normal package without losing intent.

## v0.1 commands

- `cargo script-workbench capture <path>`
- `cargo script-workbench doctor <bundle>`
- `cargo script-workbench explain-inference <bundle>`
- `cargo script-workbench diff <old> <new>`
- `cargo script-workbench export-plan <bundle>`
- `cargo script-workbench pack <bundle>`

## v0.1 artifact set

- `frontmatter-authority.receipt.json`
- `discovery-scope.receipt.json`
- `invocation-interpretation.receipt.json`
- `cache-residency.receipt.json`
- `script-manifest.view.json`
- `script.receipt.json`
- `script-doctor.report.json`
- `script.lock.json`
- `export-lineage.plan.json`
- `script-support-bundle.manifest.json`

## v0.1 implementation stance

- parse single-file-package frontmatter and classify explicit/defaulted/rejected fields first;
- import Cargo config-root / invocation information conservatively;
- keep advisory portability findings separate from hard Cargo semantics;
- export planning should be conservative and non-mutating.

## Stage 1

Freeze frontmatter-authority, discovery-scope, invocation-interpretation, cache-residency, and export-lineage vocabularies.
Do not chase full editor integration or package synthesis yet.

## Stage 2

Add portability diffing, redaction presets, and issue-template / CI adapters.

## Stage 3

Add richer export helpers once workspace/config discovery semantics stabilize further upstream.

## Adoption targets

1. developers sharing minimal reproducers,
2. educators and tutorial authors,
3. CI or docs pipelines that execute single-file examples,
4. maintainers converting “one-file bug scripts” into ordinary packages for long-lived fixes.
