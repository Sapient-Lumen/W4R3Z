# rev0098 — Legal action page location

rev0097 made the largest combat choice surfaces discoverable by cursor page. rev0098 adds the next executable piece of the legal-choice protocol: an opt-in locator for a selected action.

## Why this matters

`validate_legal_action(...)` deliberately stays cheap and authoritative. When the bounded frontier is incomplete, a canonical combat declaration can be legal by direct domain validation even if it was not listed in the first 128 offered actions.

That is correct for applying the action, but it leaves search and agent callers with a second question:

```text
where would this action appear in the deterministic paged choice surface?
```

`locate_legal_action_page(...)` answers that without changing the default frontier budget or collapsing validation with discovery.

## New API

`LegalActionPageLocation locate_legal_action_page(const GameState&, const LegalAction&, std::uint64_t page_limit = 128)` returns:

- whether the action was found;
- the choice kind and chooser;
- the requested and effective page limits;
- the page cursor that contains the action;
- the zero-based action cursor;
- the index inside the returned page;
- the page's `next_cursor`, `actions_seen`, completion bit, and scanned-page count.

A requested page limit of zero is normalized to an effective limit of one in the locator. This prevents external cursor loops from becoming non-progressing probes while preserving the caller's requested value in the returned metadata.

## Boundaries

The locator is intentionally separate from `validate_legal_action(...)`; it is not a replacement for validation:

- validation answers whether the action is legal now;
- paging answers what can be discovered from a cursor;
- location answers where a selected action appears in that paged surface.

This keeps ordinary application cheap while giving search/replay tooling an auditable discovery proof when it needs one.

## Tests added

- `test_legal_action_page_location_finds_tail_combat_actions` finds an all-attacker declaration beyond the first 128-action prefix, reconstructs it from page cursor/index, normalizes a zero page-limit probe to one, and locates a late six-blocker combat-damage order.
- `test_legal_action_page_location_reports_missing_without_mutation` verifies that a wrong-chooser action reports no page position and does not mutate StateCore.

## Remaining work

This is still not the final legal-choice protocol. Stable external cursor tokens, page schema versions, page hashes, count APIs, and small-state equivalence properties are still open. The important forward move is that discovery now has a concrete location surface rather than relying on either a bounded vector prefix or an unlocated direct-validation escape hatch.


## rev0099 durable use

rev0099 promotes page-location proof into the action evidence path. Legal `ActionReceiptRecord` rows now store the located page position, and `ActionTrace.v4` lets replay recompute the location and page hash before mutation. A mismatch is reported as `ChoicePageLocationMismatch`.
