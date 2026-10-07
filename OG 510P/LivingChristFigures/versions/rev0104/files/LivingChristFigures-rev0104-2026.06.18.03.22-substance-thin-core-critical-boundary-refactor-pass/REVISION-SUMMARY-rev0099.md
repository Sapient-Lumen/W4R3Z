# Revision Summary — rev0099

rev0099 is a public-bundle boundary and surface-refactor pass. It adds a PUBLIC-only bundle manifest and a release-blocking Public Export Surface Audit so the legacy public export manifest cannot be misread as permission to export internal review evidence. The audit proves the public payload stays under PUBLIC/, blocks raw URLs/contact fields/source-ledger exposure in the bundle, classifies legacy included_files as reviewer-support only, and keeps the public layer closed. No candidate/source/claim/public content expansion is made.

## Main additions

- `PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json`
- `tools/public_export_surface_audit.py`
- `META/Public-Export-Surface-Audit-current.*`
- `SCHEMA/Public-Export-Surface-Audit-Fields-current.*`
- release gate `gate_082`

## Boundary outcome

The actual public bundle is PUBLIC-only and contract-allowlisted. Internal META, GOVERNANCE, and SCHEMA evidence can remain review support, but cannot be mistaken for public payload.
