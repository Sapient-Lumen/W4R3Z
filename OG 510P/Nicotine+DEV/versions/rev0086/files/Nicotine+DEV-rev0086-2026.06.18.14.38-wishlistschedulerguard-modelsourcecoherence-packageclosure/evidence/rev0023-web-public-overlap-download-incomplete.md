# rev0023 public-overlap packet — DOWNLOAD-INCOMPLETE-PROVENANCE-01

## Search themes

Searched for combinations of:

```text
Nicotine+ incomplete download resume stale bytes
Nicotine+ INCOMPLETE md5 username virtual_path downloads.py
Nicotine+ incomplete file lock fcntl lockf
Nicotine+ shutil.move completed download race
Nicotine+ existing file same size already downloaded
Nicotine+ complete file remains in Incomplete Downloads folder
Nicotine+ Cannot save file incomplete INCOMPLETE
Nicotine+ files deleted on quit incomplete folder
```

## Important public overlap

- GitHub issue #3769: completed downloads can remain in the incomplete folder after a temporary completed-folder permission/move failure, and the reporter asks for retry/recovery behavior.
- GitHub issue #1019: complete files remained in the incomplete folder and stalled at 100%/waiting states.
- GitHub issue #1411: every downloaded file remained as an `INCOMPLETE...` filename despite appearing completed.
- GitHub issue #3152: incomplete-folder deletion safety issue when finished/incomplete/received folders overlap.
- GitHub issue #2888: invalid incomplete path/filename surfaced as repeated `Cannot save file` errors.
- Release notes list #1019 as a historical closed issue, confirming the incomplete-completion symptom area is publicly known.

## Novelty assessment

```text
U-226: public-adjacent, not clean. No exact stale exact-size incomplete-byte provenance report found in this pass.
U-230: public-adjacent, not clean. No exact symlink/no-follow incomplete-file open report found in this pass.
U-250: public-adjacent, not clean. No exact lock-failure-continues report found in this pass.
U-253: candidate no direct public match found, but constraint-sensitive and support-only.
U-222: public-adjacent, support-only. No exact same-size complete-file provenance report found in this pass.
U-249: public-overlap/public-adjacent because #3769 directly overlaps final-move failure/retry behavior; exact TOCTOU wording not found.
```

## Decision consequence

Because public incomplete-folder/finalization symptoms are already substantial, rev0023 does not present this family as a clean fresh security finding. It is kept as verified audited-backlog hardening.
