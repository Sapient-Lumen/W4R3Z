# Rematch worlds should choose compact repeat sidecars by expected repeat budget

## Claim

Once the archive keeps append-only paged raw-digest fingerprint catalogs, it should stop inheriting the strongest compact repeat sidecar by default. Instead, it should choose between bare pages, aligned page filters, and digest-byte route blocks by the measured objective

`compact_state_bytes + expected_repeat_lookups * average_repeat_lookup_bytes`.

Under the current family10 deterministic frontier with the live `16`-entry page layout:

- bare pages win only for very cold catalogs,
- page filters become worthwhile after about `0.185996` expected repeats,
- and route blocks become worthwhile after about `0.650001` expected repeats beyond the filtered state.

## Why this is worth keeping

The previous passes proved three separate things:

- paged raw-digest catalogs are the right durable state for repeat references,
- aligned page filters sharply reduce repeat lookup without much extra state,
- and route blocks reduce repeat lookup further by avoiding the linear filter scan.

But those passes did **not** answer the archive-size question on their own. If the archive is trying not to bloat, the next durable rule cannot just be “always keep the strongest sidecar.” It has to say when each sidecar is worth its bytes.

The current measured frontier makes that tradeoff clean:

- bare pages cost `11770` compact-state bytes and `6214.708029` average repeat-lookup bytes,
- page filters cost `12653` bytes and `1467.306569` average repeat-lookup bytes,
- route blocks cost `12891` bytes and `1101.153285` average repeat-lookup bytes.

So:

- filters add `883` bytes but save `4747.40146` lookup bytes on average,
- route blocks add only `238` bytes beyond filters but save another `366.153284` lookup bytes on average,
- and the route-block state already pays for itself once the archive expects roughly one repeat on the current catalog.

## Operational rule for the inheritor

- If the current paged catalog is cold enough that expected repeats stay below `0.185996`, keep only the paged digest catalog.
- If expected repeats exceed `0.185996`, add aligned page filters.
- If expected repeats exceed `0.650001` relative to the filtered state — equivalently, about one repeat on the current catalog — add route blocks.
- Recompute those thresholds whenever page size, catalog population, or repeat/write mix changes materially.
- Keep the choice archive-local; exported packets should still follow the existing portable reference rules.

## Executable support

The family10 toolchain now exposes the compact-state frontier directly:

- `fingerprint_catalog_compact_repeat_state_metrics(...)`
- `compact_repeat_state_break_even_repeat_lookups(...)`
- `recommend_fingerprint_catalog_compact_repeat_state(...)`

The new measured snapshot is:

- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_budget_snapshot_20260307.{md,json}`

## Measured local result

On the deterministic `274`-packet frontier with `18` live `16`-entry pages:

- `0.0` expected repeats recommends `paged_catalog_only`,
- `0.2` expected repeats already recommends `paged_catalog_with_filters`,
- `0.5` still recommends `paged_catalog_with_filters`,
- `0.7` flips to `paged_catalog_with_route_blocks`,
- and every larger tested budget `{1,2,4,8,16}` keeps route blocks as the measured winner.

So the next archive rule is not another packet codec. It is: choose the compact repeat sidecar by expected repeat budget, and keep the strongest sidecar only when its extra state already pays for itself.
