# 58 — AAR Routing Policy (Deterministic Pseudocode) (v0.19)

This doc makes AAR behavior explicit, testable, and debuggable.

## Inputs
- WS objects with types, statuses, hotness, refs, timestamps
- Event log deltas since agent’s last cursor
- Agent ROLE subscriptions
- TOUCH scope overlap (leases / file scopes)
- Budget profile (items/lines/tokens)
- Exploration settings (DISCOVERY/RANDOM on/off)

## Outputs
- A bounded view obeying section order (47_) with suppression diagnostics.

## Core algorithm (high level)
1. `view = []`
2. add H0 header (always)
3. add MANDATORY events since last cursor (bounded; bodies truncatable)
4. add HOT items (global hot list, bounded)
5. add DELTA list (compact change lines, bounded)
6. add ROLE items (subset by subscription + TOUCH overlap)
7. if budget remains and DISCOVERY on:
   - pick 0–1 exploration candidates (46_)
8. if budget remains and RANDOM on:
   - pick 0–1 random candidate
9. if over budget:
   - drop lowest-priority sections in order: RANDOM → DISCOVERY → ROLE → DELTA
   - never drop HOT/MANDATORY/H0

## Candidate ranking
### HOT
Already computed by promotion table (27_). Ordering:
- mandatory-anchored first
- then hotness desc
- tie-breaker: recency

### ROLE
Compute score:
- +2 if TOUCH overlap
- +1 if referenced by selected patch or certified CE
- +1 if referenced by >=2 tasks
- -1 if stale
Pick top N.

### DISCOVERY
Use exploration score (46_):
- +unreviewed
- +referenced-but-not-hot
- +linked-to-uncertain-claims
- +deadlock-associated
Pick highest score; 10–20% random fallback.

## Diagnostics (“why didn’t I see X?”)
Router emits suppression info (not in agent view by default):
- suppressed_due_to_budget: [IDs]
- suppressed_due_to_policy: [IDs + reason]
- section_overflow_stats

MetaLLM and Gearbox can inspect this.

## Testability
AAR must be testable with golden inputs:
- given WS+events+budget, output must match expected stable rendering.
