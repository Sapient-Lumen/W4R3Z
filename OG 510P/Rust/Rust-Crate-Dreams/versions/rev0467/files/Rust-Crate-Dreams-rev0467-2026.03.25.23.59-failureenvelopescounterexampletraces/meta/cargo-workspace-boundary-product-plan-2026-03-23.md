# Product plan — P-0506 Cargo Workspace Boundary Doctor Kit (2026-03-23)

## Product thesis

The crate should help another person answer one boring but high-value question:

> “What exactly did Cargo consider above me, under which invocation mode, and which config layers could have changed the result?”

The product is therefore a **reviewable support bundle**, not a config editor and not a Cargo replacement.

## Receiver-facing artifacts

### 1) `ancestor-discovery.receipt.json`
What it should provide:
- subject manifest / subject path
- invocation mode
- ancestor candidates in observed order
- candidate kind (`manifest`, `config_file`, `config_include`, `home_config`, `cargo_home_config`)
- stop / boundary reason (`selected_workspace_root`, `explicit_workspace_boundary`, `single_file_autodiscovery_disabled`, `no_candidate`, `manual_review_required`)
- exactness class for each candidate (`observed`, `inferred`, `suspected`)

### 2) `config-layering.report.json`
What it should provide:
- all material config routes
- precedence order
- include edges
- path basis per route (`cwd`, `config_parent`, `cargo_home`, `env_literal`, `manual_review_required`)
- whether member-crate configs were omitted because invocation happened at the workspace root
- notes for redaction or partial visibility

### 3) `invocation-mode.report.json`
What it should provide:
- invocation family (`cwd_auto_discovery`, `manifest_path`, `manifest_command`, `single_file_manifest_path`, `single_file_manifest_command`)
- subject kind (`cargo_toml`, `single_file_package`)
- config-root expectation
- workspace auto-discovery posture
- whether cwd and subject-root are intentionally different

### 4) `boundary-support-bundle.manifest.json`
What it should provide:
- versioned top-level manifest
- bundle members and hashes
- redaction posture
- exactness warnings
- route back to diagnosis/advice

## CLI shape

- `cargo boundary-doctor capture` — emit all available bundle files
- `cargo boundary-doctor doctor` — print a short diagnosis + path to bundle
- `cargo boundary-doctor diff old.bundle new.bundle` — compare discovery/config/invocation drift

## v0.1 implementation cut

Build only enough to stabilize the vocabulary:
- detect cwd vs subject path
- walk ancestor candidates conservatively
- import config file locations and `include` chains
- record env / `--config` route presence when visible
- classify invocation mode
- emit diagnosis families without auto-fixing

## Adoption story

Best first adopters:
- editor and wrapper authors
- CI teams with non-root launches
- monorepo maintainers
- users debugging parent-manifest/home-config poisoning

## What not to build yet

- manifest/config rewriting
- interactive TUI
- full Cargo parser emulation
- broad build-failure explanation beyond discovery/config boundaries
