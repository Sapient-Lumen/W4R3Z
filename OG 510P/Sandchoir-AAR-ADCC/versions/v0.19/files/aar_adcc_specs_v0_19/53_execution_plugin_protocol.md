# 53 — Execution Plugin Protocol (v0.19)

Agents need to “do work” (build/test/prove) without turning your router into spaghetti.

This doc defines a *minimal execution surface* as a plugin.
It can be permissive in your sandbox; the key is ergonomic boundedness, not security theater.

## 1) Two execution lanes
### Lane A: Registry verifiers (preferred)
- bounded, repeatable, cached
- produces E# evidence cards

### Lane B: Ad-hoc sandbox commands (allowed, but fenced)
- produces ledger logs
- must be attached to a REQ# or a task T#
- must not be silently executed as part of parsing

## 2) Execution request object (EXEC#)
Fields:
- `from` (Ai or human/MetaLLM)
- `kind`: verifier|cmd
- `cmd` or `verifier_name`
- `cwd_ref` (canonical | agent_worktree | scratch)
- `timeout_class`: cheap|medium|expensive
- `expected_signal` (1 line)
- `on_success`: create E# / propose patch / certify CE
- `on_fail`: create E# / request refinement

## 3) Router behavior
- Router queues EXEC jobs under a budget (cost classes).
- Router streams minimal outputs:
  - WS gets E# signal lines
  - Ledger gets full logs with pointers
- Router caches verifier results by snapshot key.

## 4) Agent ergonomics
Agents should not paste long commands into WS.
Instead they propose:
- `checks{unit_fast=3}` or `exec{verifier=unit_fast}`
- or REQ to MetaLLM/human to run an ad-hoc command

## 5) Failure handling
- timeouts produce E# with `result=unknown` and a short note
- flaky outputs produce E# `result=flaky` and request repro refinement

## 6) Anti-spaghetti discipline
If a command cannot be described in one line, it is not a “verifier.”
Keep the registry small.
