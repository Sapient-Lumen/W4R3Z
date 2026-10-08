# 899 — Public-fingerprint non-file route and oversize audit

**Track:** Shared / Verifier / Release gate

rev0862 adds the missing executable boundary for public routes that exist but are not regular files. A same-selector packet can no longer replace a publishable surface such as `README.txt`, `notes/*.md`, `envelopes/*.envelope.json`, or `objects/*.json` with a directory or other non-file and have the route collapse into ordinary absence.

The public-fingerprint helper now emits:

`non_file_public_surface_rejected_for_hash:<relpath>`

and the strict policy path continues to fail closed on any public-fingerprint warning. The same audit also records the profile-1.4 oversize behavior:

`file_exceeds_max_include_bytes_rejected_for_hash:<relpath>:max_bytes=<n>`

Audit artifacts:

- `artifacts/reports/public-fingerprint-nonfile-and-oversized-route-audit-rev0862.json`
- `artifacts/reports/public-fingerprint-nonfile-and-oversized-route-audit-rev0862.csv`
- `artifacts/reports/public-fingerprint-nonfile-and-oversized-route-audit-rev0862.md`

Boundary: this is bounded synthetic public-fingerprint safety only. It is not a filesystem sandbox, private-evidence integrity proof, production publication governance, legal reliance, current voter instruction, certification, or live-pilot authorization.
