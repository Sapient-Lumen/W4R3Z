# Source graph data — rev0005

This directory contains the active source graph surfaces for the first PoliceMisconduct pilot.

## Current data files

- `doj_sls_law_enforcement_agencies.seed.json` — rev0003 seed source rows; kept as the original row surface.
- `doj_sls_matter_objects.rev0004.json` — `27` source-scoped matter objects derived from the seed rows.
- `doj_sls_document_census.rev0004.json` — `148` label-only source-document rows.
- `doj_sls_status_events.rev0004.json` — source-page status observations and fragility flags.
- `doj_sls_official_news_events.rev0005.json` — `6` official DOJ press-release event rows.
- `doj_sls_status_reconciliation_queue.rev0005.json` — `7` reconciliation tickets for source conflicts, source lag, mixed rows, and missing current-status proof.
- `doj_sls_event_matter_crosswalk.rev0005.json` — crosswalk rows from official news events to matter objects or unmatched agency labels.
- `doj_sls_high_volatility_source_packets.rev0005.json` — source-packet nonclaims for the most fragile status surfaces.
- `foundation_source_carriers.seed.json` — non-pilot carrier references for denominator/use-of-force/decertification modeling.

## Current allowed claim power

Allowed:

- source page exists;
- matter label observed;
- agency labels observed;
- source-page status label observed;
- document label/class/year observed;
- official DOJ press-release event observed;
- event maps or fails to map to an existing matter object;
- source-status conflict/missingness ticket exists.

Not allowed:

- document content summary;
- department misconduct claim;
- current court-status assertion;
- officer/person record;
- incident record;
- settlement amount record;
- public status badge from press release or source-page label alone.


## rev0006 additions

Rev0006 adds status-candidate and proof-gate surfaces. These are all nonclaims:

- `doj_sls_status_candidate_packets.rev0006.json`
- `doj_sls_court_order_accession_candidates.rev0006.json`
- `doj_sls_local_monitor_sources.rev0006.json`
- `doj_sls_child_agency_status_splits.rev0006.json`
- `doj_sls_public_status_cards.rev0006.json`
- `doj_sls_history_retention_warnings.rev0006.json`
- `doj_sls_ghost_carrier_candidates.rev0006.json`
- `doj_sls_additional_official_news_events.rev0006.json`

None of these files authorizes person extraction, incident extraction, document content summaries, or public current-status claims.


## Rev0011 preservation surfaces

Rev0011 adds preservation queues and debt registers. These files are operational nonclaims: they describe what must be frozen, resolved, hashed, privacy-scanned, or watched for mutation before any content summary or claim promotion.
