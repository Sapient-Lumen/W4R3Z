# Loose payload locator audit — rev0861

Status: `loose_hash_locator_ready_payloads_still_absent`.

## Risk addressed

rev0860 made exact-path candidate grafting safe, but it still assumed recovered
payload bytes would already sit at canonical EvidenceVault paths. That is a
practical recovery risk: caches, exports, filesystem searches, or unpacked
archives may preserve the bytes while losing the original directory shape.

rev0861 adds a hash-first locator that scans real candidate roots without
following symlinks, matches by exact byte count and SHA-256, and stages only a
complete, unique, non-ambiguous match set back to canonical paths.

## Current payload state

```text
full expected payloads:                 17
full expected bytes:                    25066
full missing without candidate roots:   17
minimum expected payloads:              4
minimum expected bytes:                 7751
minimum missing without candidate roots:4
canonical payload bytes in overlay:     0
```

## Controls now covered

```json
{
  "ambiguous_stage_rejected": true,
  "duplicate_hash_ambiguous": true,
  "loose_paths_found": true,
  "loose_paths_staged_to_canonical_targets": true,
  "partial_stage_rejected": true,
  "path_escape_rejected": true,
  "stage_inside_candidate_rejected": true,
  "stage_inside_overlay_rejected": true,
  "symlink_file_skipped": true
}
```

## Operator path

```bash
python3 PROOFCORE/verifiers/locate_streamfold_payloads_rev0861.py --mode minimum --json
python3 PROOFCORE/verifiers/locate_streamfold_payloads_rev0861.py \
  --candidate-root /path/to/cache-or-export \
  --mode minimum \
  --stage-dir /tmp/ev-streamfold-loose-minimum \
  --json
python3 scripts/validate_streamfold_loose_payload_locator_rev0861.py
```

## Still blocked

The overlay still contains zero canonical streamfold payload bytes. This audit
does not grant rights, does not recover payload bytes, does not prove streamfold
correctness, and does not claim a SNARK, zero-knowledge proof, or succinct proof.
