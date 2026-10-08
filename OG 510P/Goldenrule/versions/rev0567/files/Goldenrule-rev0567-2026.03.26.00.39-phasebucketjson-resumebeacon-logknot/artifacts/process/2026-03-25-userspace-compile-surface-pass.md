# 2026-03-25 userspace compile surface pass

## Goal
Preserve one compact answer to the next later-machine question after the new userspace fetch card: once the registry-only warm-cache step succeeds, does the first compile/test foothold still look like a proc-macro/Pure-Rust bring-up, or has the workspace started asking for build-script or native-helper repair work?

## Landed
- Added `scripts/report/build_cloudtainer_userspace_compile_surface.py`.
- Added `scripts/test/check_cloudtainer_userspace_compile_surface.py`.
- Added generated companions:
  - `artifacts/reports/cloudtainer_userspace_compile_surface.json`
  - `docs/CLOUDTAINER_USERSPACE_COMPILE_SURFACE.md`
- Threaded the new card through the Makefile surface, docs indexes, environment guidance, generated-doc presence check, and inventory refreshes.
- Extended `docs/RESEARCH_SOURCES.md` with `RS-GR-562` and `RS-GR-563`.

## Main local result
The first later-machine compile lane is still the narrow case:
- `compile_surface_code = direct_derive_no_native_build`
- direct dependencies: `11` total (`9` runtime / `2` dev / `0` build)
- direct derive-feature entry points: `2` (`clap`, `serde`)
- workspace `build.rs` files: `0`
- lockfile codegen-support package hits: `6`
- lockfile native-helper watchlist hits: `0`
- workspace targets: library `yes`, bins `1`

## Why it matters
The archive now preserves both halves of the later-machine compile story: the fetch lane is still compact, and the first compile/test witness still looks like proc-macro/codegen friction rather than a native-host package rescue. If that changes later, this card should fail loudly before someone spends a short external Rust session on the wrong preparation.

## Local checks
- `python3 scripts/report/build_cloudtainer_userspace_compile_surface.py --write`
- `python3 scripts/test/check_cloudtainer_userspace_compile_surface.py`
- `python3 scripts/test/check_cloudtainer_userspace_fetch_surface.py`
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
