---
id: P-0059
title: buildscript-testkit — hermetic tests and fixtures for build.rs and -sys crates
status: idea
domains: [cargo, build-scripts, ffi, testing]
last_reviewed: 2026-03-08
evidence:
  - https://github.com/gdesmott/system-deps/issues/97
  - https://doc.rust-lang.org/cargo/reference/build-scripts.html
  - https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
needs:
  - Make build scripts testable and reduce copy-paste bugs in -sys crates.
  - Provide a standard harness for verifying emitted cargo instructions and metadata contracts.
risks:
  - Hard to be fully cross-platform; must start with a narrow, valuable harness.
  - Needs careful UX so maintainers actually write tests instead of skipping.
---

## Problem

`build.rs` logic is often copied from other crates, rarely has tests, and can be highly platform-dependent. This creates brittle FFI crates and confusing failure modes for end users. The `system-deps` community explicitly calls out that copied imperative build scripts share bugs/defects and aren’t easily updated or tested.

A dedicated test harness could make build scripts *boringly reliable*.

## Users & user stories

- **Sys crate maintainers**: “I want to lock down what my build script emits and detect regressions early.”
- **Downstream application teams**: “I want failures to be explainable and reproducible across CI and local machines.”
- **Tool authors**: “I want fixtures that represent ‘real build.rs behavior’ to validate tooling.”

## Prior art (and why it’s insufficient)

- Cargo docs describe how build scripts work, but do not provide a standard testing approach.  
  https://doc.rust-lang.org/cargo/reference/build-scripts.html  
- Some crates test build scripts indirectly (integration tests in downstream projects), but that’s slow, flaky, and hard to maintain.
- `system-deps` reduces the need for imperative scripts, but many crates can’t adopt it immediately and still need quality gates.  
  https://github.com/gdesmott/system-deps/issues/97

## Design goals / non-goals

### Goals
- Run a build script in a **controlled environment** with deterministic inputs.
- Capture and parse emitted lines (`cargo:...`, `cargo::...`) into a structured model.
- Provide fixture helpers for mocking common native discovery mechanisms (fake `pkg-config`, fake `vcpkg` outputs).
- Produce stable “golden” outputs so changes are reviewable.

### Non-goals
- Fully emulate Cargo’s compilation pipeline.
- Replace integration tests; instead, make unit-style tests for build scripts practical.

## Architecture & API sketch

### Library core
- `BuildScriptRunner::run(script_path, ctx) -> BuildScriptOutput`
  - captures stdout/stderr
  - parses cargo directives into `Directives`:
    - link libs, link search paths, cfgs, rerun rules, metadata keys
- `TestContext`:
  - env vars allowlist
  - temp `OUT_DIR`
  - optional mocked tool binaries on `PATH` (e.g., `pkg-config`)

### Test macros
- `#[buildscript_test] fn test_name(ctx: &mut TestContext) { ... }`
- helpers:
  - `ctx.mock_pkg_config("openssl", include_dirs=[...], libs=[...])`
  - `ctx.mock_vcpkg("zlib", ...)` (later)

### Golden files
- `assert_output_matches!("fixtures/foo.expected.json", output.normalized_json())`
- normalization rules:
  - sort paths and libs
  - strip machine-specific temp paths via placeholders

## Security / safety model

- Treat build scripts as untrusted code when running tests:
  - default “no network” sandbox mode when possible
  - strict limits on runtime and output size
- Provide a “deny-by-default” env allowlist.

## Maintenance & governance

- Keep the core crate dependency-light and stable.
- Maintain a shared fixture corpus for common sys crates patterns (linking, generated headers, cfgs).

## MVP milestones

- **0.1**: run a build script binary; parse directives; golden output comparisons; mock `pkg-config`.
- **0.2**: `cargo buildscript-test` subcommand to run harnesses across a workspace.
- **0.3**: optional sandbox integration (pairs well with `isolate-kit` / build sandbox proposals).


## What this crate should provide other people

This crate should make `build.rs` behavior reviewable before users discover it the hard way.

Other people should get:

- `buildscript-run.report.json` — normalized env, mocked tools, exit status, stdout/stderr excerpts, and parsed directives.
- `directives.normalized.json` — link/search/cfg/rerun/metadata directives in stable sorted form for golden tests.
- `fixture-manifest.toml` — explicit scenario inputs (`PATH`, env allowlist, fake `pkg-config`, fake `vcpkg`, expected failures).
- `notes.md` — scenario-specific explanation for future reviewers.

That gives maintainers a real answer to:

- “did my script emit the same contract as last release?”,
- “did I accidentally broaden rerun triggers?”,
- and “does my fallback path actually work without a live system package manager?”

## 0.1 boundaries

A good 0.1 should:

- run build scripts in a controlled fixture environment,
- parse Cargo directives into typed normalized output,
- support a fake `pkg-config` backend first,
- and keep sandboxing optional and layered rather than mandatory.

A bad 0.1 would try to faithfully emulate the entire Cargo pipeline or promise full cross-platform parity from day one.
## Recommended 0.1 crate split

Keep the first release split between:

- `buildscript-test-core` — controlled execution, output capture, directive normalization
- `buildscript-fixture-tools` — fake `pkg-config`, temp-path placeholders, env allowlists
- `cargo-buildscript-test` — workspace-facing runner and golden update UX

This keeps the value centered on **reviewable fixture behavior**, not on emulating Cargo wholesale.

## Upstream fit

This crate should test **build behavior**, not bake in a permanent assumption that the ecosystem will always center one handwritten `build.rs` file.

Because Cargo already has unstable `metabuild` and `multiple-build-scripts` surfaces, the harness should model one or more build-script executions / units and keep its scope on deterministic fixture inputs plus normalized outputs rather than trying to emulate Cargo wholesale.
