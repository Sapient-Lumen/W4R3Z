# 2026-03-25 userspace fetch surface pass

## Goal
Preserve one small static answer to a later-machine question that the archive could not yet answer from the existing userspace-rustup plan alone: *how complicated is the dependency/bootstrap surface right now, before anyone spends a brief egress window on it?*

## Landed
- Added `scripts/report/build_cloudtainer_userspace_fetch_surface.py`.
- Added `scripts/test/check_cloudtainer_userspace_fetch_surface.py`.
- Added generated companions:
  - `artifacts/reports/cloudtainer_userspace_fetch_surface.json`
  - `docs/CLOUDTAINER_USERSPACE_FETCH_SURFACE.md`
- Threaded the new card through the Makefile surface, docs indexes, environment guidance, generated-doc presence check, and inventory refreshes.

## Main local result
The current later-machine Rust lane is still the compact case:
- `fetch_surface_code = registry_only_single_workspace`
- `Cargo.lock` packages: `80`
- registry packages: `79`
- git packages: `0`
- workspace/path packages: `1`
- workspace members: `1` (`crates/gr_engine`)
- direct `gr_engine` deps: runtime `9`, dev `2`, build `0`
- additive toolchain requests: component `rustfmt`, no extra compilation targets

## Why it matters
The archive now preserves not just the comeback commands, but also the static reason those commands are still expected to fit inside a brief later-machine egress window. If the lockfile or workspace widens later, this card should fail loudly before someone assumes the old fetch budget is still safe.

## Local checks
- `python3 scripts/report/build_cloudtainer_userspace_fetch_surface.py --write`
- `python3 scripts/test/check_cloudtainer_userspace_fetch_surface.py`
- `python3 scripts/test/check_cloudtainer_userspace_rustup_plan.py`
- `python3 scripts/test/check_generated_docs_presence.py`
- `python3 scripts/test/check_research_docs.py`
- `python3 scripts/test/check_scripts_compile.py`
- `make update-command-inventory`
- `make test-command-inventory`
- `make update-validator-inventory`
- `make test-validator-inventory`
- `make update-artifact-buckets`
- `make test-artifact-buckets`
- `make test-reports-json`
