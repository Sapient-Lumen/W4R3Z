# DeriveBSD rev0604 session review — payload projection, catalog drift, Lynx

Revision package: `DeriveBSD-rev0604-2026.06.18.10.10-payloadprojection-catalogdrift-lynx.zip`
Semantic cube cut: `2026-06-18r629`

## Intent

Continue from rev0603 without adding another doctrine or registry layer. The riskiest remaining runtime lie after direct package material binding and finite dependency closure was that the catalog still duplicated dependency and identity metadata already present in the consumed fixture package bytes. A stale hand-authored catalog row could claim closure evidence that did not match the package payload it supposedly described.

## Substance shipped

- Made checked-in runtime package fixture payloads the metadata source of truth for the offline fixture resolver.
- Added runtime verification that each package payload binds `package_id`, `platform`, `origin`, `version`, `runtime_dependencies`, fixture-only truth flags, and the current cube cut before lock evidence is issued.
- Changed the runtime truth claim to `finite-offline-fixture-catalog-projection-plus-payload-verified-closure-and-bytes-not-a-package-index-resolution` so the prototype remains explicit about what it is and is not proving.
- Added `package_payload_metadata_policy` and `fixture_payload_digest` through lock, plan, artifact material manifest, sealed inputs, activation surface, and explain output.
- Added a release-critical regression for catalog/payload dependency drift.
- Reworked the missing-dependency and dependency-cycle regressions so they mutate package payloads and refresh catalog projections, testing resolver behavior rather than stale catalog lies.
- Refactored package/material handling around explicit fixture-payload decoding, material verification, dependency validation, and closure helpers in `tools/derive_runtime.py`.

## Audit/refactor performed

The audit target was the runtime fixture repository boundary. The refactor reduced duplicate catalog truth by projecting identity/dependency claims from package payloads and by making catalog rows prove agreement with consumed bytes. This is intentionally still a fixture repository, but it is closer to the shape of a future real FreeBSD resolver: resolver metadata must agree with material bytes before lock evidence exists.

A small front-door cleanup also avoided increasing the index budget: the r629 `docs/00-index.md` release note was shortened and excess blank release-history separators were removed rather than raising `tools/baselines/frontdoor_budget.json`.

## Evidence refreshed

- `validation/runtime-package-catalog/current/catalog.json`
- `validation/runtime-materials/current/packages/*.pkg`
- `validation/runtime-golden-thread/current/run.summary.json`
- `validation/runtime-golden-thread/current/workspace/`
- `spec/examples/cube.hygiene.run.ledger.json`
- cube generated summaries and generated docs
- FreeBSD host-proof contract examples, proof bundle, and current real-host work order surfaces after the r629 cut
- `README.md`, `CHANGELOG.md`, `docs/00-index.md`, `docs/110-juicy-os-lessons.md`, and current operator/runtime docs

## Validation

- Runtime golden thread: passed.
- Spec examples: 469 validated.
- Release-critical hygiene ledger: 52 checks completed, 52 passed, 0 failed, 0 timed out.
- Generated docs: synced.
- Generated artifact release IDs: synced to `2026-06-18r629`.
- Current generated surface sync: passed.
- Discovery, latest-cut, version, front-door budget, and last-updated checks: passed.
- Python bytecode artifact check: clean.

## Honest boundary

This revision still does not resolve real FreeBSD repository metadata, consume actual pkg/base archives, construct a boot environment, call `bectl`, launch bhyve, mutate a host, or import a real FreeBSD proof. It only tightens the fixture repository so false catalog metadata cannot become runtime evidence.

## Recommended next cut

Move from fixture-payload projection toward one real resolver-shaped repository snapshot: signed/freshness-bound repository metadata, exact package/base archive hashes, and a network-denied build path that can carry those real bytes into the same artifact/evidence chain. Do not add more registry surface until at least one real package/base byte path exists.
