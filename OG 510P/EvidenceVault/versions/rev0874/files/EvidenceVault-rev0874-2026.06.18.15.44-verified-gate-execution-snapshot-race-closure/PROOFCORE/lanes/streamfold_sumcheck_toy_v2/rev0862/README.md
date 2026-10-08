# rev0862 streamfold archive payload search lane

rev0862 closes the next recovery gap after the loose hash locator: candidate payload bytes may be trapped inside ZIP/export artifacts rather than exposed as ordinary files. The new verifier scans real directories and ZIP archives by exact byte count and SHA-256, then stages only complete unique matches to canonical EvidenceVault paths outside the overlay.

This is deliberately narrow and executable:

```bash
python3 PROOFCORE/verifiers/locate_streamfold_payload_archives_rev0862.py --mode full --json
python3 PROOFCORE/verifiers/locate_streamfold_payload_archives_rev0862.py --self-test --json
python3 PROOFCORE/verifiers/locate_streamfold_payload_archives_rev0862.py \
  --candidate-source /path/to/export.zip \
  --candidate-source /path/to/unpacked/cache \
  --mode minimum \
  --stage-dir /tmp/ev-streamfold-archive-stage \
  --json
```

Current bundle state remains blocked: all 17 canonical `streamfold_sumcheck_toy_v2` payloads are absent from the overlay. The cloudtainer search receipt records that 12 visible EvidenceVault ZIP artifacts were scanned by this lane and produced zero payload matches.

The lane rejects duplicate hash matches as ambiguous, skips ZIP symlink entries, skips unsafe ZIP member names, refuses partial staging, refuses staging inside the overlay, and refuses staging inside directory candidate roots.

Non-claims: this is not a recovered payload bundle, not a rights grant, not a publication permission signal, not a SNARK, not zero knowledge, and not a streamfold protocol-correctness proof.
