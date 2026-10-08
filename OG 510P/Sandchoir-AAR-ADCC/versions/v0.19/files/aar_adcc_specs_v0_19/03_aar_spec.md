# 03 — AAR Spec (Adaptive Attention Router) (v0.19)

AAR composes **views** (prompt segments) per agent from WS + deltas.

## View sections (default order)
1. `H0` (human priority) — always first
2. `MANDATORY` — always shown, cannot be muted:
   - mode/strictness changes
   - protocol lock (if any)
   - lease changes affecting your touched scope
   - certified CE and selected patch
3. `HOT` — global hot items (promoted via scoring + votes)
4. `DELTA` — changes since agent’s last seen cursor
5. `ROLE` — subscription-based items (menu)
6. `DISCOVERY` — controlled exploration slot (1)
7. `RANDOM` — pure random unseen delta slot (0–1)

## Views are bounded
- item-count cap per section
- line cap per item (1–5 lines)
- total view cap (items and lines)

## Deltas and cursors
- Every WS mutation increments `CURSOR`.
- Agents provide `CURSOR` in `@CTRL`.
- AAR returns `DELTA(CURSOR)` (bounded) by default.

## Hot promotion
Hotness is **attention**, not truth. Promotion sources:
- system triggers (selected patch change, certified CE, failing top check)
- weighted attention votes
- hotness scoring heuristics (see 04_aar_hotness_scoring.md)

## Personalization ladder
- P0: no personalization (everyone sees same)
- P1: menu subscriptions (safe default)
- P2: bounded pull (“zoom 1 item” per slice)
- P3: policy proposals (MetaLLM/human approves between runs)
- P4: freeform (deferred; drift risk)

## Request routing
REQ# appears in recipient’s ROLE/Mentions area, not global HOT unless:
- recipient promotes it, or
- it targets a certified CE or selected patch.

## Compaction
When WS pressure is high:
- generate SUM# objects
- evict stale/low-hotness items
- preserve invariants: H0, mandatory anchors, selected patch, certified CE

See also: 46_controlled_exploration_policy.md and 47_view_assembly_and_token_budgeting_contract.md
