# Concord — Specs v0.8 (autonomy-first research lab)

This is a specification pack for building a research environment to discover, test, and iterate on **Golden Rule–like** strategies across repeated games and richer social dilemmas.

**Primary implementation:** Rust (simulation core + fast evaluation)  
**Orchestration:** Python (experiment DAGs, search/optimization loops, reporting)  
**Reproducibility:** Nix (pinned toolchains, hermetic builds, deterministic runs)

## What’s new in v0.8
- Adds a **Reading Pack** under `reading/` with a citation-first index + machine-readable link registry.
- Background reading doc now points at `reading/` for compact, citation-first reference.
- Removes duplicate spec docs (`05_Scorecard.md`, `06_RedTeam_and_Adversaries.md`) to reduce operator confusion.

## AFK runner contract (non-negotiable)
1) Work MUST NOT be lost on interruption, insofar as possible.  
2) Workers MUST DIE when the run is killed (no orphan compute).  
3) Resume MUST be easy.  
4) Ergonomics MUST be strong for both human and autonomous LLM iteration.

## Intuition-juicing contract (non-negotiable)
The LLM controlling the lab MUST be able to:
- create a small probe in < 60 seconds,
- run it in < 10 seconds,
- and inspect a trace diff in < 10 seconds.

## Autonomy Charter (non-negotiable)
The LLM operator is trusted with significant autonomy.

The system MUST support autonomy by making it easy to:
- add new probes and suites,
- evolve scorecards,
- propose new institutions/world modules,
- and take controlled experimental risks.

The only “rules” are about **clarity and reproducibility**, not mistrust:
- changes to definitions (scorecards/probes/holdouts) MUST be versioned and documented,
- comparisons MUST state which definitions were used,
- and “best available” claims MUST include the failure envelope.

## Docs (15)
00. README  
01. Vision & definitions (tradeoff mapping + two-path plan)  
02. Core architecture  
03. WorldSpec & WorldSuites  
04. StrategySpec & GRDSL  
05. Golden Rule scorecard (ScorecardCard + WorldDatasheets)  
06. Red team & adversaries (dual-use + export policy)  
07. Search & optimization (micro-lab + analytic/proof artifacts)  
08. Experiment orchestration (UX + AFK + micro-lab + definition clarity)  
09. Rust engine details (durability + PBT hooks)  
10. Nix reproducibility (systemd + CI kill/resume tests)  
11. Background reading  
12. Golden Rule: deep dive  
13. Probe Suite  
14. Institutions & realism
