# Validation toolchain manifest

This generated guide makes the `make lint` admission wrapper inspectable without turning it into a certification authority.
It pairs with `VALIDATION-TOOLCHAIN-MANIFEST.json`, which records ordered tool scripts, support modules, entrypoints, sizes, and SHA-256 hashes.

## Non-claim
This is not a lint-sovereign, validation-score-sovereign, hash-governance-court, toolchain-certification-tribunal, or manifest-notary-authority; it records toolchain identity and hashes for audit only.

## Counts
- Ordered lint tools: 217
- Support modules: 37
- Entrypoints: 4

## Entrypoints
- `tools/run_lint_suite.py` — admission-entrypoint — `326f390aca5c7739…`
- `tools/package_release.py` — release-entrypoint — `7f73e398061b8204…`
- `Makefile` — command-surface — `2b4ed9b4839b7a32…`
- `VALIDATION-INDEX.json` — coverage-index — `50ecc1f786c37b7f…`

## First and last ordered lint tools
- First: `tools/check_discovery.py`
- Last: `tools/check_mechanism_pressure_register_contract.py`

## Use
Use this manifest to detect admission-wrapper drift, support-module edits, and generator/checker identity changes. Do not use it as a review court or proof that the archive is semantically correct.
