# ACT DR6 inventory-control replay audit (rev0363)

## Why this was the next risky gap

After rev0362, ACT DR6 remained the largest locator-only public-data pressure surface in the source-snapshot manifest. The cube had already retained compact checksum or inventory controls for DESI, GWTC, SPT, and NANOGrav, but `REF-0729` and `REF-0731` still depended on public landing-page locators. That was too weak for a large CMB release whose public surfaces include maps, beam files, NILC products, passbands, PSPIPE spectra/covariance/SACC products, MCMC-chain groups, NERSC chain access, and a separate ACT DR6 lensing-likelihood payload.

The risk was not that ACT DR6 should promote a route. The risk was that a future restart could treat a landing page as if it were already a stable product inventory. rev0363 corrects that by retaining a compact inventory-control artifact and making its semantics executable.

## What is retained

rev0363 adds two local control files:

- `payload-snapshots/REF-0729-ACT-DR6-DATA-PRODUCTS/act_dr6.02_lambda_inventory.control.json`
- `payload-snapshots/REF-0731-NASA-LAMBDA-ACT-DR6-LENSING/act_dr6_lensing_likelihood_inventory.control.json`

The first file records 88 ACT DR6.02 inventory entries: release anchors, LAMBDA product groups, selected passband/PSPIPE downloadable files, MCMC-chain model-group summaries, detailed LCDM chain files, and detailed tensor/r chain files. The second records three ACT DR6 lensing-likelihood entries: the LAMBDA tarball identity, the product-description data classes, and the public software locator.

These are local control inventories, not science payload mirrors. No map files, likelihood tarballs, MCMC chains, notebooks, NERSC trees, or code checkouts are vendored.

## Validator/refactor change

`tools/source_snapshot_manifest.py` now recognizes `retained-inventory-control-sha256` and `inventory_control_json` records. The validator checks local SHA-256, byte size, line count, JSON syntax, `source_ref` binding, capture date, source-page locators, entry count, entry category counts, unique entry IDs, entry component names, route-credit cap, payload-retention vocabulary, and row-level `payload_inventory_records` coverage against retained inventory entries.

The generated source-snapshot audit now reports local inventory-control file and entry totals in addition to retained payload, checksum-manifest, and component-checksum counts.

## Negative replay

`tools/source_role_negative_replay_tests.py` now includes an inventory-control semantic drift case. The negative replay mutates a retained inventory-control JSON entry from `S0` to `S1` while updating the local SHA-256, byte size, and line count in the manifest so generic file-hash custody still passes. Source-snapshot validation must still fail on semantic inventory drift.

That is the intended boundary: a local file hash proves bytes, but the cube also has to prove that the retained control file still says what the route-cap and custody machinery think it says.

## Boundary retained

No route score, authority state, promotion ceiling, empirical-delta authority, forecast realization, decision outcome, evidence-unit score, public-record credit, or observed-sector recovery state changes in rev0363.

ACT DR6 remains S0 denominator/source-custody pressure. The new inventory-control files make the public product inventory more replayable; they do not make ACT DR6 a candidate-native ToE support source, a dark-energy ontology result, or a primordial-tensor detection.

## Remaining gap

The next ACT-specific risk is exact payload/checksum identity. rev0363 records product inventory without upstream payload checksums. A later revision should only advance ACT custody if it can retain small upstream control/checksum files, pin exact payload/version identities, or execute a bounded route-local likelihood replay. More prose about ACT would be wasteful unless it is tied to executable replay.
