# Git provenance / source-tree match gate — rev0065

rev0065 continues from rev0064 and does not open a new private packet. The goal is to deepen the source-bundle audit: rev0064 proved that `Nicotine-source(1).zip` can be safely ingested; rev0065 proves that the three archived source lanes are bound to the Git object/ref provenance bundled with that source ZIP.

## Source identity

```text
source bundle: Nicotine-source(1).zip
expected SHA256: feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b
observed SHA256: feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b
ZIP safety errors: 0
status: pass
```

## Git worktree and ref binding

rev0065 validates, for each archived lane:

```text
source-trees/<lane>/.git pointer parses to the matching bundled worktree path
bundled git-full/.git/worktrees/<lane>/HEAD equals expected lane commit
bundled git-full/.git/worktrees/<lane>/ORIG_HEAD equals expected lane commit
worktree commondir is ../..
reverse gitdir pointer names source-trees/<lane>/.git
expected packed ref resolves to the lane commit
upstream remote URL is https://github.com/nicotine-plus/nicotine-plus.git
commit object exists and is a Git commit
```

| lane | expected ref | commit | commit subject | status |
|---|---|---|---|---|
| `github-tag-3.3.10` | `refs/tags/3.3.10` | `caf9e101a841ff2e0a96aebc8e07bbf7ff1b2026` | `Version 3.3.10 (#3321)` | pass |
| `github-branch-3.3.x` | `refs/remotes/upstream/3.3.x` | `98089ac233aa57786e8dbdc48123f6ac1c4767d8` | `shares.py: remove path traversal components when normalizing virtual name` | pass |
| `github-branch-master` | `refs/remotes/upstream/master` | `f4e17d59783dbc48ea31d2e899a681e2dd1ed500` | `macOS: avoid rendering glitches in GTK 4.22` | pass |

## Git tree ↔ source-tree comparison

rev0065 compares each tracked Git tree blob to the corresponding file in the archived `source-trees/<lane>/` tree using Git blob SHA-1 calculation.

| lane | tracked files | source files excluding `.git` | exact matches | materialized symlink rows | non-symlink mismatches | extra files | strict touched files exact | status |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `github-tag-3.3.10` | 677 | 677 | 676 | 1 | 0 | 0 | 5/5 | pass |
| `github-branch-3.3.x` | 683 | 683 | 681 | 2 | 0 | 0 | 5/5 | pass |
| `github-branch-master` | 776 | 776 | 769 | 7 | 0 | 0 | 5/5 | pass |

The materialized-symlink rows are retained as an explicit packaging deviation rather than hidden as mismatches. They are all Git mode `120000` paths outside the seven strict/front packet touched-source set. The 15 strict/front touched files remain exact Git tree blob matches across the three lanes.

Detailed rows:

```text
data/rev0065_git_tree_file_match_manifest.csv/json
data/rev0065_git_symlink_materialization.csv/json
```

## Negative controls

The helper includes four fail-closed controls:

```text
tampered tracked file blob -> detected as blob mismatch
wrong worktree HEAD -> detected as head mismatch
missing expected packed ref -> detected as ref missing
unsafe source .git pointer -> rejected by pointer validator
```

All four negative controls passed.

## Verification

```text
rev0065 Git provenance helper: pass
worktree identity rows: 3/3 pass
git ref rows: 3/3 pass
commit provenance rows: 3/3 pass
git tree file rows: 2136 validated
materialized symlink rows: 10 classified
strict touched files exact: 15/15
negative controls: 4/4 pass
package hygiene rows: 5/5 pass
inherited rev0064 source-intake rerun: pass
coherence linter: no structural coherence-map errors detected
```

## Boundary

This is archived-source Git provenance proof. It does not say that the seven packets are fixed or unfixed on live current upstream. A fresh current checkout or current source tarball still needs to be identified, hashed, classified, and run through the current-source seven-gate flow before live-current external filing.
