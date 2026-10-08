# Rematch worlds should treat positive-service weakening SLAs as a one-diagonal staircase

The recent width-only weakening portfolio passes already gave two exact support horizons:

- exact-only horizon `E(s)`
- suffix-only horizon `S(s)`

That still leaves a small nuisance for an inheritor:

> how many genuinely different positive-service SLA schedule states are there, and how do they change as the target service share relaxes?

The new staircase law answers that cleanly.

Positive-service targets do not form a vague continuum of schedules. They collapse to **17 canonical states** indexed by `(E,S)`, starting at `(0,0)` and ending at `(6,11)`.

As the target service share decreases, the archive walks a monotone staircase through those states. Every threshold crossing does exactly one of three things:

- add one suffix support unit
- add one exact support unit
- or, once and only once, add one of each together

That unique diagonal event happens at the shared threshold `1/91`, where the staircase moves from `E3_S8` to `E4_S9`.

So the positive-service geometry is not just finite. It is a **serial path**:

- `10` suffix-only steps
- `5` exact-only steps
- `1` shared diagonal step

with path word `SSESSSESSESDSESE`.

This is a tighter mental model for the inheritor than the raw band tables. A positive-service SLA target is now just a location on one audited staircase.

The zero-service case stays separate: target `0` is the degenerate full-support signature `E15_S15`, which sits off the positive-service staircase.

Future redesign signal: any extra diagonal step, any jump larger than one support unit on an axis, or any non-monotone move means the weakening SLA geometry has substantively changed.
