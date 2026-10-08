# DESI SHA-256 manifest custody audit — rev0360

rev0360 closes the highest-risk local-custody gap left by rev0359 without vendoring the bulky DESI DR2 cosmology chains. The public DESI DR2 BAO cosmology-results directory contains a release-level SHA-256 manifest, so the cube now retains that checksum manifest locally and validates its syntax and accounting during lint.

## Substance added

`SOURCE-SNAPSHOT-MANIFEST.json` now marks `SSM-REF-0626-DESI-DR2-CHAIN-RELEASE-CUSTODY` as `upstream-sha256-manifest-retained` / `retained-checksum-manifest-sha256`.

The retained file is:

`payload-snapshots/REF-0626-DESI-DR2-BAO-COSMO-PARAMS/dr2_vac_dr2_bao-cosmo-params_v1.0.sha256sum`

The local record stores SHA-256, byte size, line count, checksum algorithm, manifest entry count, and top-level component-root counts. In this revision the retained DESI checksum manifest has 1,237 component entries: 765 under `cobaya/` and 472 under `iminuit/`.

This is a custody gain, not a data mirror. The MCMC chain/posterior files remain external; the cube retains only the compact upstream integrity map that lets a later operator verify downloaded DESI components against DESI-published SHA-256 values.

## Refactor/audit changes

`tools/source_snapshot_manifest.py` now distinguishes ordinary retained text payloads from retained checksum manifests. It allows a larger but still bounded checksum-manifest cap, validates every non-empty manifest line against the declared checksum algorithm, rejects absolute or parent-traversal component paths, verifies declared entry counts and root counts, and reports checksum-manifest file/entry counts in the generated audit.

`tools/source_role_negative_replay_tests.py` now includes a checksum-manifest syntax mutation. The negative replay corrupts a manifest line while updating the local file hash, byte size, and line count so generic hash drift cannot catch it; lint must fail specifically through checksum-manifest parsing.

## Non-promotion boundary

This revision changes source custody and replay checks only. It does not change route scores, authority states, promotion ceilings, empirical-delta authority, forecast realization, decision outcomes, evidence-unit scores, public-record credit, or observed-sector recovery state.

## Next risk after this pass

The next source-custody work should either retain another compact checksum/control manifest, such as GWTC companion checksum material if size and license remain acceptable, or add exact-version/public-record identity to DESI release surfaces whose landing pages can drift independently of the retained checksum file. The important rule is unchanged: retain compact integrity maps before bulky science payloads.
