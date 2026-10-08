# Frontier-source freshness core-custody audit — rev0319

## Scope

This is a narrow executable freshness repair, not a general source registry. It checks only volatile public frontier sources that currently spend custody, empirical-pressure, or forecast-runway language inside route-critical rows.

The canonical assertion set covers five surfaces: GWTC-5/GWOSC O4b strong-field custody, DESI DR2 cosmology chains/data products, Euclid Q1 plus CERN schedule watchlist boundaries, CMB-S4 closeout custody, and LISA construction/prototype runway custody.

## Failure modes found

`rev0318` refreshed several top-level GWTC-5 and DESI DR2 rows, but the refresh did not initially reach all rows that carry stale scientific-pressure risk. Systematics, calibration, likelihood, prior, and contrast rows can continue to shape route interpretation after the visible carrier/evidence row has been updated.

A second, more severe failure appeared during the rev0319 audit: a CMB-S4 freshness assertion can pass syntactically while using a wrong-domain source ref. The direct LIGO/GWOSC O4b open-data reference is correct for GWTC-5 rows, but wrong for CMB-S4-specific closeout/forecast-realization rows.

## Repair implemented

`rev0319` adds `FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json` and `tools/frontier_source_freshness.py`. `make index` writes `docs/30-program/frontier-source-freshness-audit.generated.md`, and lint rejects assertion failures or generated-audit drift.

The tool now checks both required refs and forbidden refs. CMB-S4-specific rows require the official CMB-S4 status/closeout ref and reject the LIGO/GWOSC O4b ref where it would be semantically wrong.

The generated audit checks `41` required source-carrying rows across `5` assertions and reports zero freshness failures.

## Boundary discipline

Freshness is not promotion. A current public catalog, likelihood product, project-status page, construction milestone, prototype-hardware note, or schedule update can repair custody and make stale-row drift visible, but it does not solve inverse-map ambiguity, candidate-native witness obligations, systematic dependence, prior dependence, comparison-denominator debt, or route-promotion gates.

Euclid Q1, CERN schedule, CMB-S4 closeout, and LISA runway rows remain custody/timing/forecast-realization boundaries. They are not evidence for a route until a later revision binds them to named public products, systematics, and replayable likelihood surfaces.
