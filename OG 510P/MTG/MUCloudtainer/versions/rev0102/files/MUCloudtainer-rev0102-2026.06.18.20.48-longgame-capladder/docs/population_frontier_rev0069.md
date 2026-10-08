# Population frontier — rev0069

rev0069 moves the counter/threat work from a chain of named duels into a small rectangular empirical-game pilot:

```text
counter policies: legacy_cf34_counter_ranker, public_counter_guard
threat policies:  library_aware_threat_closure_targetguarded, jace_pressure_threat_response, face_protect_threat_surge
size/life cells:  counter40_vs_threat40, counter60_vs_threat40, counter60_vs_threat60 × life 20/40
```

The runner executes 18 arms × 2 life totals × 2 target seats × 2 starting-player parities × 1 rep = 144 games. It writes the raw game rows, arm summary, mechanism summary, a 240-row C++ transition sample, and one security row per size/life context.

## Why this matters

rev0065-0067 were useful but still formed a response treadmill: repair counter, repair threat, add surge, compare pairwise. The population frontier instead asks the operational question a claim gate actually needs:

```text
Given this frozen threat population, what is each counter policy's worst-case floor?
Given this frozen counter population, which threat axis is the best response?
Is the rectangular policy matrix complete, or are we accidentally making a claim from missing cells?
```

## Results

The inherited rev0065-0067 summaries had zero complete 2×3 counter-policy population cells because legacy CF34 was never evaluated against pressure or surge. rev0069 closes that specific pilot gap with seed-disjoint games and reports six complete size/life cells.

The run was operationally clean:

```text
games: 144
C++ supported transition events: 24,533
C++ mismatches: 0
Python errors: 0
truncations: 0
complete population cells: 6/6
```

The results remain pilot evidence, not confirmatory inference. Each arm has only four games after seat and starting-player balancing. The value is that the missing-cell blocker has been converted into a runnable empirical-game surface with explicit worst-case floors.

## Sharpest pilot read

The population view is much harsher than single best-looking cells. Worst-case pure security values across the six contexts range from 0.00 to 0.75. That means the next substantive work should not promote either counter policy globally; it should enlarge the complete population matrix with preregistered reps and precision targets.
