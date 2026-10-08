# Fixity state machine — rev0012

Rev0012 adds a ten-state fixity model.

The key safety distinction is between **F2 HTTP metadata observed** and **F3 private payload captured**. Rev0012 reaches F2 for selected DOJ targets but does not reach F3.

A target at F2 may support source-inventory bookkeeping. It may not support content summary, legal-effect extraction, person records, incident records, public current-status display, or public payload display.

The first state where bounded content summary can become possible is F7, and only after F3-F6 have all passed. The first state where claim review can become possible is F8. Public display review is F9 and must remain separate from internal claim review.

