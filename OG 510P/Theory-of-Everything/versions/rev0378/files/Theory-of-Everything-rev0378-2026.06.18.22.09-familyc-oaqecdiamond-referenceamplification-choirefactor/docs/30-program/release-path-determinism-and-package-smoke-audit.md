# Release path determinism and package-smoke audit — rev0319

## Scope

This revision targets a release-boundary failure mode rather than a new scientific registry. The cube had strong source-tree checks, but the packaging command itself was too weak: an operator could run `make package` after editing ledgers without first regenerating generated surfaces or running lint/schema validation. That created a path for a stale but neatly zipped cube.

No route is promoted. This revision hardens the mechanics by which a revision becomes a linked continuation object.

## Failure mode found

Before this pass, `make package` cleaned transients and wrote a zip. It did not itself require `make index` or `make lint`. The intended manual sequence was known, but the release boundary did not enforce it.

That matters because `AUTHORITY-DEPENDENCY-GRAPH.json`, generated summaries, release freshness audits, schema validation, and route-pressure checks are only protective if the package path actually runs them before emitting the zip. A convenience zip command can otherwise preserve exactly the stale generated surfaces the earlier revisions were built to eliminate.

## Repair implemented

`rev0319` makes `make package` depend on `index` and `lint`, then build and smoke-test the zip:

1. `make index` regenerates source-replayed generated surfaces.
2. `make lint` runs transient cleanup, archive lint, and registered JSON Schema validation.
3. `tools/package_release.py` writes a deterministic zip.
4. `tools/smoke_package_release.py` extracts the zip, runs `make lint` inside the extracted package, rebuilds the package from extracted contents, and requires a byte-identical SHA-256 digest.

The release path is now executable proof that the linked artifact is not merely present but replayable from its own contents.

## Deterministic packaging refactor

`tools/package_release.py` now writes archive members in canonical sorted path order and fixes zip metadata from the manifest timestamp. It also treats nested `.zip` files as release transients so stale bundles cannot hitchhike into a new release payload.

This closes a cloudtainer waste path: old packages, debug zips, or accidental nested release bundles should not inflate or contaminate the next linked revision.

## Package-smoke behavior

`tools/smoke_package_release.py` checks four practical properties:

- every zip member stays under the canonical release root;
- no transient bytecode, cache directory, or nested zip is retained;
- the extracted package passes `make lint`; and
- the extracted package rebuilds to the same zip digest.

The smoke test is intentionally end-to-end. It is not another registry. It proves that a recipient can unpack the artifact and recover the same release bytes with the packaged tools.

## Non-promotion rule

Release determinism is scientific hygiene, not scientific evidence. A byte-identical, lint-clean package can still contain weak routes, failed inverse maps, stale physical assumptions, or insufficient empirical pressure. This revision protects continuity and auditability only.

## Follow-on executed in this linked revision

The stale-source scan was executed immediately after the release-path repair, and it stayed intentionally narrow. `FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json` covers only volatile public frontier sources currently spending custody or empirical-pressure language, and lint now rejects drift between those assertions, the named rows, and the generated audit.

The rule remains: update live executable rows when a current public artifact clearly supersedes the row's named release; do not turn watchlists into evidence.

## Frontier custody addition

This revision also tightens the highest-value live empirical source row touched in rev0318: GWTC-5 strong-field custody now requires the direct O4b/GWOSC open-data release reference (`REF-0629`) in addition to catalog/news custody references. This is custody and replay pressure only; it does not promote any route.
