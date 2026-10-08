# Legal Action Page Context Seal — rev0104

rev0104 seals every `LegalActionPage` to the context that produced it.

Before this revision, the page proof chain had schema, cursor, hash, count, locator, receipt, and trace evidence, but a standalone page still relied on nearby receipt fields to explain which StateCore and offered choice request it belonged to. That was a portability gap for agents, replay tooling, and future search indexes.

## Contract

`LegalActionPage` now carries:

- `state_hash`: the canonical StateCore hash at the moment the page was offered;
- `choice_request_hash`: the `ChoiceRequest::action_set_hash` for the chooser and state that produced the page.

The page protocol schema is now `kLegalActionPageSchemaVersion == 3`. `legal_action_page_hash(...)` uses `MTGSim.LegalActionPage.v3` and folds both context fields into the hash alongside schema, cursor metadata, count evidence, and page contents.

## Propagation

The same context evidence is copied through:

- `LegalActionPageLocation::page_state_hash` and `page_choice_request_hash`;
- `ActionReceiptRecord::choice_page_state_hash` and `choice_page_choice_request_hash`;
- `ActionTraceEntry::expected_choice_page_state_hash` and `expected_choice_page_choice_request_hash`.

`serialize_action_trace(...)` now emits `MTGSim.ActionTrace.v7` with `choice_page_state=` and `choice_page_request_hash=`. The parser remains backward-compatible with v1-v6; older traces are context-wildcarded because they predate the seal.

## Replay and validation

Replay compares page context during the existing page-location check. A drifted page state hash or page choice-request hash fails as `ChoicePageLocationMismatch` before StateCore or Journal mutation.

Receipt validation also verifies that a located page’s context equals the receipt’s `state_hash_before` and `choice_request_hash`. This makes malformed receipts fail locally even before a full replay run.

## Why this matters

The project’s mission is trusted transitions: state plus explicit choice becomes a validated next state plus typed evidence. A page is part of that evidence, not just a convenience vector. Context sealing lets an external caller cache, inspect, or replay a page proof without silently detaching it from the state/request surface that made it meaningful.

## Still open

- Stable external cursor tokens.
- Closed-form/random-access counts for large legal-choice domains.
- Small-state equivalence properties between full frontiers, page concatenation, direct validation, locators, receipts, traces, and replay.
- A reusable staged transaction layer for choice validation and cost payment.
