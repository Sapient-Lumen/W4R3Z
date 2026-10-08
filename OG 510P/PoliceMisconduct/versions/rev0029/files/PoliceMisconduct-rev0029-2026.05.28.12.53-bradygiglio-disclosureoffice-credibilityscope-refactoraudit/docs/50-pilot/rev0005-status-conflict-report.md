# Rev0005 status conflict report

Rev0005 adds a bridge from DOJ Special Litigation Section source rows to DOJ official press-release events.

## Why this revision exists

Rev0004 indexed source-page status labels and document labels, but it had not yet modeled what happens when another official DOJ carrier gives a later or more specific status signal. Rev0005 treats that as a first-class source problem, not as a nuisance.

The current rule is:

> A status signal is not a status claim.

The DOJ cases/matters page remains the source-page spine for the pilot. Its law-enforcement section was observed with the page label `Updated May 1, 2026`. Rev0005 then added six official DOJ press-release events as source carriers.

## What was added

- `data/source_graph/doj_sls_official_news_events.rev0005.json` — six official DOJ press-release event rows.
- `data/source_graph/doj_sls_status_reconciliation_queue.rev0005.json` — seven reconciliation tickets.
- `data/source_graph/doj_sls_event_matter_crosswalk.rev0005.json` — crosswalk rows from official event labels to matter objects or unmatched agency labels.
- `data/source_graph/doj_sls_high_volatility_source_packets.rev0005.json` — four source packets for high-volatility matters.
- `OFFICIAL-NEWS-CARRIER-LEDGER.json`, `STATUS-CONFLICT-RESOLUTION-LEDGER.json`, `DOCKET-RECHECK-PROTOCOL.json`, and `EVENT-TAXONOMY.json`.

## High-value discoveries

### Same-owner conflict / lag

The New Orleans and Newark rows demonstrate why a source-page label must not be displayed as current legal status. The DOJ cases page labels New Orleans and Newark as `Enforcement`, while DOJ official press releases say federal courts terminated those consent decrees in November 2025.

Rev0005 does **not** decide the current legal status. It opens reconciliation tickets and requires docket/order accession.

### Motion is not termination

Cleveland is different. A February 2026 DOJ press release says the parties jointly filed a motion to terminate federal oversight, while the source page remains `Enforcement`. That is not a conflict in the same way; a motion requires a later court-order check.

### Closed is not erased

Louisville and Minneapolis show the history-retention problem. DOJ closure/retraction language must be recorded as a dated official event, but prior public-record carriers remain historical source records. Closure/retraction language does not delete the fact that findings reports, complaints, consent decrees, motions, or orders were public carriers.

### Mixed rows need child status

Orange County remains a mixed-row problem: OCDA and OCSD are represented in one DOJ row with different status labels and later OCDA completion language. Rev0005 keeps this as a child-agency split task, not a department-page claim.

## What was not admitted

- no current court-status claims;
- no officer records;
- no civilian records;
- no incident records;
- no lawsuit merits summaries;
- no settlement amount records;
- no document-content summaries.

## Next best move

Use `DOCKET-RECHECK-PROTOCOL.json` on New Orleans and Newark first. They are the cleanest same-owner conflict tests and will force the cube to model terminal orders, source-page lag, monitor archives, and rollback wording before any public status display.
