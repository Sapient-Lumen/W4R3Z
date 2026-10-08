# Status-label freshness tiers — rev0014

Freshness tiers control recheck cadence. They do not assert current legal status.

Tiering uses:

- most recent document-label year;
- whether the row says Investigation, Enforcement, Closed, or mixed labels;
- whether later official-news signals are known to be volatile;
- whether child-agency split handling is required.

The tiers are:

- `P0_recent_or_terminal_signal_recheck_before_display`;
- `P1_recent_source_page_document_recheck_before_display`;
- `P1_investigation_label_recheck_before_display`;
- `P2_enforcement_label_periodic_recheck_required`;
- `P3_older_closed_or_statement_label_recheck_required`.

Every tier blocks public current-status display in this revision.
