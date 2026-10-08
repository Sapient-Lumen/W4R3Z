# rev0102 — Legal Action Page Protocol Refactor

## Mission seam

rev0102 turns the rev0097–rev0100 legal-choice work from a useful paging utility into a more explicit protocol boundary. The heart of the seam is still:

```text
StateCore + chooser + explicit LegalAction -> validated next StateCore + typed evidence
```

The new work makes the external legal-choice page contract harder to drift silently by binding every page and trace proof to a stable schema number.

## Page schema evidence

`kLegalActionPageSchemaVersion` is the public in-code version for the current cursor/page contract. `LegalActionPage::schema_version` is emitted by every page, folded into `legal_action_page_hash(...)`, and copied through `LegalActionPageLocation::page_schema_version` when a selected action is located.

Action receipts now persist this as `choice_page_schema_version`. Serialized traces now emit `MTGSim.ActionTrace.v5` with `choice_page_schema=` beside the existing `choice_page_hash=`. Replay treats older v4 page-hash traces as parseable but schema-wildcarded; v5 traces reject schema drift through the existing `ChoicePageLocationMismatch` channel before StateCore mutation.

## Refactor: one combat-choice enumerator per domain

The combat choice code previously had two executable paths for each large legal domain:

- one path for bounded frontier prefixes;
- another path for cursor pages.

That duplication was useful while the paging surface was emerging, but it was the wrong shape for a durable protocol: a future fix to attack, block, or combat-damage-order legality could update one path and silently leave the other path behind.

rev0102 introduces `append_bounded_frontier_actions(...)`, so the frontier prefix now uses the same `for_each_legal_attack_declaration(...)`, `for_each_legal_block_declaration(...)`, and `for_each_legal_combat_damage_order(...)` emitters as page generation. This makes the emitter layer a single enumerator source for each combat choice domain. The frontier still stops at `kMaxDeclarationActionsPerPlayer`, still reports `complete=false` only when a real next action exists, and still keeps direct-domain validation for canonical tail choices.

## Regression coverage

Added and extended tests prove that:

- pages carry `kLegalActionPageSchemaVersion`;
- page hashes change when only `schema_version` changes;
- locators preserve `page_schema_version`;
- `ActionTrace.v5` serializes and parses `choice_page_schema=`;
- replay rejects page-schema drift before StateCore or journal mutation;
- the refactored frontier prefix remains order-equivalent to the first cursor page.

## Still open

This revision does not add random access or closed-form exact counts for large legal-choice domains. It also does not solve staged casting/activation transactions, replacement proposals, or full APNAP multi-choice ordering. The next useful slice is a count/lower-bound query and a small-state equivalence property that spans priority actions, combat declarations, direct validation, pages, page locations, receipts, and trace replay.


## rev0103 continuation

rev0103 bumps `kLegalActionPageSchemaVersion` to 2 because the page protocol now exposes explicit count-contract fields. The rev0102 schema evidence still serves the same purpose: traces that carry an older page protocol can be parsed, but replay will not silently treat changed page contracts as equivalent.


rev0104 bumps `kLegalActionPageSchemaVersion` to 3 because the page protocol now exposes page context evidence. `LegalActionPage::state_hash` and `LegalActionPage::choice_request_hash` are copied into page locations, receipts, and `ActionTrace.v7`, and replay treats mismatched context as `ChoicePageLocationMismatch` before mutation.
