# 2026-03-25 — userspace offline proof ladder pass

## Goal

Add one compact later-machine execution surface that proves the warmed userspace Cargo cache is actually sufficient **offline** before widening to more Rust work.

## Added

- `scripts/report/build_cloudtainer_userspace_offline_proof_ladder.py`
- `scripts/test/check_cloudtainer_userspace_offline_proof_ladder.py`
- `artifacts/reports/cloudtainer_userspace_offline_proof_ladder.json`
- `docs/CLOUDTAINER_USERSPACE_OFFLINE_PROOF_LADDER.md`

## Main preserved result

- current ladder code: `fetch_then_offline_compile_then_exact`
- current quick foothold remains shard prefix `1`
- touched target remains `probe_run`
- only `1` of `7` emitted phases requires network access
- explicit later-machine checkpoint now exists between `cargo fetch --locked` and the first exact witness:
  - `cargo test --locked --offline --no-run -p gr_engine --test probe_run`

## Why this mattered

The archive already preserved:
- how to bootstrap repo-local rustup later,
- that the lockfile surface is still registry-only and compact,
- and that the first compile lane still looks like proc-macro bring-up rather than native-helper rescue.

What was still missing was the first *execution* proof that those static facts are enough to keep moving without further network access. This pass closes that gap.

## Validation run

- `make update-cloudtainer-userspace-offline-proof-ladder`
- `make test-cloudtainer-userspace-offline-proof-ladder`
- `make update-command-inventory`
- `make test-command-inventory`
- `make update-validator-inventory`
- `make test-validator-inventory`
- `python3 scripts/test/check_generated_docs_presence.py`
- `python3 scripts/test/check_readme_command_surface.py`
- `python3 scripts/test/check_docs_index_core.py`
- `python3 scripts/test/check_research_docs.py`
- `python3 -m py_compile scripts/report/build_cloudtainer_userspace_offline_proof_ladder.py scripts/test/check_cloudtainer_userspace_offline_proof_ladder.py`

## Source handles added

- `RS-GR-564` — Cargo `cargo test --no-run`
- `RS-GR-565` — Cargo offline / frozen guidance
