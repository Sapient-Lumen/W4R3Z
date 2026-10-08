# Scenario: subdirectory package with dirty VCS snapshot

A package under `crates/widget/` is packaged from a dirty worktree.
The bundle preserves `.cargo_vcs_info.json` facts and explicitly repeats that they are best-effort rather than provenance.
