# Archive payload search audit — rev0862

## Risk addressed

The active streamfold recovery bottleneck is still payload absence. rev0861 made loose directory recovery possible, but a likely real-world source is a ZIP/export/cache artifact. rev0862 adds a ZIP-aware archive search path so candidate archives can be scanned by exact byte count and SHA-256 without full extraction.

## Current state

- Full selected streamfold payloads: 17
- Full selected payload bytes: 25066
- Full missing in this overlay: 17
- Minimum first recovery payloads: 4
- Minimum missing in this overlay: 4
- Cloudtainer EvidenceVault ZIP artifacts scanned: 12
- Payload matches in those ZIP artifacts: 0

The cloudtainer scan is a negative receipt, not a proof that the payload bytes do not exist elsewhere.

## Executable surfaces

```bash
python3 PROOFCORE/verifiers/locate_streamfold_payload_archives_rev0862.py --mode full --json
python3 PROOFCORE/verifiers/locate_streamfold_payload_archives_rev0862.py --self-test --json
python3 scripts/validate_streamfold_archive_payload_search_rev0862.py
```

To test a future archive or unpacked cache:

```bash
python3 PROOFCORE/verifiers/locate_streamfold_payload_archives_rev0862.py \
  --candidate-source /path/to/export.zip \
  --candidate-source /path/to/unpacked/cache \
  --mode minimum \
  --stage-dir /tmp/ev-streamfold-archive-stage \
  --json
```

## Controls exercised

- `ambiguous_stage_rejected`: True
- `directory_payload_found`: True
- `duplicate_hash_ambiguous`: True
- `mixed_sources_staged_to_canonical_targets`: True
- `partial_stage_rejected`: True
- `stage_inside_candidate_directory_rejected`: True
- `stage_inside_overlay_rejected`: True
- `unsafe_zip_member_skipped`: True
- `zip_payload_found`: True
- `zip_symlink_entry_skipped`: True

## Non-claims

This lane does not recover payload bytes, grant rights, unblock publication, prove streamfold correctness, or claim SNARK/zero-knowledge/succinct proof properties.
