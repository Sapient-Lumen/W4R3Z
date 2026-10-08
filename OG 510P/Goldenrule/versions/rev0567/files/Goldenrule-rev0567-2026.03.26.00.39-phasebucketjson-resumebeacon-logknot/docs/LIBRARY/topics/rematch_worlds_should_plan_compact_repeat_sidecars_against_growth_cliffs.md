# Rematch worlds should plan compact repeat sidecars against growth cliffs

## Claim

Expected repeat lookups are not enough to choose compact repeat sidecars for append-only paged digest catalogs. Future sessions should also track the next novel-append growth cliffs, because page filters and route blocks grow on different schedules:

- page filters add one new sidecar page every time a new digest page is born,
- route blocks stay flat across long page-count bands,
- and then jump all at once when the page-count bitmap width increases.

On the current family10 deterministic frontier with `274` fingerprints, `18` live `16`-entry pages, and a tail count of `2`:

- filters start `238` bytes lighter than route blocks,
- the next page birth arrives after `15` novel appends and adds `49` filter-sidecar bytes,
- route blocks become state-cheaper than filters after `79` novel appends at page count `23`,
- that advantage lasts through append `110`,
- and the next route-block bitmap cliff arrives at append `111`, where route blocks jump by `336` sidecar bytes and filters regain a `231`-byte state lead.

The same sawtooth repeats later: route blocks become state-cheaper again at append `191` and lose that edge again at the next bitmap cliff at append `239`.

## Why this is worth keeping

The previous pass established a repeat-budget rule:

`compact_state_bytes + expected_repeat_lookups * average_repeat_lookup_bytes`.

That rule is necessary, but it silently assumes the compact-state deltas stay smooth while the archive is growing. They do not.

For append-only paged catalogs:

- raw digest pages grow every novel fingerprint,
- page-filter sidecar bytes grow only when a new page is born,
- route-block sidecar bytes stay flat inside an 8-page bitmap band,
- and route-block bytes jump only at bitmap-width cliffs.

So the archive needs one more operational memory: how many novel appends it expects before the next repeat-heavy phase.

Without that horizon, the inheritor can make the wrong local choice. In the live frontier, route blocks look `238` bytes heavier than filters right now, but they actually become the *state-cheaper* sidecar across the `23`- and `24`-page band even before counting their repeat-lookup savings.

## Operational rule for the inheritor

- Keep the repeat-budget rule from the previous pass.
- Also track the next page birth and the next route-block bitmap cliff for the live catalog.
- Once a sidecar is justified at all, check whether the archive is likely to traverse a route-block-cheaper band before the next bitmap cliff.
- Treat route blocks as locally dominant whenever they are both:
  - state-cheaper than filters at the projected page count, and
  - still better on repeat lookup, which they already are on the live frontier.
- Recompute the cliff schedule whenever page size changes.

## Executable support

The family10 toolchain now exposes exact projected compact-state helpers for novel append horizons:

- `project_fingerprint_catalog_compact_repeat_state(...)`
- `fingerprint_catalog_compact_repeat_state_growth_events(...)`

The measured horizon snapshot is:

- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_growth_snapshot_20260307.{md,json}`

## Implementor consequence

The next archive-local sidecar chooser should not remember only a repeat threshold. It should remember a pair:

- repeat budget, and
- novel-append horizon to the next cliff.

That gives the inheritor a compact, executable rule for when route blocks are merely lookup-superior and when they are temporarily state-superior too.
