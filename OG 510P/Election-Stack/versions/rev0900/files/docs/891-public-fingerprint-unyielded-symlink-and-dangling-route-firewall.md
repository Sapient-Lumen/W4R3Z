# 891 — Public-fingerprint unyielded-symlink and dangling-route firewall

**Track:** Shared / Verifier / Release gate

rev0861 advances the bounded public-fingerprint helper to profile `1.3`. The substantive change is that public-surface symlinks the normal include iterator could skip are now warning surfaces instead of collapsing into ordinary missing-file semantics.

Executable behavior:

- dangling root public files such as `README.txt` symlinks emit `file_symlink_rejected_for_hash:<relpath>`;
- dangling or otherwise unyielded `notes/**/*.md|txt` symlinks emit stable file-symlink warnings;
- unyielded nested public-directory symlinks under `notes/` emit stable directory-symlink warnings;
- `tools/compare_public_fingerprints.py` returns `UNSAFE_WARNING`, not a plain mismatch or match, when either side carries those warnings;
- strict verification-policy authentication remains fail-closed on any public-fingerprint warning.

Audit: `artifacts/reports/public-fingerprint-unyielded-symlink-audit-rev0861.json`.

Boundary: this is route-safety for a bounded public fingerprint. It is not a filesystem sandbox, certification claim, legal-authority proof, or production trust-root proof.
