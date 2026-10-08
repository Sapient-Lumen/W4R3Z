# Buildscript TestKit fixtures

This fixture family exists to make **P-0059 buildscript-testkit** more concrete.

The goal is to make `build.rs` behavior reviewable without pretending to emulate every Cargo internal.

## Intended first scenarios

1. `fake_pkg_config_success` — stable link/search/cfg output from a mocked `pkg-config`.
2. `fake_pkg_config_missing` — deterministic failure with actionable help.
3. `rerun_scope_regression` — script accidentally broadens rerun triggers.
4. `env_allowlist_gap` — script depends on an undeclared env input.
5. `vendored_fallback_path` — source-build fallback path is exercised in a fixture, not only on a maintainer laptop.

## Minimal bundle for 0.1

- `fixture-manifest.toml`
- `buildscript-run.report.json`
- `directives.normalized.json`
- `notes.md`

## Design rule

Prefer **stable normalized outputs** and fake-tool fixtures over brittle machine-specific golden logs.
## Included example

- `scenarios/fake_pkg_config_missing/` — tiny deterministic missing-library fixture.
