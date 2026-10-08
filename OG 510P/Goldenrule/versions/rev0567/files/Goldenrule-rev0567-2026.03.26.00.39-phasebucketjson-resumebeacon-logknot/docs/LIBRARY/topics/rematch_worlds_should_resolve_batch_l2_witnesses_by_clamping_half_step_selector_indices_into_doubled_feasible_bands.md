# Rematch worlds should resolve batch L2 witnesses by clamping half-step selector indices into doubled feasible bands

Once a path-`L2` compromise request has already been reduced to one scalar selector key `half_step_selector_index = h`, witness selection no longer needs a separate selector-decoding step.

If the feasible overlap interval is `[a, b]` in source-rank coordinates, double that interval to `[2a, 2b]` on the same half-step lattice as the selector key. The feasible witness class is then exactly

`projected_half_step_witness_index = clamp(h, 2a, 2b)`.

This keeps both the request class and the selected witness class on the same `0..32` integer lattice:
- even outputs `2k` decode to singleton feasible witnesses `[k, k]`;
- odd outputs `2k+1` decode to adjacent feasible tie witnesses `[k, k+1]`;
- preserving the selector inside the doubled feasible band, clamping up to `2a`, and clamping down to `2b` are the only possible execution cases.

Practical consequence for inheritors:
- after feasibility is known, execute path-`L2` witness choice by one integer clamp instead of decoding a selector interval and then projecting it;
- on the current realized catalog this matched all `5,049` selector-class/interval cases exactly;
- the case split is simple and auditable: `1,785` preserves, `1,904` clamp to the lower boundary, and `1,360` clamp to the upper boundary;
- the witness output still lives on the same full `33`-class half-step lattice, so no extra output encoding is needed;
- infeasible families still fail for the old reason only, namely interval disjointness with its blocker certificate.

Do **not** confuse the clamped witness index with an exact mean, a preferred bundle summary, or a non-`L2` statistic.
