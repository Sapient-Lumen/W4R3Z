# rev0100 — Legal action page hash and zero-limit cursor progress

rev0100 closes two remaining page-protocol holes from the rev0097–rev0099 legal-surface work.

## Page-content binding

`LegalActionPage` now records both the caller's `requested_limit` and the normalized `effective_limit`, plus a reproducible `page_hash`. The public helper `legal_action_page_hash(...)` hashes:

- choice kind and chooser;
- requested cursor and next cursor;
- requested and effective limits;
- actions-seen lower/exact count;
- completion flag;
- the ordered hashes of actions actually returned in the page.

`LegalActionPageLocation` carries that page hash as `page_hash`, and `ActionReceiptRecord` / `ActionTrace.v4` persist it as `choice_page_hash`. Replay still recomputes `locate_legal_action_page(...)` before mutation, but now it can reject a trace when the selected action has the same offset while the surrounding page content changed.

## Zero-limit progress

The page API now treats a requested limit of zero as an explicit request with `effective_limit == 1`. This preserves the caller's original request while guaranteeing that a non-empty legal-choice domain advances `next_cursor`. The regression `test_legal_action_page_zero_limit_still_advances_and_hashes_page` proves cursor progress, reproducible `legal_action_page_hash(...)` output, distinct hashes for adjacent zero-limit pages, and no StateCore mutation.

This does not replace future cursor/schema versioning, exact-count APIs, or random-access choice construction. It makes the current cursor protocol safer and more auditable while preserving the bounded frontier contract.


## rev0102 schema binding

rev0102 keeps the rev0100 page hash concept but folds `LegalActionPage::schema_version` into `legal_action_page_hash(...)`. The current schema constant is `kLegalActionPageSchemaVersion`; action receipts and `ActionTrace.v5` persist it as `choice_page_schema_version` / `choice_page_schema=` so a trace can fail fast when the page contract changes even if cursor/index metadata still lines up.


## rev0103 count hash note

rev0103 keeps the rev0100 page-hash boundary but promotes it to `MTGSim.LegalActionPage.v2`. The hash now includes `total_actions_lower_bound`, `total_actions_exact`, and `remaining_actions_lower_bound`, so page hashes bind not only page contents and cursors but also the exact-vs-lower-bound cardinality contract exposed to agents and replay tooling.


rev0104 keeps the rev0100 page-hash boundary but promotes it to `MTGSim.LegalActionPage.v3`. The hash now includes `state_hash` and `choice_request_hash`, so page hashes bind page contents, cursor/count metadata, schema, and the StateCore/request context that produced the page.
