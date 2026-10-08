# For Gwern

Lacuna is a research gift prompted by [“Better Fiction via Retcon Planning”](https://gwern.net/blog/2026/llm-retcon). It is not a claim that retcon planning already works, and it is not another fiction-writing prompt.

The narrow claim is:

> Retcon planning needs an executable custody and experiment boundary, or a long-context model can silently blur observed canon, private hypotheses, rejected futures, evaluator preference, and accepted world state.

Lacuna supplies that boundary as a dependency-free Python/SQLite kernel plus managed sidecars.

## What is implemented

The article’s six-stage loop maps to concrete artifacts:

1. **Canon:** typed, sourced, audience-scoped observations and exact accepted narration custody.
2. **Hypotheses:** plural candidate worlds and explicit unknowns rather than one hidden truth paragraph.
3. **Resampling:** exact candidate count and exact bounded rollout beats at a source-bound checkpoint.
4. **Selection:** provenance-stripped candidates, a fixed rubric, checked arithmetic, and deterministic tie-breaking.
5. **Compression:** winner-only bounded state-card custody with narrow write authority.
6. **Forgetting:** an authenticated fresh-narrator continuation dispatch that excludes rejected candidates, rollouts, scores, verifier findings, and parent history. The strongest path can bind a checkpoint-defined complete census of every durable pre-checkpoint audience turn whose exact prose survives in retained managed runs; an explicit run list remains available but is labeled partial rather than silently treated as complete.

The commitment-budget warning is also operational: observed facts, disclosures, commitments, fair-play seals, and explicit consequences have different revision costs and leave forward repair custody rather than being overwritten.

## What is not claimed

Lacuna does not call a model, prove provider isolation, guarantee candidate diversity, validate an aesthetic rubric, parse prose entailment, or show that the method improves fiction. Before blind rating, the scenario runner searches every retained regular-file body and relative pathname under each frozen cell—including cube databases, SQLite sidecars, and locks—for preregistered exact canaries. A clean scan is falsification pressure, not proof of memory erasure, semantic independence, or filesystem confinement.

The actual experiment should therefore use fresh API calls or genuine subagent contexts. One long ChatGPT conversation remains a useful playtest and a deliberately confounded control, not the clean forgetting condition.

## The shortest appraisal path

From the extracted archive:

```bash
./lacuna --version
sha256sum -c MANIFEST.sha256
./lacuna artifact check --strict-members --format markdown
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 tools/run_acceptance.py --timeout 60
```

For the expanded deterministic suite:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 tools/run_acceptance.py --all-modules --timeout 60
```

For exhaustive opt-in verification, install the schema test extra and run finer bounded shards with `--all`:

```bash
python3 -m pip install -e '.[test]'
for shard in $(seq 1 32); do
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 tools/run_acceptance.py --all --timeout 90 --shard "${shard}/32"
done
```

For the design argument, read [`docs/design/GWERN_GIFT_TEST.md`](docs/design/GWERN_GIFT_TEST.md). For the executable comparative protocol, read [`docs/operators/SCENARIO_CAPSULES.md`](docs/operators/SCENARIO_CAPSULES.md) and [`docs/operators/SCENARIO_BUNDLES.md`](docs/operators/SCENARIO_BUNDLES.md).

A small local setup begins with:

```bash
rm -rf /tmp/lacuna-gwern-seed /tmp/lacuna-scenario-runs
./lacuna demo /tmp/lacuna-gwern-seed
./lacuna scenario template /tmp/lacuna-gwern-seed > /tmp/lacuna-scenario.json
```

Edit the two scripted player inputs and declare the model/sampling policy in `/tmp/lacuna-scenario.json`, then freeze the four-condition comparison:

```bash
./lacuna scenario begin /tmp/lacuna-gwern-seed \
  /tmp/lacuna-scenario.json \
  --root /tmp/lacuna-scenario-runs \
  --format markdown
```

Thereafter follow only the emitted run’s `NEXT.md`. The path is intentionally serial and explicit: opaque condition dispatch, exact return, whole-retained-tree pre-rating contamination scan, blind rating, then unblinding. The replicated bundle layer adds all-blocks-before-any-unblind custody and rater-level export.

## Why this may be useful even if the hypothesis fails

A negative result would still be informative. The four primary conditions separate forward-only narration, prompt-only retconning, Lacuna with serial roles, and Lacuna with fresh role contexts plus a fresh narrator. Mechanical failures—stale artifacts, context reuse, hidden-state leakage, unsupported success, commitment repair, and exact canary matches—remain distinct from human judgments of coherence, agency, payoff, coincidence restraint, and enjoyment.

That makes it possible to learn whether the value comes from retcon search, typed custody, context reset, role separation, or none of them, without treating one persuasive transcript as the experiment.
