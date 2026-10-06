# Frontier backlog resolved-residue audit — 2026-06-15

## Finding

During the rotated smoke-slice pass, `FRONTIER-BACKLOG.json` still labeled resolved questions as live or failed to label them resolved. The most harmful examples were:

- `OQ-0251`, resolved by `RS-0259`, still marked `open`;
- `OQ-0248`, resolved by `RS-0256`, still marked `open`;
- several older backlog rows lacked `state`, `resolved_by`, and `successor` even though `RESOLUTION-LEDGER.json` had already closed them.

This is not cosmetic. A frontier surface that carries stale resolved items as open creates exactly the waste the archive is trying to avoid: future sessions spend scarce reentry attention rediscovering closures instead of continuing the live risk.

## Refactor

`FRONTIER-BACKLOG.json` now has a `resolved_residue_audit` block and every backlog row whose id appears in `RESOLUTION-LEDGER.json#items[].resolved_objects` must either be absent or explicitly marked as resolved with the matching resolution id and successor.

`tools/check_frontier_backlog_resolved_residue_contract.py` is the fail-closed guard. It does not turn the backlog into a review court. It only prevents a narrow, local false-frontier bug: resolved OQs masquerading as open work.

## Boundary

The checker does not decide which old unresolved constitutional questions matter. It only enforces that questions already closed by the resolution ledger do not remain labeled open in the frontier backlog.

## Consequence

The current live frontier is `OQ-0255`. The historical backlog can still carry resolved pressure as context, but it cannot pretend that resolved rows are current work.
