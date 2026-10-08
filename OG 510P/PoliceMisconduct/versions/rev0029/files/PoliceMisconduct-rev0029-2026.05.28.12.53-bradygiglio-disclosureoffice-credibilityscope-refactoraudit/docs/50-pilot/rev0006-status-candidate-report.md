# rev0006 status-candidate report

Rev0006 answers the rev0005 frontier: how should the cube behave when source-page labels, press releases, local pages, monitor sources, and court notices point in different directions?

The answer is a new intermediate object: **current-status candidate**.

A candidate is not a claim. It is a structured reconciliation hypothesis with proof gaps, rollback triggers, and public-display blocks.

## What rev0006 added

- `data/source_graph/doj_sls_status_candidate_packets.rev0006.json` — 9 status candidates, all nonclaims.
- `data/source_graph/doj_sls_court_order_accession_candidates.rev0006.json` — 14 order/docket accession candidates.
- `data/source_graph/doj_sls_local_monitor_sources.rev0006.json` — 6 local, monitor, court-notice, and source-family bridge rows.
- `data/source_graph/doj_sls_child_agency_status_splits.rev0006.json` — first mixed-row child agency split, starting with Orange County.
- `data/source_graph/doj_sls_public_status_cards.rev0006.json` — 7 no-person public card copy candidates.
- `data/source_graph/doj_sls_history_retention_warnings.rev0006.json` — 6 history-retention warnings.
- `data/source_graph/doj_sls_ghost_carrier_candidates.rev0006.json` — 6 ghost carrier candidates for press-release agencies absent from the current source-row seed.

## Test matters

### New Orleans

Signals: DOJ cases page label remains Enforcement; DOJ press release and city page report termination. Rev0006 creates a terminal status candidate but blocks public current-status display until terminal order/docket proof is accessioned.

### Newark

Signals: DOJ cases page label remains Enforcement; DOJ press release and monitor-member source report termination. Rev0006 creates a terminal status candidate but blocks public current-status display until terminal order/docket proof is accessioned.

### Seattle

Signals broadly align: cases page Closed, DOJ press release reports completion/termination/final dismissal, and WAWD court notice provides the case number and hearing. Rev0006 still blocks public current-status display until the final order/docket entry is accessioned.

### Cleveland

Signal: DOJ and Cleveland filed a motion to terminate. This is not a terminal event. Rev0006 classifies it as motion-pending/unresolved.

### Orange County

The parent row mixes OCDA and OCSD. Rev0006 creates child agency status objects so OCDA completion and OCSD completion/closed signals cannot overwrite each other.

### Louisville / Minneapolis

DOJ closure/retraction language is treated as a dated federal event plus a history-retention problem, not as erasure of earlier public-record carriers.

## Core rule

A status candidate is not a public status claim.

Created: 2026-05-25T00:23:00Z
