# Session review — rev0872

## Work selected

The session prioritized a demonstrated read/write redirection defect over another doctrine surface. Exact-byte recovery was still attempted, but no candidate was admitted without a complete path-specific index match.

## Delivered

- Reproduced rev0871 root substitution against the exact parent script hashes: materialization wrote to a replacement directory, and coverage hashed replacement bytes.
- Added `scripts/root_anchor.py` and carried one captured root identity through coverage, recovery-target validation, and materialization.
- Closed an already-exact early-return hole found while testing the refactor.
- Replaced alias-normalizing path checks across the active gate, integrity, overlay-chain, patch recovery, and history recovery surfaces.
- Added four deterministic root-swap regressions plus stable-root and symlink-root controls.
- Caught and fixed an integrity-validator self-mutation during finalization; six entrypoints now activate no-bytecode policy before local imports, with nine isolated execution probes.

## Byte recovery result

No new exact canonical byte stream was proven. Coverage remains 109 exact current-path files and 125 rehydratable files. The sibling-bundle, patch/history, adjacent OCF output, and public-search routes did not produce a candidate meeting path, size, and full SHA-256 together.

## Highest remaining risks

Owner-approved root/component rights, all 17 selected StreamFold payloads, canonical `README.md`, and 4,461 unavailable canonical files remain open.
