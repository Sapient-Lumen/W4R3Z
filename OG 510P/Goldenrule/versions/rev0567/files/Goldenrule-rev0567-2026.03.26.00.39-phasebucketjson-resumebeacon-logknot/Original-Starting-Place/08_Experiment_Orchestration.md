# Experiment Orchestration (Python `grlab`) — UX, AFK safety, micro-lab, and autonomy

## 8.1 Core goal
Make experiments easy to run, hard to misinterpret, and impossible to lose.

This lab is built for an operator (human or LLM) with **significant autonomy**:
- you can add probes,
- change scorecards,
- invent new worlds,
- and take risks.

The system’s job is to preserve meaning and reproducibility while you do that.

## 8.2 Baseline CLI commands (required)
- `grlab doctor`
- `grlab run <experiment.yaml>`
- `grlab report <run_id>`
- `grlab frontier <run_id>`
- `grlab compare <strategyA> <strategyB> --suite holdout`
- `grlab reproduce <failure_id>`
- `grlab trace <failure_id>`
- `grlab mutate <strategy_id> --mode neighborhood`
- `grlab redact`

## 8.3 AFK commands (required)
- `grlab afk <experiment.yaml>`
- `grlab resume <run_id>`
- `grlab watch <run_id>`

## 8.4 Micro-lab commands (required)
- `grlab quick <strategyA> <strategyB> --probe <probe_id>`
- `grlab probe new --template ipd_noise --out probes/my_probe.yaml`
- `grlab probe run probes/my_probe.yaml --against <strategy_id>`
- `grlab trace --diff <failure_or_runA> <failure_or_runB>`
- `grlab shrink <failure_id>`
- `grlab metamorphic check <relation_id> --suite <suite_id>`
- `grlab certify <strategyA> <strategyB> --mode analytic`

## 8.5 Definition clarity tooling (required)
### Frozen evaluation snapshot (per run)
Every run MUST record an evaluation snapshot identifier:
- scorecard hash,
- probe registry hash,
- holdout registry hash.

Runs MUST store this snapshot in the manifest and display it in reports.

### Definition diff
`grlab defdiff <runA> <runB>`
Shows:
- what definitions changed,
- and how the frontier/rankings shifted.

This supports autonomy: you can change definitions, and still keep comparisons honest.

## 8.6 Confidence banners (gentle, useful)
Reports SHOULD include a “confidence banner” that summarizes:
- holdout status,
- sensitivity stability,
- tail-risk changes,
- metamorphic check status.

This is not scolding; it’s a quick way to know how much to trust a comparison.

## 8.7 Optional: experiment tracking integrations (ergonomics)
The lab MUST work fully offline with local artifacts.

Optionally, the lab MAY integrate with experiment tracking tools to improve UX:
- MLflow-style run logging (params/metrics/artifacts) for browsing and comparison.
- W&B-style artifact lineage graphs for run provenance.
- DVC-style experiment management for lightweight branching/compare without repo bloat.

If enabled, these are adapters only:
- the source of truth remains the local artifact store + run manifests.

## 8.8 Public-safe export (dual-use)
`grlab export <run_id> --public`
Must redact sensitive adversary implementations and recipe-level exploit triggers.

## 8.9 Human-facing translation (required)
Reports MUST include narrative summaries:
- probe id, round numbers, deltas,
- mapping to Golden Rule lenses,
- faithful to the trace.

## 8.10 AFK durability requirements (unchanged)
Durable queue + atomic commits + kill guarantees remain required.

## 8.11 LLM-safe mutation workflow (must)
No overwrites; new StrategySpec ids; promotion stores evidence.
