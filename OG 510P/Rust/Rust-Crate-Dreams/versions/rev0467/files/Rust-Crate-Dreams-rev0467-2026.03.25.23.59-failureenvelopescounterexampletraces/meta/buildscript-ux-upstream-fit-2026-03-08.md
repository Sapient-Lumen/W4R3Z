# Buildscript UX upstream-fit note — 2026-03-08

This note tightens **P-0046 buildscript-ux-kit** against current Cargo substrate.

## Main judgment

The right framing for **P-0046** is now clearer than when the proposal first landed.

Cargo already exposes **enough substrate** that this crate does not need to invent a new protocol:

- build-script directives and visibility rules are documented,
- `cargo::error` and `cargo::warning` are real first-class surfaces,
- `--message-format=json` includes `build-script-executed` output,
- Cargo distinguishes cached versus newly executed work in its JSON/messages,
- and unstable Cargo already points toward less-handwritten / more unit-shaped build-script futures (`metabuild`, `multiple-build-scripts`).

At the same time, the remaining gap is still very real:

- warnings from non-path dependencies are hidden by default unless the build fails or the user asks for `-vv`,
- build-script failures are still reported as noisy in live Cargo issues,
- `cargo::error` still has awkward presentation edge cases when scripts exit non-zero,
- and Cargo’s JSON output is a parsed substrate, not a support bundle.

So **P-0046** should be planned as a **support/report layer above Cargo**, not as a replacement for Cargo.

## Current upstream facts that matter

### 1. Cargo already documents build-script visibility rules

The build-script docs explicitly say `cargo::warning` is only shown by default for `path` dependencies; warnings from crates.io dependencies are normally hidden unless the build fails or the user uses `-vv`.

That means a serious crate should surface:

- whether a warning was visible by default,
- whether the user only saw it because the build failed,
- and whether the crate is escalating a hidden warning into a review artifact.

### 2. Cargo JSON already carries parsed build-script results

The external-tools docs say `--message-format=json` includes `build-script-executed` messages with parsed link/search/cfg/env/out_dir data.

That means **P-0046** should not start from “Cargo tells us nothing structured.”
It should import Cargo JSON first when available and treat raw stdout/stderr parsing as a supplement.

### 3. Cached build-script output is still output

Cargo’s JSON docs explicitly note that `build-script-executed` messages may appear even when the script was not run, showing previously cached values.

That means reports must distinguish at least:

- `live_capture`,
- `cargo_json_cached`,
- `imported_log`,
- or `mixed`.

Otherwise the crate will overclaim how direct its observations are.

### 4. `cargo::error` is real but does not finish the UX story

The build-script docs document `cargo::error`, and Cargo has already improved warning/error presentation historically.
But current Cargo issues still show that non-zero exits plus `cargo::error` can lead to logs where the structured message is followed by a large dump.

That means the crate should not frame itself as “fixing a missing directive.”
It should frame itself as:

- choosing the shortest actionable message,
- classifying noisy directive churn,
- and producing a reviewable bundle.

### 5. Upstream may reduce handwritten `build.rs`

Unstable Cargo already has `metabuild` and `multiple-build-scripts`.
That means **P-0046** should model **observations / units**, not hard-code one handwritten `build.rs` file path as the permanent identity.

## What 0.1 should provide

A good first version should hand other people:

- `buildscript-report.json`
- `buildscript-summary.txt`
- `policy-gate.report.json`
- optional `notes.md`

The key extra semantics should be:

- `capture_origin`
- message `visibility`
- package / unit identity
- `suggested_fix`
- `manual_review_required`
- `workspace_policy_scope`

## Recommended first scenarios

Prioritize small fixture bundles for:

1. `pkg_config_missing_lib`
2. `cargo_error_exitcode_mismatch`
3. `rerun_noise_overwhelms_failure`
4. `transitive_warning_hidden`
5. `cached_buildscript_output_not_run`
6. `workspace_policy_gate`
7. `secretish_output_redaction`

That list is intentionally support-oriented rather than “all possible build script protocol behavior”.

## Anti-patterns

- Do not pretend Cargo JSON is already the full support artifact.
- Do not assume every report came from a live run.
- Do not design around one permanent `build.rs` file-path identity.
- Do not turn policy gating into “fail on every transitive warning forever”.
- Do not merge this crate with native dependency resolution or build-script test harness work.

## Repo implication

The next worthwhile improvements on this frontier should prefer:

- richer fixture scenarios,
- stable bundle vocabulary,
- visibility/capture-origin semantics,
- and a sharper CLI/API contract for **P-0046**,

instead of adding another generic native-build-adjacent proposal.

## Sources

- Cargo build scripts reference: https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo external-tools JSON: https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo unstable features (`metabuild`, `multiple-build-scripts`): https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo issue #10159: https://github.com/rust-lang/cargo/issues/10159
- Cargo issue #15038: https://github.com/rust-lang/cargo/issues/15038
- Cargo issue #15792: https://github.com/rust-lang/cargo/issues/15792
