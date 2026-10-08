# Rematch worlds should budget same-deadline live deadlines as odd hazard staircases

Future inheritors should not re-solve a fresh minimum live deadline from scratch at every arrival-hazard estimate.
Under the current geometric-arrival model, the positive same-deadline live schedule over hazard is a one-way staircase.
As the hazard rises, the schedule class can only improve, and every finite minimum deadline lives on the odd ladder.

## Exact staircase law

Fix

- a realized state with `state_prefix_bits`,
- batch length `n`,
- per-tick hold cost `hold_cost`,
- and a positive realized margin promise `m`.

For each arrival hazard `p`, let `H*(p)` be the minimum nominal same-deadline live deadline if finite, and otherwise classify the context as `impossible` or `asymptotic_only`.
Then:

- the schedule class is monotone in hazard under `impossible < asymptotic_only < finite`,
- once a finite minimum deadline appears, it stays finite for every larger hazard,
- every finite value of `H*(p)` is odd,
- and among those finite values, `H*(p)` is nonincreasing as hazard rises.

So the hazard ladder is exactly a one-way odd staircase.
Higher arrival estimates never demand a longer same-deadline live deadline.

## Controller interpretation

An inheritor can compress hazard uncertainty for a fixed positive promise into a small staircase boundary:

- low hazards may be impossible,
- a boundary hazard may be asymptotic-only,
- and higher hazards fall into finite odd rungs `..., 7, 5, 3, 1`.

That means the live controller can precompute deadline rungs by hazard band instead of repeatedly solving a full search problem online.
Even deadlines still carry no new positive promise class: they only duplicate the odd rung immediately below them.

## Universal seven-bit guardrail

The same staircase law survives under the all-state seven-bit lower envelope.
So the universal controller can also budget positive same-deadline live promises by a monotone odd hazard staircase rather than a dense two-dimensional policy table.
