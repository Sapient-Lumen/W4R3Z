# Engineering pilot cross-case memo: numeric assumptions

Revision: `rev0003`

The first three engineering records were not chosen merely because they are famous. They were chosen because they test whether the cube can hold three things at once:

1. a concrete official-source incident record;
2. a causal chain specific to that incident;
3. a cautious cross-case pattern that does not overrun the evidence.

## The provisional pattern

`MKH-PAT-0001`: numeric representation assumptions escaped their valid domain.

The pattern currently includes:

- **Mars Climate Orbiter:** impulse units crossed a software-interface boundary at the wrong scale.
- **Ariane 5 Flight 501:** a reused computation encountered values outside the numeric range assumed under a prior flight envelope.
- **Patriot Dhahran:** time conversion precision loss accumulated under an uptime regime outside expected use.

## Why this is not just “software bug”

Calling these “software bugs” is too coarse. In each case, software represented a physical or operational quantity: impulse, horizontal velocity, or time. The danger came when the representation crossed a boundary that the surrounding system did not check adequately.

That boundary differs by case:

- organizational/interface boundary for MCO;
- mission-envelope/reuse boundary for Ariane;
- operational-duration/precision boundary for Patriot.

## Negative controls needed

Before this becomes a synthesized pattern, the archive needs cases where similar risks were caught:

- a units mismatch detected before flight;
- a range overflow caught by test-envelope expansion;
- a time-precision drift caught by operational reset rules or simulation;
- a reused component rejected because its assumptions did not match a new system.

Without negative controls, the pattern risks becoming anecdotal overfit.

## Query primitives unlocked

The pilot makes these future queries possible:

- Show me failures where the encoded unit differed from the consumer’s expected unit.
- Show me failures where a reused component carried hidden assumptions from a previous operating envelope.
- Show me failures where uptime or accumulated state invalidated a precision assumption.
- Show me official recommendations that would have caught the numeric assumption before field exposure.
