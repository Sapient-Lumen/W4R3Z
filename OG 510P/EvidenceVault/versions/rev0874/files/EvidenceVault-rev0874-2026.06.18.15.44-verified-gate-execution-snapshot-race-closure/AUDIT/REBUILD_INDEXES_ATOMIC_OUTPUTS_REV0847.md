# Rebuild-indexes atomic output audit — rev0847

- Status: `rebuild_indexes_release_critical_outputs_atomic_and_symlink_guarded`
- Revision context: `rev0847-overlay-over-rev0846-over-rev0840`
- Purpose: Make rebuild_indexes.py write generated release-critical digest and metadata surfaces through atomic same-directory replacements instead of direct truncating writes.
- Risk reduced: Interrupted rebuilds are less likely to leave truncated INDEX, MANIFEST, RELEASE_MANIFEST, or RO-Crate surfaces, and generated-output parents such as INDEX/ are rejected if they resolve through symlinks.

- Changed/rebuild script: `scripts/rebuild_indexes.py`
- SHA-256: `df31735a8f0d6bbeec632094880ed2e6f218a57f623d01c522766f2422b12477`

## Dynamic cases

- clean atomic generated-output helper write replaces bytes and leaves no temporary files
- generated-output target outside the archive root is rejected
- symlinked generated-output parent INDEX/ is rejected before bytes are written outside the archive
- simulated os.replace failure propagates and removes the same-directory temporary file

## Protected outputs

- `RELEASE_MANIFEST.json`
- `ro-crate-metadata.json`
- `RO_CRATE_PROFILE.md`
- `INDEX/files.json`
- `INDEX/files.csv`
- `MANIFEST.sha256`

## Limits

- This validates helper behavior with fixtures; a full canonical tree should still run make rebuild-indexes and make gate after applying the overlay stack.
- Atomic replacement reduces partial-write risk, but it is not a signed provenance or crash-consistency guarantee for every filesystem.

## Validator

- Command: `/opt/pyvenv/bin/python3 scripts/validate_rebuild_indexes_atomic_outputs_rev0847.py`
- Return code: `0`
- Validator SHA-256: `e77aa4d1fa1e3c9b246d62eea60792554521cb289ab457fb9bbdaec8c35fb8a3`

```text
rebuild-indexes-atomic-outputs-rev0847: OK
```
