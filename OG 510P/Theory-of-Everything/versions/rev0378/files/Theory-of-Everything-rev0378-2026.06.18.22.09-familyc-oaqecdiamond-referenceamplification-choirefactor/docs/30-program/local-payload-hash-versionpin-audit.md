# Local payload hash / version-pin audit — rev0359

> Supersession note (rev0360): the DESI DR2 BAO cosmology release now retains its upstream SHA-256 checksum manifest locally and parses it during negative replay; this rev0359 audit remains the first local-payload pilot baseline.

rev0359 closes the highest-risk gap left by rev0358: the archive could say that a public payload existed, but only bulky GWTC-style releases had upstream component checksums and the lighter SPT/DESI surfaces were still inventory-only. This revision adds a deliberately small executable pilot rather than broad payload mirroring.

## Substance added

`SOURCE-SNAPSHOT-MANIFEST.json` now has a local retained-payload path for the NASA LAMBDA SPT-3G B-mode lane. The two small text bandpower files are retained under:

- `payload-snapshots/REF-0642-SPT3G-LAMBDA-BANDPOWERS/bandpowers_err_BK_Mask.txt`
- `payload-snapshots/REF-0642-SPT3G-LAMBDA-BANDPOWERS/bandpowers_err_Edge.txt`

The manifest records each local file's source locator, source component name, SHA-256, byte size, line count, and custody note. `tools/source_snapshot_manifest.py` recomputes these values during lint, so local corruption or stale declared hashes now fail closed.

This is intentionally not a general vendoring policy. The 111.8 MB SPT likelihood tarball remains external, and GWTC-5 / DESI bulky payloads remain external. The pilot proves the control path on tiny, public, route-relevant text payloads before the cube attempts larger payload preservation.

## GWTC-5 exact-version correction

The GWTC-5 custody row now distinguishes exact captured identity from latest-pointer behavior. rev0358 recorded the older Zenodo v1 payload locator. The public Zenodo record now advertises a newer v2 record, and rev0359 records the exact captured v2 record id, v2 DOI, latest pointer, latest resolved record, and v2 component md5 checksums.

This correction matters because a future operator should not refresh a public data product by following a latest URL and then believe they are still checking the same payload. `payload_record_identity` is now an executable manifest field for versioned public records, and negative replay deletes it to prove lint fails.

## Refactor/audit changes

`tools/source_snapshot_manifest.py` now validates:

- `local_payload_records` path safety under `payload-snapshots/`;
- local SHA-256 drift;
- local byte-size and line-count drift;
- a small-text retention cap for retained local payloads;
- exact captured record identity for Zenodo-style versioned payload records;
- latest-pointer versus exact-version separation.

The generated audit now reports local retained payload file count and retained payload byte count. In rev0359 that count is 2 files / 1,768 bytes.

`tools/source_role_negative_replay_tests.py` now has 15 cases. The new cases mutate a retained local payload and remove versioned public-record identity from the source snapshot manifest. Both must be detected before lint can pass.

## Non-promotion boundary

This revision changes custody and replay only. It does not change any route score, authority state, promotion ceiling, empirical-delta authority, forecast realization, decision outcome, evidence-unit score, public-record credit, or observed-sector recovery state.

## Next risk after this pass

The next useful expansion is another small-file local hash, not a large mirror. Good targets are a DESI README/control/likelihood-index file or a GWTC md5 manifest if licensing and size remain compatible. The exact-version identity field should also be extended to other DOI/latest-style records before broad checksum refreshes.
