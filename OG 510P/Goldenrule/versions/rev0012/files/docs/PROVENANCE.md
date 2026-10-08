# Provenance And Verification

Concord treats outcomes as evidence artifacts, not screenshots or anecdotes.
If bytes change, claims must be re-verified.

## Definitions Are Artifacts

Evaluation definitions must be explicit and hashable.

Current examples:
- Gauntlet spec: `examples/gauntlet/gauntlet_v1.json`
- Holdout spec: `examples/holdouts/holdout_v1.json`

`grlab gauntlet` and `grlab holdout` include spec hashes (and resolved opponent/probe hashes) in output JSON.

## Run Manifests

For run-based workflows, `manifest.json` records:
- experiment hash,
- world and strategy hashes,
- `definitions_hash`.

Use `grlab defdiff` to compare run definitions:

```bash
python3 -m grlab defdiff runs/<run_a> runs/<run_b>
```

## Attestation

`grlab attest` writes `attestation.json` with stable hashes over key artifacts.
Depending on flags and available files, this includes:
- `manifest_sha256`
- `report_sha256`
- `queue_db_sha256`
- `definitions_hash`
- `artifacts_tree_sha256`

Example:

```bash
python3 -m grlab attest runs/<run_id> --include-queue-db --include-artifacts
```

## Verify

`grlab verify` checks that current bytes match the attestation.

Verify a run directory:

```bash
python3 -m grlab verify runs/<run_id>
```

Verify a tarball export:

```bash
python3 -m grlab verify <bundle.tar.gz>
```

Optional consistency check for manifest definition hashing:

```bash
python3 -m grlab verify runs/<run_id> --check-definitions-hash
```

## Public Export Safety

Public sharing should use redaction/export with policy checks:

```bash
python3 -m grlab redact runs/<run_id> --out-dir <redacted_dir> --public
python3 -m grlab export runs/<run_id> --out <bundle.tar.gz> --public
```

Policy denylist:
- `policy/public_export_denylist.json`

Overrides require explicit operator intent (`--allow-sensitive`).
