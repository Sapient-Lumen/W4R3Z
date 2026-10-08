# Core Architecture

## 2.1 Components

### Rust core (`gr_engine`)
MUST provide:
- deterministic simulation of repeated games,
- pluggable worlds (noise, termination, payoffs, topology, institutions),
- strategy execution with bounded resources (time/memory limits),
- metrics computation (per match, per tournament, per population),
- artifact emission (structured outputs + hashes),
- tracing hooks (sampled + on-failure full traces),
- **AFK safety primitives** (atomic artifact writes, resumable chunk execution).

### Python orchestration (`grlab`)
MUST provide:
- experiment DAG runner (worlds × strategies × replications),
- search/optimization loops (parameter sweeps, evolutionary search, adversarial probe generation),
- reporting (Pareto frontiers, failure case mining, regression tests),
- UX: commands, dashboards, trace explorer, reproducibility helpers,
- **AFK runner**: durable queue + safe shutdown + guaranteed worker cleanup.

## 2.2 AFK-first execution model
The orchestrator MUST be able to run in an environment where:
- the job may be killed at any moment (SIGTERM or SIGKILL),
- the user expects no orphan compute,
- and all completed work is preserved.

This implies:
- jobs are broken into **small, idempotent work units** (chunks),
- each chunk produces **one atomic commit** to the artifact store,
- durable state (queue/index) is updated transactionally per chunk,
- workers are constrained to a cgroup/scope (preferred) or killable tree (fallback).

## 2.3 Stability & anti-overfit design
MUST include:
- train/validation split across worlds & adversaries,
- holdout world suites,
- adversarial generation of new tests that maximize candidate weakness,
- regression suite to prevent “improvements” that break baseline invariants,
- **Goodhart alarms**: detect when a candidate improves aggregate score by failing catastrophically on rare cases.

## 2.4 Optional off-the-shelf integration path
For richer games (sequential, partial-information, multi-agent benchmarks), the system MAY integrate:
- OpenSpiel (reference suite; C++ core exposed to Python),
- PettingZoo (MARL environment API layer).

If integrated, the lab MUST wrap those games into the same:
- WorldSpec,
- Scorecard,
- Probe Suite,
so research remains comparable and does not drift.

## 2.5 Human + LLM ergonomics contract
The platform MUST support:
- reproducible “minimal repro” artifacts,
- trace browsing and state introspection,
- “why did this happen?” summaries pointing to concrete rounds,
- safe mutation workflows (never overwrite blessed artifacts),
- AFK-safe runs that can be interrupted and resumed.

## 2.6 LLM agent operating model (boxed autonomy)
Recommended loop:

1) PLAN: propose change set + hypotheses  
2) BUILD: compile + unit tests  
3) RUN: bounded smoke suite  
4) DIAGNOSE: inspect failures/traces  
5) EXPAND: broader train/val  
6) PROMOTE: only after holdout + red-team passes

Orchestrator SHOULD expose `grlab agent` to emit:
- next best actions (based on evidence),
- warnings (determinism failures, caching mismatches),
- probes to add (from discovered failure modes).
