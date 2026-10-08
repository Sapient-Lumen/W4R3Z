# Rev0026 audit/refactor: hazard classification and consequence exposure

This refactor pass identifies a recurring schema problem across engineering records: physical failure mode and consequence exposure are often entangled. Nuclear records, process-safety records, structural records, and impoundment records all need hazard/consequence overlays that are not moral verdicts and not post-hoc drama.

Rev0026 starts with impoundments because tailings facilities make the issue unavoidable. A facility is not only a mechanism; it is also a stored material, a runout path, an emergency-planning problem, a monitoring problem, a disclosure problem, and a governance problem.

The cube therefore adds `IMPOUNDMENT-FACTOR-AUDIT-LEDGER.json` and `HAZARD-CLASSIFICATION-REFACTOR-LEDGER.json` rather than modifying every engineering schema immediately. Future sessions should let the overlay stabilize, then migrate durable fields into schema.
