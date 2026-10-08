# Package contract — rev0068

## Why it exists

rev0067 passed its revision-local and inherited audits while `manifest.json` still described rev0066 and `data/revision_log.json` still ended at rev0061. Byte-level checksums faithfully preserved the inconsistency.

## Contract

`scripts/audit_package_contract.py` requires agreement among:

```text
root directory name
manifest revision, timestamp, codename, cube_name, filename
README first heading
latest revision-log entry
CHECKSUMS exact file coverage, byte counts, and SHA-256 hashes
environment/requirements records
absence of build and cache artifacts
```

The accepted name grammar is:

```text
Project-Name-rev####-YYYY.MM.DD.HH.MM-lowercase-hyphen-codename.zip
```

The audit intentionally distinguishes semantic identity from checksums. Both must pass.

## Finalization

Run validation first. Then run:

```bash
PYTHONPATH=. python scripts/finalize_package.py
PYTHONPATH=. python scripts/audit_package_contract.py
```

The finalizer removes `build/`, `__pycache__/`, `.pytest_cache/`, `*.pyc`, and `*.pyo`, writes `CHECKSUMS.json`, and invokes the package contract.

The archive must be created outside the cube root so it does not checksum itself.
