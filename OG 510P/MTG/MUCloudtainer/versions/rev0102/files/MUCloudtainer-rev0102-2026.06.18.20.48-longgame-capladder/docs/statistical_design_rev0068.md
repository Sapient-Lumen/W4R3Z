# Statistical design correction — rev0068

## Separation of gates

MUC-5 should maintain two distinct gates.

### Operational integrity gate

Checks:

```text
matrix completeness
minimum total execution count
no truncations or Python errors
forensic/feature/ownership rerun coverage
C++ support and mismatch status
replay status
public-information and target-ownership invariants
```

Passing this gate means the experiment ran as specified. It does not establish a strategic claim.

### Inference gate

Future checks:

```text
preregistered primary estimand
per-cell precision or sample target
paired seed allocation where valid
frozen holdout seed family
confidence interval for the policy delta, not only each arm
adaptive-stopping record
multiple-comparison handling
robustness across a fixed opponent population
```

Passing this gate may support a claim within its registered scope.

## rev0068 code correction

A missing response-policy row previously became score `0.0` and could be called a refutation. The comparator now emits nulls and `incomplete_matrix`; the gate requires all 18 combinations of three size axes, three threat policies, and two life totals.

## rev0067 evidence status

The current response matrix is exploratory. It is useful for selecting pressure points, but many cells have 8–24 games and broad intervals. No point-estimate label should be promoted to a robust-policy claim until a preregistered paired holdout or policy-population evaluation is run.
