# 46 — Controlled Exploration Policy (v0.19)

You want:
- hotness heuristics (exploit)
- controlled exploration (explore)
- a small amount of true random (anti-blind-spot)

This doc turns that into a **bounded policy** that will still work under unknown slice counts.

## 1) Why explore at all
Exploration is a hedge against:
- consensus collapse
- local optimum lock-in
- hidden counterexamples
- forgotten tasks stuck in the ledger

## 2) Exploration slots (AAR)
AAR has two non-mandatory “exploration-like” sections:
- `DISCOVERY` (controlled exploration): 0–1 items per view
- `RANDOM` (true random): 0–1 items per view

Hard cap: at most 2 total exploration items per view, and only when budgets allow.

## 3) Controlled exploration candidate pool
Candidates must be WS IDs, not raw ledger text.
Pool = items that are:
- not currently in HOT
- not mandatory
- stale or low-attention
- or newly created but unreviewed

Exclude:
- anything already resolved (done/superseded)
- anything with no actionability (pure talk, no refs to tasks/patch/evidence/CE)

## 4) Selection policy (bandit-lite, no heavy math required)
Maintain per-item “exploration score” that increases when:
- item is unreviewed
- item is referenced by many tasks but not hot
- item is linked to “uncertain” claims
- item is associated with repeated deadlocks

Then pick:
- 80–90%: highest exploration score (deterministic)
- 10–20%: random among remaining candidates (true random)

This keeps a little randomness without losing control.

## 5) Exploration success criteria (“what counts as a win”)
An exploration item is “successful” if it yields any of:
- a certifiable CE (CE# with witness+repro+expected signal)
- a discriminative verifier suggestion that resolves a dispute
- a small patch proposal that reduces blast radius
- a compaction summary that unblocks progress (SUM#)
- a lease/ownership clarification that prevents collisions

If exploration doesn’t yield a win in N cycles:
- lower exploration rate (turn off RANDOM first)
- or change the pool constraints

## 6) Safety against derailment
- exploration items cannot change canonical state by themselves
- any canonical change still requires selection (patch vote / human / integrator)
- exploration never displaces mandatory channel and H0

## 7) MetaLLM knobs
MetaLLM can adjust:
- exploration rate (DISCOVERY on/off, RANDOM on/off)
- N (cycles before deeming exploration ineffective)
- pool filters (what qualifies as “actionable”)

If truncation spikes: exploration is disabled automatically.
