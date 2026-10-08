# Handoff — rev0065 Git provenance / tree-match gate

Purpose: give reviewers a compact proof that the uploaded archived source bundle is not merely a loose ZIP of files. The strict/front archived source lanes are bound to bundled Git worktree metadata, packed refs, commit objects, and Git tree blobs.

Primary files:

```text
docs/GIT-PROVENANCE-TREE-MATCH-GATE-REV0065.md
docs/GIT-PROVENANCE-COHERENCE-REFACTOR-REV0065.md
tools/probe_rev0065_git_tree_provenance.py
data/rev0065_git_worktree_identity.csv/json
data/rev0065_git_ref_integrity.csv/json
data/rev0065_git_commit_provenance.csv/json
data/rev0065_git_tree_file_match_summary.csv/json
data/rev0065_git_tree_file_match_manifest.csv/json
data/rev0065_git_symlink_materialization.csv/json
data/rev0065_git_provenance_negative_controls.csv/json
evidence/rev0065-git-provenance-helper-output.json
```

Reviewer command:

```bash
python tools/probe_rev0065_git_tree_provenance.py --source-zip /path/to/Nicotine-source.zip
```

Expected high-level result:

```text
status: pass
worktree identity rows: 3
git ref rows: 3
commit rows: 3
git tree file rows: 2136
negative controls: 4
package hygiene rows: 5
failures: 0
```

Important exception: ten Git mode `120000` paths are materialized as regular file contents in the uploaded source tree. They are recorded in `data/rev0065_git_symlink_materialization.csv`; none are strict/front packet-touched files.
