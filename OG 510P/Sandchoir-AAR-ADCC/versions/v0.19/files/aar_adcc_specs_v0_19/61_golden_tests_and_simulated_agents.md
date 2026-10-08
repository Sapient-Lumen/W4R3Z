# 61 — Golden Tests + Simulated Agents (v0.19)

You need a way to develop this without burning real LLM turns.

## 1) Simulated agent outputs
Create a library of fixtures:
- perfect CTRLJSON
- json-ish CTRLJSON (needs healing)
- missing CTRL
- partial output truncation
- adversarial / injection-like text in ledger
- long rambling prose with a tiny CTRL buried late

## 2) Golden tests
Given:
- WS snapshot + event log + budget profile
Expect:
- exact rendered view text (or stable hash)
- suppression diagnostics
- parse outcomes

This tests the “anytime packet salvage” and bounded view guarantees.

## 3) Load tests (cheap)
Simulate:
- 5 agents streaming concurrently
- one hung agent
- bursty output causing queue pressure
Verify:
- bounded queues don’t blow up
- state_store remains responsive
- checkpoints still succeed

## 4) Regression suite
Every bug becomes:
- a fixture
- a golden test
This is how you keep stability while iterating quickly.
