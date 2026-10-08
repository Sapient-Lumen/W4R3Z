# rev0007 sparring-agent probe

rev0007 adds two crude named agents to make the gametable less monocultural:

```text
random
heuristic
counter_happy
threat_rush
```

A tiny probe was run across:

```text
4 agents
4 seed decks
ordered agent pairs
ordered deck pairs
20 and 40 starting life
land_band mulligan agent
512 games total
```

Artifacts:

```text
data/rev0007_sparring_agent_probe.csv
data/rev0007_sparring_agent_probe_summary.json
data/rev0007_sparring_agent_probe_stdout.txt
```

## Important caveat

The probe is not MUC theory. In this small run, `random` is not obviously crushed by the heuristic family. That should be treated as a warning that the current heuristics are weak and that the simulator still needs richer evaluation, not as evidence that random play is strong.

This is actually useful: the payoff-table builder should preserve weak/weird agents because brittle strategies often look good only against a narrow opponent set.

## Why this matters later

A future PSRO-like loop can treat a strategy as a bundle:

```text
deck constructor + mulligan policy + pilot policy
```

Then a population contains things like:

```text
counter-heavy construction + counter_happy pilot
Overlord-heavy construction + threat_rush pilot
probe-shortlisted robust deck + heuristic pilot
learned policy/value pilot
external/LLM-generated code policy
```

rev0007 only seeds the table and opponent diversity needed to get there.

