# 172. Open research questions and experiment backlog

**Track:** Shared

This project is intentionally ambitious. Some parts are *deployable now* (Track A),
some are “hard-mode research” (Track B), and some require an ecosystem build-out (Track C).

This doc is the “don’t lie to yourself” list: where the hard questions live.

## 172.1 Recovery under dispute (shared)

- What is the minimal evidence package that a court/campaign/public can use to
  distinguish: operator mistake vs malice vs systemic compromise?
- How do we define “remedy” tiers (re-run, RLA expansion, precinct-level recheck, full recount)?
- How should evidence bundles be curated for adversarial narrative environments?

## 172.2 Verification ecosystem corruption (shared)

- How do we measure *representative coverage* for monitors and audits in a way
  that is hard to game (`148-challenge-selection-and-coverage-metrics.md`)?
- What is the right governance model for witnesses/monitors (consortium vs market vs mandated)?

## 172.3 Remote return realities (Track B)

- What meaningful coercion-mitigation exists in uncontrolled environments?
- What does “graceful failure” look like (if remote return is attacked, how does the system revert)?
- How do we avoid building “disaster bait” that encourages unsafe deployment?

## 172.4 North Star ecosystem build (Track C)

- What is the minimal viable endorsement transparency system to avoid capture
  (see `169-endorsement-and-reference-value-transparency.md`)?
- What is the practical intersection of RATS/EAT with supply-chain attestations (SLSA/in-toto)?
- How do we handle private manufacturing data while keeping public verifiability?

## 172.5 Meta-engineering questions (LLM-maintained archives)

- What changes should *require* ADRs?
- What is the best “release note” format for an evolving spec pack?
- What is the right balance between prose specs and machine-checkable schemas?

This backlog is intentionally not “owned” by a single person.
If you are an LLM maintainer: add candidates, but also add **what evidence would resolve it**.
