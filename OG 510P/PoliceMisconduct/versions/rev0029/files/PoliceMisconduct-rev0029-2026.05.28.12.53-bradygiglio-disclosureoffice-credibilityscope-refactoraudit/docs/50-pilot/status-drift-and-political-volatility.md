# Status drift and political volatility

Police-accountability records are not static. They are subject to legal status changes, federal enforcement changes, local compliance changes, political reversals, court orders, monitor reports, and source-page maintenance.

Rev0003 treats status drift as a first-class problem.

## Four status fields

The cube should eventually represent at least four separate status fields:

1. `source_page_status` — what a given page says at a given access time.
2. `status_signal` — a press release, motion, monitor notice, local update, or news item suggesting a change.
3. `court_order_status` — status grounded in a court order.
4. `current_status_candidate` — the display candidate after current recheck.

These fields should not collapse.

## Political posture is a source fact, not a truth override

A later federal administration may retract findings, dismiss cases, terminate oversight, or change enforcement posture. The cube should record those changes exactly. It should not pretend they did not happen. It also should not delete the public-record existence of earlier reports, complaints, decrees, court orders, or monitor materials.

The archive is temporal: it records source events over time.

## Public wording principle

Avoid: “Department is under federal enforcement.”

Prefer: “The DOJ source page accessed on DATE listed this matter as ENFORCEMENT. Current status requires docket/source recheck.”

Avoid: “DOJ proved misconduct.”

Prefer: “DOJ issued a findings report; document summary and claim extraction are not yet admitted in this cube.”
