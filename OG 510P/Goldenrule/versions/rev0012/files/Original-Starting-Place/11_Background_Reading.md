# Background Reading & Practical Pointers (curated)

This list is not exhaustive. It highlights references that inform how we keep the lab reproducible and interpretable.


## Reading pack shipped with the repo
This repo includes a citation-first reading shelf under `reading/`:
- `reading/README.md`: annotated index by theme.
- `reading/links.yaml`: machine-readable metadata (extendable).
- `reading/bibliography.bib`: compact citation metadata.
- `reading/papers/README.md`: removal/compaction note for omitted PDF blobs.

Use it for two things:
1) Justify why a probe exists (“this test targets X failure mode in paper Y”).
2) Generate new probes by translating claims into falsifiable unit tests.

## Documentation patterns for transparency
- Model Cards: standardized reporting for models (intended use + evaluation boundaries).
- Datasheets for Datasets: standardized documentation for dataset composition + limitations.

Concord borrows this style for:
- ScorecardCards (definition + non-goals + failure modes),
- WorldDatasheets (suite composition + gaps).

## Tooling for quick tests and counterexample minimization
- Property-based testing frameworks: Hypothesis (Python) and proptest (Rust).
- Metamorphic testing: relations across runs when there is no oracle (addresses the “oracle problem”).
- Delta debugging / test case reduction: shrink a failure-inducing input to a minimal repro.
- Probabilistic model checking (PRISM): formal analysis for DTMC/MDP models (optional for small FSMs).

## Experiment tracking / run organization (optional UX accelerators)
- MLflow: logs parameters, metrics, artifacts and helps compare runs.
- Weights & Biases: artifact lineage graphs and run dashboards.
- DVC experiments: lightweight experiment management tied to Git without bloating the repo.

These are optional adapters; Concord’s source of truth is its local artifact store + manifests.

## IPD math and analytic tools
- Memory-one / finite-memory strategies can be represented as Markov chains; expected payoffs computed from stationary distributions.
- Press & Dyson (2012): zero-determinant/extortion analysis via stationary-state payoffs.

## Beyond IPD (optional phase)
- OpenSpiel (game research framework).
- PettingZoo (multi-agent environment API).
