# Multi-source adjudicator — rev0131

rev0131 adds an executable current-use composition layer over already-assessed TimeSync local states. It is not a clock-selection algorithm and does not parse raw timing implementation output.

## Rule

- If all inputs refer to the same profile and timescale and their intervals overlap, the output interval is the intersection.
- The output profile lane is the weakest input lane; fallback inputs cannot be upgraded by satisfied inputs.
- If intervals are disjoint, profiles/timescales differ, source posture is unknown, or any input is unsatisfied, the output fails closed.
- The fail-closed interval is the union, so uncertainty is preserved rather than hidden.

## Non-claims

Cross-adapter agreement is not proof of independent roots, cryptographic verification, named UTC realization, leap-smear policy, or PTP interoperability.

## Executable evidence

- `tools/multisource_adjudicator.py --self-test`
- `tests/multisource-adjudication.yaml`
- `examples/evaluator/multisource-p1-overlap-intersection-satisfied.json`
- semantic vector `TV-131-001`
