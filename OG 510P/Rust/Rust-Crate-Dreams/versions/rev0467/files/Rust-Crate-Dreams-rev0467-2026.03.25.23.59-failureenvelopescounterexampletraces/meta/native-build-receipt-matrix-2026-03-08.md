# Native build stack — receipt matrix (2026-03-08)

This note answers a simple planning question for the current frontier:

> **What should each crate hand to other people?**

The native-build stack gets stronger when each proposal has a distinct receiver and artifact bundle.

## Main judgment

The three crates are adjacent, but they should not hand people the same thing.

- **P-0046** gives people a **failure explanation bundle**.
- **P-0059** gives people a **reviewable fixture result bundle**.
- **P-0058** gives people a **support / resolution contract bundle**.

That separation keeps the stack coherent.

## Receiver matrix

### P-0046 — buildscript-ux-kit

Primary receivers:

- end users trying to build a crate,
- CI maintainers triaging failures,
- IDE/tool authors rendering build-script problems.

What they should receive:

- `buildscript-report.json`
- `buildscript-summary.txt`
- `policy-gate.report.json`
- optional `notes.md`

The key promise:

- **one boring answer to “what mattered and what do I try next?”**

### P-0059 — buildscript-testkit

Primary receivers:

- `-sys` crate maintainers,
- reviewers checking `build.rs` drift,
- tooling authors building fixture corpora.

What they should receive:

- `fixture-manifest.toml`
- `buildscript-run.report.json`
- `directives.normalized.json`
- optional `notes.md`

The key promise:

- **one reviewable answer to “did the script still emit the contract we expected?”**

### P-0058 — native-deps-kit

Primary receivers:

- maintainers of native dependency crates,
- downstream consumers trying to satisfy native requirements,
- enterprise/air-gapped teams needing support truth and offline honesty.

What they should receive:

- `native-contract.toml`
- `native-resolution.report.json`
- `backend-attempts.receipt.json`
- `consumer-doctor.txt`
- optional later `consumer-doctor.report.json`

The key promise:

- **one support answer to “what native support was promised, what was tried, and why did this outcome happen?”**

## Scenario matrix for 0.1

### P-0046 first scenarios

1. `pkg_config_missing_lib`
2. `transitive_warning_hidden`
3. `workspace_policy_gate`

### P-0059 first scenarios

1. `fake_pkg_config_missing`
2. `fake_pkg_config_success`
3. `rerun_scope_regression`

### P-0058 first scenarios

1. `links_override_handoff`
2. `pkg_config_then_vendored`
3. `offline_policy_failure`

## Sequence implication

The stack should still be built in this order:

1. **P-0046** — because every later artifact gets better if failure/report vocabulary is already stable.
2. **P-0059** — because fixture outputs should compare normalized concepts, not raw logs.
3. **P-0058** — because the native-contract layer is broadest and benefits most from already having shared report/test vocabulary.

## Anti-drift rule

Future passes should ask, for every new artifact name:

- is this a **failure explanation** artifact,
- a **fixture review** artifact,
- or a **support contract** artifact?

If the answer is “all three”, the archive is probably drifting again.
