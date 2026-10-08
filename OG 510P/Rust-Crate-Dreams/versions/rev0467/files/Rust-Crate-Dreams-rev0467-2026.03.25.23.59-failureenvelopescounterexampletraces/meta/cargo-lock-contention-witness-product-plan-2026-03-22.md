# Cargo Lock Contention Witness Kit — product plan (2026-03-22)

## Product shape

Deliver **P-0490** as:

1. a library for capture / normalize / classify / explain / diff / pack;
2. a cargo-adjacent CLI for local triage and CI-support bundles;
3. a compact schema family that editors, wrappers, and other tools can import.

## Receiver-facing promise

Given a blocked Cargo workflow, another engineer should be able to tell:

- which roots were actually in play and how their paths were determined,
- which actor command lane actually ran,
- what wait window was directly observed,
- how exact blocker identity is,
- and what each recommended mitigation would cost.

## v0.1 commands

- `cargo contention-witness snapshot`
- `cargo contention-witness doctor`
- `cargo contention-witness attach-session <id>`
- `cargo contention-witness audit-exactness <bundle>`
- `cargo contention-witness explain-costs <bundle>`
- `cargo contention-witness diff <old> <new>`

## v0.1 artifact set

- `cache-root.manifest.json`
- `root-authority.receipt.json`
- `root-sharing.report.json`
- `lock-wait.receipt.json`
- `actor-command-lane.receipt.json`
- `wait-window.receipt.json`
- `wrapper-context.receipt.json`
- `process-role.snapshot.json`
- `evidence-source.receipt.json`
- `exactness.report.json`
- `collision-diagnosis.report.json`
- `mitigation.plan.json`
- `mitigation-cost.report.json`
- `build-analysis-session.link.json`
- `contention-support-bundle.manifest.json`

## v0.1 implementation stance

- Cargo config/env import and rust-analyzer config import first;
- live stderr/process observation as optional-but-important evidence;
- imported build-analysis sessions as supporting context only;
- mitigation output should be conservative and non-mutating.

## Stage 1

Freeze root-authority, actor-command-lane, wait-window, and mitigation-cost vocabularies.
Do not chase process control or cache orchestration.

## Stage 2

Add richer diffing, redaction presets, and editor-specific adapters.

## Stage 3

Add imported upstream lock-layout/version heuristics once those surfaces stabilize more.

## Adoption targets

1. developers using rust-analyzer plus terminal Cargo commands,
2. large workspaces and monorepos,
3. CI/build engineers investigating intermittent blocking,
4. tool authors wrapping Cargo for diagnostics, tests, or codegen.

## 2026-03-22 refinement — package-cache lock modes, residual contention, and outcome diffs now need first-class status

The next implementation step should freeze three more receiver-facing artifacts:

- `package-cache-lock-mode.receipt.json`
- `residual-contention.report.json`
- `mitigation-outcome.diff.json`

### Why

- package-cache work is not one undifferentiated lock class;
- target-dir/build-dir mitigations can leave residual proc-macro/build-script or package-cache surfaces;
- and users need an honest before/after contract, not just a recommendation string.

### v0.1.5 artifact set

Add to the current witness bundle:
- `package-cache-lock-mode.receipt.json`
- `residual-contention.report.json`
- `mitigation-outcome.diff.json` (optional when only one bundle exists)

### Stage ordering update

After root-authority / actor-command-lane / wait-window are frozen, next prioritize:
1. package-cache lock-mode receipt,
2. residual-contention report,
3. mitigation-outcome diff,
4. then only later richer adapters or orchestration.
