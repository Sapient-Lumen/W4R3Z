# rev0097 — Legal action cursor paging

rev0095 made bounded combat frontiers truthful. rev0096 made the selected action's validation source durable. rev0097 adds the next executable step: deterministic cursor pages for the combat choice surfaces that can exceed the 128-action frontier budget.

## Why this matters

The bounded frontier is still intentionally small. That is useful for cheap UI and policy-mask probes, but it is not enough for search, self-play, or replay tooling that needs to discover actions after the first prefix. A legal declaration omitted from the first 128 actions should not require the caller to guess a canonical encoding and ask direct validation by hand.

`enumerate_legal_action_page(...)` gives callers a resumable view:

- `cursor` is a zero-based legal-action offset in the deterministic order used by the frontier.
- `requested_limit` records the requested page size.
- `next_cursor` is the cursor for the next page.
- `complete=false` means at least one legal action exists after the returned page.
- `actions_seen` is exact when `complete=true` and a lower bound when `complete=false`.

The original `enumerate_legal_action_frontier(...)` remains a bounded prefix and keeps its explicit `complete` / `generation_limit` truth metadata. The page API is additive, not a silent budget increase.

## Implemented page families

rev0097 implements pages for the high-risk combat families that first exposed the prefix problem:

- attack declarations;
- block declarations;
- combat-damage order permutations.

Ordinary finite priority/pending-trigger action sets are sliced from their existing complete frontier. Unsupported future huge choice families must add direct pagers rather than pretending a prefix is exhaustive.

## Tests added

- `test_attack_action_page_reaches_actions_omitted_by_frontier_prefix` proves that eight attackers produce two 128-action pages and the all-attacker declaration is reachable after the first prefix.
- `test_block_action_page_reaches_actions_omitted_by_frontier_prefix` proves the same for eight independent blockers.
- `test_damage_order_page_reaches_late_permutation_without_raising_frontier_budget` proves a six-blocker damage-order surface has 720 permutations and a late reverse order is reachable by paging.
- `test_legal_action_page_and_frontier_reject_invalid_player_without_mutation` guards invalid-player queries at the frontier/page boundary.

## Refactor/audit note

The combat enumeration code now has shared labelling helpers for attack declarations, block declarations, and combat-damage-order actions. The bounded frontier path and the page path intentionally stay separate: the frontier stops at the budget, while pages can walk until the requested cursor/window is satisfied.

This is still not the final legal-choice protocol. It does not yet provide stable external cursor schemas, exact counts for every family, or constraint-backed random access. It does, however, turn the most dangerous remaining prefix-only surface into an executable discovery API without creating another registry layer.
