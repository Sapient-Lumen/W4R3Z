# 897 — Public-fingerprint oversized public-file and prefix-hash firewall

**Track:** Shared / Verifier / Release gate

rev0862 advances `tools/public_fingerprint_report.py` to profile `1.4`. The substantive change is that oversized public files are no longer represented by a truncated/prefix hash. They are rejected from the public-fingerprint entry list and emit a stable warning:

`file_exceeds_max_include_bytes_rejected_for_hash:<relpath>:max_bytes=<n>`

Strict verification-policy authentication already fails closed on any public-fingerprint warning, so a packet with a large public `README.txt`, note, envelope, or object cannot accidentally satisfy a policy through a digest that only commits to the first bytes.

Executable checks:

- `scripts/check_public_fingerprint_tool_safety.py` creates an oversized public `README.txt`;
- the helper emits the oversize warning;
- `--include-file-hashes` does not include the oversized public file;
- `tools/compare_public_fingerprints.py` reports `UNSAFE_WARNING`, not `MATCH`, when either side has the oversize warning.

Boundary: this is a bounded publishable-fingerprint safety check. It is not a filesystem sandbox, private-evidence integrity proof, certification claim, legal-authority proof, production publication governance, or live-pilot authorization.
