# DeriveBSD rev0603 review — dependency closure, fixture deps, Harborseal

## Aim

The riskiest remaining runtime input lie after rev0602 was that the lock/build path could bind direct package bytes while silently omitting transitive runtime inputs. rev0603 narrows that gap without adding a new doctrine or registry layer.

## Substantive runtime changes

- `tools/derive_runtime.py` now computes a finite offline fixture package dependency closure for requested packages.
- The checked-in fixture catalog makes `nginx` depend on `openssl` and `pcre2`.
- Lock, plan, artifact, explanation, and copied artifact inputs now carry the resolved closure, not only the directly requested package.
- The resolver rejects missing dependency targets, duplicate/self edges, and dependency cycles before lock evidence can be emitted.
- Artifact materialization copies every closed package byte into `inputs/packages/` and records closure metadata in `inputs/package-materials.json`.

## Focused refactor/audit

The runtime resolver and material verifier were refactored around explicit package-entry, dependency-list, closure-resolution, and package-material helpers. This reduces repeated ad hoc checks in the build path and makes the future replacement point clearer: the fixture resolver can later be swapped for a real FreeBSD pkg/base-byte resolver while preserving the same artifact carry-forward invariant.

Generated cube surfaces were refreshed only where the r628 runtime and proof-contract version bump would otherwise make evidence stale: schema audit, schema refactor backlog, hygiene checkset manifest, context pack, doc catalog, artifact index, risk index, and current runtime/hygiene docs.

## Release-critical regressions added

- Missing catalog dependency target fails before lock creation.
- Dependency cycle fails before lock creation.
- Existing rev0602 material-byte digest and mutable `:latest` workload closure regressions remain active.
- Existing rev0601 transaction-spine regressions remain active.

## Validation carried forward

- Runtime golden thread passed.
- Spec examples validated: 469.
- Release-critical hygiene ledger: 52 passed, 0 failed, 0 timed out.
- Current generated surface sync passed.
- Generated docs check passed.
- Front-door budget check passed with warnings only.
- Version check passed.
- Python bytecode artifact check passed after cleanup.

## Honest boundary

This is still fixture closure, not authoritative FreeBSD repository resolution. No real package archives, base package set, `bectl` boot-environment activation, bhyve launch, host mutation, or imported real-host proof is claimed.
