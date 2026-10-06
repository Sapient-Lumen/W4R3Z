# DeriveBSD-rev0602-2026.06.18.09.09-materialbytes-pinnedclosure-otter review

## Cut intent

This cut continues the runtime-first recovery from rev0600/rev0601. The riskiest remaining lie was that the runtime lock named packages and a microVM image without binding consumable software bytes. r627 moves that seam forward without pretending to have a real FreeBSD package/base resolver.

## Substantive changes

- `tools/derive_runtime.py` now verifies package material bytes from `validation/runtime-materials/current/packages/` against catalog-bound repo-relative paths, sha256 digests, and byte sizes.
- The runtime artifact now carries copied package input bytes under `inputs/packages/` and records them in `inputs/package-materials.json` before sealing and tree-manifest hashing.
- `spec/examples/microvm.spec.json` now uses a digest-pinned microVM closure; the runtime rejects `:latest` and any closure lacking `@sha256:<64 lowercase hex>`.
- `validation/runtime-package-catalog/current/catalog.json` now describes an offline fixture catalog plus checked-in fixture byte material. This is still explicitly not an authoritative FreeBSD package index.
- `tools/check_runtime_golden_thread.py` now mutates a package material digest and a mutable `services/nginx:latest` closure to prove the new guards fail closed.

## Audit/refactor

The audit/refactor stayed intentionally small. Runtime material handling is centralized behind material path, digest, and size verification helpers, while generated docs and front-door index text were refreshed or compacted only where stale evidence or budget failures would otherwise make the cut dishonest. I did not add a schema family, registry, ADR, or broad doctrine lane.

## Evidence

- `tools/check_runtime_golden_thread.py`: passed.
- `tools/validate_spec_examples.py`: passed, 469 examples.
- `tools/hygiene.py --profile release-critical --ledger-json spec/examples/cube.hygiene.run.ledger.json --timeout-seconds 180`: completed via resumable chunks; 52 passed, 0 failed, 0 timed out.
- `tools/check_current_generated_surface_sync.py`: passed against the completed r627 ledger.
- `tools/check_generated_docs.py`, `tools/check_discovery.py`, `tools/check_version.py`, and `tools/check_frontdoor_budget.py`: passed. The front-door budget still warns that the index and LLM runbook are above their old observed byte baselines, but they remain within enforced budgets.
- `tools/check_no_python_bytecode_artifacts.py`: passed after transient `__pycache__` cleanup.

## Honest boundary

This cut still uses fixture bytes. It does not resolve FreeBSD repository metadata, consume real FreeBSD package/base archives, create a boot environment, switch `bectl`, launch bhyve, mutate a host, or import real-host proof. The next high-value step is an authoritative FreeBSD byte resolver that can replace the fixture catalog while preserving the same lock/build/artifact carry-forward invariant.
