# Source-bundle intake and safe-extraction gate — rev0064

rev0064 continues from rev0063 and does not open a new private packet. The goal is to make the uploaded source bundle itself an audited input, not just an implicit prerequisite for downstream replay helpers.

## Source identity

```text
source bundle: Nicotine-source(1).zip
expected SHA256: feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b
observed SHA256: feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b
ZIP entries scanned: 3551
source-lane files manifested: 2139
source-lane total bytes: 46605550
status: pass
```

## Source lanes

| lane | files | bytes | manifest SHA256 | git worktree HEAD | status |
|---|---:|---:|---|---|---|
| `github-tag-3.3.10` | 678 | 14577303 | `12bf750459c12fff6770598b5dc11ab7c8e3e77b6995a74bad6a94a1cb37d2cd` | `caf9e101a841ff2e0a96aebc8e07bbf7ff1b2026` | pass |
| `github-branch-3.3.x` | 684 | 14625090 | `64f696fc32bcb45213b5f40491c546cf9a9a5844f2fd854001747d78f713df3d` | `98089ac233aa57786e8dbdc48123f6ac1c4767d8` | pass |
| `github-branch-master` | 777 | 17403157 | `eef3d4dae0c236813310ef79c886d8740127d175f9b058a6015c185a1c6289aa` | `f4e17d59783dbc48ea31d2e899a681e2dd1ed500` | pass |

The source ZIP also contains a `git-full` payload, but rev0064's safe extraction gate treats the three `source-trees/<lane>/` directories as the replay input. The lane `.git` entries are plain `gitdir:` files, and the worktree HEAD rows above are recorded only as provenance.

## What the new helper checks

`tools/probe_rev0064_source_intake_safety.py` validates the uploaded source bundle by checking:

1. bundle SHA256 and existence;
2. all ZIP entries for absolute paths, parent traversal, symlinks, and duplicate normalized names;
3. all source-lane files with content hashes;
4. source-lane git worktree HEAD/ORIG_HEAD consistency;
5. safe extraction of each lane into a temporary directory and manifest-hash roundtrip;
6. the 15 critical touched source files against the rev0051 archived source-file manifest;
7. synthetic fail-closed controls for unsafe ZIP shapes;
8. package hygiene so the cube still does not embed `source-trees`, `git-full`, `.git`, `__pycache__`, or `.pytest_cache` directories.

## Verification result

```text
entry safety failures: 0
lane summaries passing: 3/3
git identity rows passing: 3/3
critical file crosscheck: 15/15
safe extraction roundtrip: 3/3
negative controls: 4/4
package hygiene rows: 5/5
```

Negative controls intentionally create malformed in-memory ZIPs and verify rejection of:

```text
parent traversal source entry
absolute path entry
symlink source entry
duplicate normalized entry
```

## Files added

```text
docs/SOURCE-INTAKE-SAFE-EXTRACTION-GATE-REV0064.md
docs/SOURCE-INTAKE-COHERENCE-REFACTOR-REV0064.md
handoff/rev0064/SOURCE-INTAKE-SAFE-EXTRACTION-GATE.md
tools/probe_rev0064_source_intake_safety.py
evidence/rev0064-source-intake-helper-output.json
evidence/rev0064-source-intake-gate/
data/rev0064_source_* files
```

## Boundary

This is archived-source intake proof. It does not say the seven packets are fixed or unfixed on live current upstream. A fresh current checkout or source tarball still needs to be identified, hashed, classified, and run through the current-source seven-gate flow before live-current external filing.
