# Public payload custody gap audit — rev0358

> Supersession note (rev0359): the SPT-3G LAMBDA bandpower surface is no longer only inventory/no-checksum custody. rev0359 retains the two small text bandpower files locally with SHA-256 replay and records GWTC-5 exact Zenodo v2 payload identity. This rev0358 audit remains as the historical gap baseline.

## Scope

This audit records the substance-first correction made in rev0358: the source-snapshot manifest no longer stops at the newly-added ACT DR6 and PTA/NANOGrav lane. It now covers older route-critical public data surfaces that already influence the cube's public-record and frontier-freshness machinery: GWTC-5, DESI DR2 cosmology chains, SPT-3G B-mode products, and Euclid Q1.

The goal is not to create another registry layer. The goal is to make the following distinctions executable:

- a locator exists, but no payload is retained locally;
- an upstream payload checksum exists and is recorded;
- only product inventory is recorded because no upstream checksum was captured here;
- a public data release is intentionally zero-placement watchlist custody rather than route-bearing evidence.

## What changed

`SOURCE-SNAPSHOT-MANIFEST.json` now carries payload-custody fields on every row:

- `payload_custody_state`
- `upstream_checksum_state`
- `local_payload_state`
- optional `payload_locator`
- optional `payload_component_checksums`
- optional `payload_inventory_records`
- optional `zero_route_placement_receipt`

`tools/source_snapshot_manifest.py` now validates those fields, prints checksum/local-retention accounting in the generated audit, and allows an empty `row_placements` list only when a frontier-source freshness receipt explicitly proves that the source is a zero-route-placement watchlist item.

## Source decisions

### GWTC-5 / O4b

`SSM-REF-0629-GWTC5-O4B-OPEN-DATA-PAYLOAD-CUSTODY` records the GWTC-5 public payload locator and upstream md5 component checksums published with the candidate-data release. The local payload state is `not-retained-bulky-external`; rev0358 does not vendor the multi-file public release into the archive.

This is a custody improvement, not a scientific promotion. The row placements remain inherited from the existing GW public-catalog custody pathway and carry `no-new-credit` caps.

### DESI DR2 cosmology chains

`SSM-REF-0626-DESI-DR2-CHAIN-RELEASE-CUSTODY` and `SSM-REF-0688-DESI-DR2-CHAIN-POSTERIOR-DOC-CUSTODY` record public chain/posterior inventory and the boundary that the archive has not captured upstream checksums here. They deliberately do not imply custody of underlying spectra/redshifts or a new dark-energy claim.

This keeps DESI DR2 as public-chain custody / acquired support already capped by route rows, not as a fresh route-promotion source.

### SPT-3G B-mode products

`SSM-REF-0641-SPT3G-BMODE-DATA-PRODUCTS-CUSTODY` and `SSM-REF-0642-SPT3G-LAMBDA-BANDPOWERS-LIKELIHOOD-CUSTODY` record product inventories for likelihood code and bandpower/likelihood data surfaces. No upstream checksum was captured in this pass, so the rows use `upstream-file-inventory-no-checksum` rather than pretending the locator equals payload integrity.

This is especially important because CMB B-mode products can be narratively over-weighted. The source-snapshot layer now says exactly what the archive has: public-product custody metadata, not payload hashes and not route credit.

### Euclid Q1

`SSM-REF-0627-EUCLID-Q1-ZERO-PLACEMENT-WATCHLIST` records Euclid Q1 as zero-route-placement watchlist custody. Its `zero_route_placement_receipt` is backed by `FSF-0003-RCP-REF-0627-EUCLID-Q1-WATCHLIST`, and the source-snapshot validator checks that the ref does not appear on route rows or route events.

This corrects a high-risk ambiguity: Euclid Q1 can be important public data and still not be a cosmology-result source inside this cube.

## What still needs work

The manifest is now strong enough to expose where payload custody is absent, but it still does not retain local payload hashes for the large public products. The next non-bureaucratic improvement should be a small-file hash pilot: choose a few small, license-compatible text/control files from SPT-3G, DESI, or a GWTC companion record; retain local SHA-256 values; and prove that the source-snapshot audit catches checksum drift without vendoring huge external archives.

The second remaining risk is mutable public-record identity. GWTC-5 has versioned public records; the cube now records the payload/checksum locator it used, but future work should decide how latest-version DOI redirects, version-specific records, and human-readable release pages are represented without changing route authority.

## Non-promotion boundary

rev0358 changes custody accounting and validation only. It does not change any route score, route authority state, promotion ceiling, empirical-delta authority, decision outcome, forecast realization, evidence-unit score, public-record credit, or observed-sector recovery state.
