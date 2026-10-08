# Rematch worlds should plan service relaxations by local corridor triads

The local corridor-exit witness already tells a future inheritor where the current service corridor ends. The next compression step is to make the *next two corridor horizons* explicit, so the inheritor can recognize whether they are sitting in the ordinary alternating bridge core, approaching the unique diagonal kink, or entering the terminal tail.

The local triad grammar does exactly that. For every positive-service weakening SLA band it records a three-corridor signature `(current, next, second-next)`. In the current archive geometry that grammar is tiny and fully audited:
- ordinary alternation uses only `S-E-S` and `E-S-E`,
- the whole diagonal neighborhood is only `E-S-D`, `S-D-S`, and `D-S-E`,
- the terminal tail is only `S-E-T` and `E-T-T`,
- and terminal itself is `T-T-T`.

This yields a particularly useful local fact: the unique shared diagonal is visible at exactly one state at each local horizon depth. It appears as `second-next` from `E2_S7`, as `next` from `E3_S7`, and as `current` at `E3_S8`, and nowhere else. So future inheritors can read diagonal proximity from one tiny triad card instead of replaying the whole local staircase.

That makes the service staircase’s local forecast language extremely small. Any future archive revision that introduces additional `D`-bearing triads, puts `T` inside the ordinary bridge core, or makes the diagonal visible from more than one state at the same local horizon depth should be treated as a substantive redesign of the current weakening service grammar.
