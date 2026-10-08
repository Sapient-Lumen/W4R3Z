# NANOGrav md5 inventory / exact-version custody audit (rev0362)

## Decision

rev0362 upgrades `REF-0734` from an official public-data locator to exact public-record custody for the NANOGrav 15-Year Data Set timing payload.

The captured payload identity is the Zenodo record `https://zenodo.org/records/16051178`, version `2.1.0`, DOI `10.5281/zenodo.16051178`, with all-versions/concept DOI `10.5281/zenodo.7967584`. The recorded upstream component is `NANOGrav15yr_PulsarTiming_v2.1.0.tar.gz` with md5 `557d42dd8486a5f8272d90dec9b228a8`.

The NANOGrav public-data row also now inventories related public NANOGrav analysis-product records and their upstream md5s:

- noise spectra / stochastic-background sensitivity curves: `NANOGrav15yr_Sensitivity-Curves_v1.0.0.tar.gz`, md5 `5b7b0f424be2885f73fb058b28571b40`;
- KDE/free-spectrum probability-density product, latest resolved record: `NANOGrav15yr_KDE-FreeSpectra_v1.1.0.zip`, md5 `e6f1630bdd85da9f942e014846f0706c`;
- continuous-wave analysis product: `NANOGrav15yr_CW-Analysis_v1.0.0.zip`, md5 `b128fa01b8bc551ef89e7a042664659b`;
- new-physics GWB MCMC-chain product: `chains.gz`, md5 `464a0c2f2645aec4bd72cbd9f1bfb4cf`.

## Boundary

This is a custody and replay-readiness gain, not a physics promotion. The archive does not vendor the NANOGrav timing tarball, the 365 MB continuous-wave bundle, or the 22.4 GB new-physics chain archive. The manifest records exact public-record identity and compact upstream md5 values so a later replay can verify the correct payload before spending any route-local credit.

`REF-0734` remains capped at `S0`, remains denominator/source-custody pressure only, and remains outside route-head acquired support.

## Refactor added

`tools/source_snapshot_manifest.py` now validates Zenodo-style DOI/record identity and checksum syntax in `payload_inventory_records`, not only in retained local checksum manifests. `tools/source_role_negative_replay_tests.py` adds a negative replay that corrupts a payload-inventory checksum and requires source-snapshot evaluation to fail.

## Why this was prioritized

The prior locator-only NANOGrav row was the riskiest gap because PTA pressure is large, public, and easy to over-narrate. The safest forward move is exact version/md5 custody first, followed later by external-payload verification or selective small-control-file retention. This keeps public data moving into the cube without turning a bibliography locator into route credit.
