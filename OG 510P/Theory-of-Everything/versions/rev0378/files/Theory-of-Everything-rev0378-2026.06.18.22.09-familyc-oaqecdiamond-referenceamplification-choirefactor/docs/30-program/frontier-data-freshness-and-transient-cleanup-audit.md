# Frontier data freshness and transient-cleanup audit — rev0318

## Scope

This revision targets two high-risk failure modes that are substantive rather than doctrinal:

1. live empirical-pressure rows becoming stale while still acting like current frontier constraints; and
2. cloudtainer/tool reuse leaving local transient bytecode that causes otherwise valid lint/package cycles to self-poison.

No route is promoted by this audit. The work updates source custody, replay hygiene, and caution boundaries only.

## Gravitational-wave freshness repair

The live gravitational-wave empirical delta formerly pointed at a `GWTC-4.0` handle. `rev0318` advances that handle to `ED-0004-GWTC5-STRONGFIELD-GR-CONSTRAINTS` and adds `REF-0624` and `REF-0625` across the relevant gravitational-wave carrier, acquisition, severity, evidence-unit, measurement-model, and decision-experiment rows.

The state remains capped at `S2`. GWTC-5.0 improves the public strong-field/dynamical-GR constraint record, but it does not by itself create a candidate-native Theory-of-Everything witness. The inverse map from catalog-level waveform/deviation/population/systematic constraints to a particular ontology remains many-to-one.

## DESI DR2 source-custody update

`REF-0626` is added to the DESI DR2 late-time-expansion corridor, its likelihood replay protocol, public-record carrier, severity row, evidence unit, and measurement model. The important repair is custody of released cosmology chains/data products, not route promotion.

The DESI row remains `S2` because the pressure surface is parameterization-, nuisance-, combination-, and inverse-map-dependent.

## Euclid and CERN watchlist boundaries

`REF-0627` is recorded as a Euclid Q1 public-data watchlist/custody reference, not as dark-energy evidence. Q1 should not be spent as a cosmology-release witness unless a future cube revision binds it to a named cosmology likelihood/product with the relevant systematics and public replay surface.

`REF-0628` is recorded as accelerator-schedule pressure only. Run schedules can affect when public records arrive, but schedule status is not evidential support.

## Route-pressure cross-repair

This same revision also hardens decision/forecast pressure in `docs/30-program/decision-forecast-route-pressure-integrity-audit.md`. The connection matters because frontier-source freshness only counts if the relevant rows actually touch route authority. `rev0318` therefore treats live source custody, route-facing forecast/decision pressure, and transient-free packaging as one release-control bundle rather than three disconnected inventories.

## Cloudtainer self-poisoning repair

Direct Python tool imports/runs can leave `__pycache__` or `.pyc` files in the project tree. The archive linter correctly rejects those transients, but that created a wasteful local failure mode: a valid tree could become invalid merely because a validation tool had been imported during inspection.

`rev0318` adds `tools/clean_transients.py`, a `make clean` target, and clean-first `make lint` / `make package` behavior. `tools/package_release.py` also removes transient files before writing the zip, so the packaged release is protected even after exploratory tool use.

## Non-promotion rule

Fresh public sources update custody and pressure surfaces. They do not discharge candidate-native proof obligations, independence assumptions, inverse-map debt, or promotion gates. This revision therefore keeps the route state unchanged.

## Followthrough executed in rev0319

The very small frontier-source freshness check now exists as `FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json` plus a generated audit. It scans only named rows that already spend current public frontier-source language, and it keeps watchlist-only sources out of evidential promotion.
