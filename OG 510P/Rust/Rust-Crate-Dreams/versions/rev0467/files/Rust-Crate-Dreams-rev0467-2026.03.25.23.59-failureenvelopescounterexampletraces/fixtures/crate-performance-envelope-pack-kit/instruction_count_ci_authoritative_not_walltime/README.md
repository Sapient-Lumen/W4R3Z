# instruction_count_ci_authoritative_not_walltime

A crate wants one CI-gated performance scenario for a parser hot path.
Locally, maintainers inspect wall-clock timing with Criterion or Divan, but the authoritative CI gate uses Iai-Callgrind instruction counts.

The fixture exists to force the pack to record:

- that one scenario can have multiple supporting measurements,
- that `instructions` can be authoritative while wall time remains only locally informative,
- and that the trust class for the scenario should be tied to the selected metric rather than copied from another runner.

Expected artifact pressure:
- `metric-authority.policy` should select `instructions`.
- `environment-fidelity.receipt` should record the Callgrind-based capture context.
- `noise-class.report` should allow `ci_reliable` for instructions while leaving wall time outside the authoritative lane.
