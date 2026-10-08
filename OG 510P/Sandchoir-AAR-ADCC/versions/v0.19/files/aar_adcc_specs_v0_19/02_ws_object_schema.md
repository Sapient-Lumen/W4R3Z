# 02 — Working Set Object Schema (v0.19)

WS is a strict, structured, bounded “blackboard.” Ledger is unlimited.

Each object has:
- `id`: C#/T#/P#/E#/CE#/REQ#/LEASE#/CAP#/SUM#
- `title`: one line
- `body`: short structured payload
- `status`: active|selected|done|stale|superseded
- `refs`: links to other IDs
- `created_at_cursor`, `updated_at_cursor`
- `owner` (optional), `scope` tags
- `hotness` (computed)

## Object types
### H0 (Human priority) — special
- Always visible first.
- Freeform natural language allowed.
- Router may keep a short history (H0.1, H0.2…) but only one is active.

### C# Claim
- `statement` (short)
- `assumptions` (optional)
- `confidence` (optional)
- `counterexamples` (refs to CE#)
- `tests` (refs to T# / verifier)

### T# Task
- `goal` (short)
- `inputs/outputs` (optional)
- `acceptance` (what “done” means)
- `priority` (optional)
- `depends_on` (refs)

### P# Patch proposal
- `touch_set` (files/components)
- `summary`
- `diff_ref` (path or pointer)
- `verify_intent` (which checks should pass/fail)
- `rollback_note`

### E# Evidence card
- `kind` (test/build/proof/repro/benchmark/manual)
- `result` (pass/fail/flaky/unknown)
- `signal` (1–5 short lines)
- `repro` (command or verifier ref)
- `scope` (what it supports/refutes)

### CE# Counterexample
Eligibility invariant:
- `witness`: concrete input/state
- `repro`: how to reproduce in sandbox
- `expected_signal`: what indicates success (fail) deterministically
- `targets`: which C# / P# it refutes
- `status`: proposed|admitted|certified|rejected|superseded

### REQ# Directed request (DM-ticket)
- `from`, `to`
- `type`: review|test|falsify|clarify|implement|summarize
- `targets`: IDs
- `deliverable`: what receiver should output
- `deadline`: next_round|by_cursor|none
- `priority`: 1–3

### LEASE# Ownership/lease
- `scope`: file/component tag
- `owner`: agent id
- `ttl`: expires at cursor or time
- `mode`: soft|hard
- `notes`

### CAP# Capability report
- `agent`
- `supports`: header_constraints|streaming|git|pytest|… (small enum list)
- `limits`: max_output_tokens, known truncation quirks (optional)
- `last_probe_cursor`

### SUM# Compaction summary
- `covers`: list of IDs compacted
- `summary`: bounded
- `kept_decisions`: key outcomes
- `discarded`: what was evicted
