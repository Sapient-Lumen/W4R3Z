# 889 — Public-fingerprint tool-safety gate and release-inventory refactor

**Track:** Shared / Release gate / Verifier

rev0860 adds `scripts/check_public_fingerprint_tool_safety.py` to the release-gate inventory.

The check exercises direct public-fingerprint report and compare CLIs, not only the strict verifier wrapper. A reviewer comparing mirrored or forwarded packets directly must not receive a clean `MATCH` when one side was reached through an unsafe public route. `tools/compare_public_fingerprints.py --json` now returns `UNSAFE_WARNING` with a nonzero exit code when either side carries public-fingerprint warnings.

Boundary: this is an executable release-gate safety check, not proof of live publication governance or signer authority.
