# ACT/PTA source-snapshot intake audit (rev0357)

rev0357 turns the riskiest unfinished source gap from rev0356 into executable rows rather than another doctrine note. ACT DR6 and PTA/NANOGrav enter the cube as public-source custody and S0 denominator pressure only. The change deliberately stops before acquired evidence-unit credit because payload checksums and full replay have not been retained.

## What changed

- `SOURCE-SNAPSHOT-MANIFEST.json` records six locator-only source snapshots: `REF-0729` through `REF-0734`.
- `tools/source_snapshot_manifest.py` validates that every snapshot placement names a bibliography ref, has a deterministic locator hash, carries a maximum route-credit cap, and is backed by a matching `source_role_event`.
- `PRC-ACT-DR6-MAPS-LIKELIHOODS`, `AP-ACT-DR6-CMB-LIKELIHOOD-REPLAY`, and `ED-0036-ACT-DR6-CMB-COSMOLOGY-DENOMINATOR-PRESSURE` place ACT DR6 pressure on the dark-energy/BAO and primordial-B-mode route corridors at S0 only.
- `PRC-NANOGRAV-PTA-TIMING-DATA`, `AP-PTA-HELLINGS-DOWNS-REPLAY`, and `ED-0037-PTA-NANOGRAV-GWB-DENOMINATOR-PRESSURE` place PTA/NANOGrav pressure on the gravitational-wave empirical route at S0 only.
- Route heads mirror the pressure through `route_local_handoff_only` events while keeping the new refs out of route-head `source_refs`.

## Audit finding

The previous risk was not lack of prose; it was absence of a small custody mechanism that could make public-source placement replayable. The new manifest is intentionally locator-only for this revision, so it should not be mistaken for payload preservation. This is a real improvement because the cube can now fail lint if a snapshot placement loses its typed S0 source-role event or leaks into a route head as retained source credit.

## Still missing

The next source-custody pass should capture exact upstream checksums or local hashes for public payloads where licensing and file size allow, then extend the same mechanism to GWTC, DESI, Euclid, SPT, and related public products. Durable-ledger revision-stamp decoupling remains separate: this revision still mutates top-level `revision` fields because current lint requires manifest alignment.

## Non-promotion boundary

No route score, authority state, promotion ceiling, decision outcome, forecast realization, evidence-unit score, public-record credit, or observed-sector recovery state is promoted by this intake. `REF-0729` through `REF-0734` are S0 pressure/custody only.
## rev0358 payload-custody extension note

rev0357 made ACT DR6 and PTA/NANOGrav visible as source-snapshot custody pressure. rev0358 keeps that lane unchanged and broadens the manifest machinery to older route-critical public data products. The important design change is that the manifest now distinguishes upstream checksum custody, inventory/no-checksum custody, local non-retention, bulky external products, and zero-route-placement watchlist receipts. ACT/PTA still do not receive route promotion from this machinery.

