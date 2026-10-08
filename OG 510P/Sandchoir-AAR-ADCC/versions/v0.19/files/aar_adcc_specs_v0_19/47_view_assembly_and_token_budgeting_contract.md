# 47 — View Assembly + Token Budgeting Contract (v0.19)

The AAR’s most important job is composing per-agent views that are:
- bounded in size
- stable in ordering
- robust to truncation
- cheap to “diff” mentally

This doc defines a deterministic assembly contract.

## 1) Budgets are multi-dimensional
A view has limits:
- max items
- max lines per item
- max total lines
- (optional) max tokens estimated

Line-based budgeting is the primary control (tokens vary by model),
but token estimates can provide safety.

## 2) Deterministic section ordering (never changes)
1. H0
2. MANDATORY
3. HOT
4. DELTA
5. ROLE
6. DISCOVERY
7. RANDOM

Any reorder requires a new protocol version (don’t).

## 3) Per-section caps are hard
Each section has:
- item cap
- line cap per item
- total line cap

If overflow:
- truncate lowest priority within section
- never truncate H0 header
- never truncate mandatory headers (may truncate bodies, but keep event lines)

## 4) Item presentation format (stable)
Every item:
- `ID title (status) [hotness=N]`
- up to K bullet lines (compact fields)
- refs: `refs: C12, P7, ...` (1 line max)

No prose paragraphs. Paragraphs go to Ledger.

## 5) Delta semantics (bounded)
DELTA is a compact change list:
- `+ C12 updated: confidence -> low`
- `+ E4 added: unit_fast fail (signal...)`
- `- P3 superseded by P7`

If an agent requests `ZOOM=ID`, the router returns a bounded expansion of just that ID next.

## 6) Token estimation (optional guard)
Router may estimate tokens conservatively:
- assume ~4 chars/token
- if over threshold: drop DISCOVERY then RANDOM, then shrink ROLE, then shrink DELTA.
Never drop mandatory/H0.

## 7) Personalization limits
Per-agent personalization is menu-based (subscriptions).
Agent-defined custom policies are not applied to view assembly in v0.x.

## 8) MetaLLM knobs
- choose budget profile per agent (default/emergency)
- enable/disable exploration sections
- trigger compaction when WS churn threatens budgets

## 9) Operator UX: view diff
Router can print:
- changes since last view
- what was suppressed due to budget

This is essential for debugging AAR behavior.
