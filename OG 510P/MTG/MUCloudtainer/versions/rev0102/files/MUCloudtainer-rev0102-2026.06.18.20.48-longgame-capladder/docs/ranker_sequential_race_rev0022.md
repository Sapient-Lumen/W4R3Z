# rev0022 ranker sequential race

rev0022 adds a staged race for a mixed ranker/code/public population.

Candidate bundle =

```text
deck construction + mulligan policy + public pilot
```

The race uses the existing cautious elimination rule:

```text
collect stage games
compute bounded-score intervals
eliminate only if candidate UCB + slack < best candidate LCB
```

This is not a formal optimal racing algorithm. It is a cloudtainer-bound budget tool. Its job is to avoid spending full matchup budgets on candidates that are already clearly behind, while keeping uncertainty visible.

## rev0022 candidate panel

```text
ranker_fjace
ranker_threat_fovr
ranker_counter_wall
ranker_patient_jace60
code_clock_fovr
code_jace60
```

Benchmark opponents:

```text
pub_counter_wall
pub_threat_overlord
pub_patient_sixty
code_force_wall
code_clock_fovr
code_jace60
```

The race writes:

```text
data/rev0022_ranker_race_games.csv
data/rev0022_ranker_race_aggregate.csv
data/rev0022_ranker_race_standings.csv
data/rev0022_ranker_race_candidate_standings.csv
data/rev0022_ranker_race_pairwise.csv
data/rev0022_ranker_race_stat_standings.csv
data/rev0022_ranker_race_stages.json
data/rev0022_ranker_race_replay_traces.jsonl
data/rev0022_ranker_race_replay_results.json
data/rev0022_ranker_race_cpp_trace_rows.csv
data/rev0022_ranker_race_cpp_trace_summary.json
data/rev0022_ranker_race_summary.json
```

## Gate policy

The race output is promotable only if all of these remain clean:

```text
promotion gate
statistical gate
Python deterministic replay samples
C++ recorded-trace transition checks
reward/truncation labels
```

A ranker can lose the race and still be useful: losing early under a clean gate is information about data/model limitations.
