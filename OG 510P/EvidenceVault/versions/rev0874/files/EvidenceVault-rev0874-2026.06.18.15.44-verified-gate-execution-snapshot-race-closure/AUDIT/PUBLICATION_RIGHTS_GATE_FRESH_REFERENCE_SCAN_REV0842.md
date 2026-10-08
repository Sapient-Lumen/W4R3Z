# Publication rights gate fresh-reference scan audit — rev0842, refreshed in rev0845

This carried-forward audit was refreshed because rev0845 changed the shared publication rights gate while preserving the rev0842 fresh-scan contract.

- Status: `fresh_license_reference_scan_gate_hardened_refreshed_with_rev0845_symlink_boundary`
- Helper SHA-256: `abfab7a27c008d49f2157a70f66660cdf15ed3f39af5af3767afa85a1d86dd73`
- Validator: `scripts/validate_publication_rights_gate_fresh_scan_rev0842.py`
- Validator return code: `0`

## Required behavior
- missing local LICENSE reference blocks a rights-ready ledger
- resolved local LICENSE reference allows a rights-ready ledger
- stale ledger missing-reference count blocks when canonical payload roots are present
- partial scan scope with a claimed ledger reference count fails closed
- CLI --json ready-root probe emits JSON and no Python bytecode

## Validator output

```text
publication-rights-gate-fresh-scan-rev0842: OK
```

## Limit

The scan is intentionally narrow and does not infer licensing terms.
