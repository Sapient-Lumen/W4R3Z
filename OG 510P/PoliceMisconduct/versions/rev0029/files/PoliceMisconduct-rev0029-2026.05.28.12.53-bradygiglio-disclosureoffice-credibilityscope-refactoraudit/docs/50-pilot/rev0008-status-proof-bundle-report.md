# Rev0008 status-proof bundle report

Rev0008 adds a reviewer-facing status-proof bundle layer. A bundle collates three signal families: the DOJ Special Litigation Section source-page label, official DOJ news events, and accessioned court/order document-effect atoms. It then records blockers before any public current-status display.

The central rule is: **signal collation is not claim promotion**.

New surfaces:

- `data/source_graph/doj_sls_source_page_resnapshot.rev0008.json` — selected source-page label resnapshot rows.
- `data/source_graph/doj_sls_official_news_signal_vectors.rev0008.json` — official DOJ news as signal vectors.
- `data/source_graph/doj_sls_status_proof_bundles.rev0008.json` — 11 private review bundles.
- `data/source_graph/doj_sls_source_acquisition_queue.rev0008.json` — unresolved docket/source acquisition targets.
- `data/source_graph/doj_sls_public_department_page_preflight.rev0008.json` — page-shape gates.

No person, incident, lawsuit-merits, settlement-amount, full document-summary, or public current-status claim is admitted.

## Why this matters

A source page can lag a press release. A press release can summarize a court event without exposing the order. A motion can look terminal but is not an order. A closing letter can be official without being a judicial act. Rev0008 makes those differences visible before the cube speaks publicly.

Created: 2026-05-25T01:04:05Z

