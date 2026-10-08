# Control coverage matrix and validator trace

This surface turns the ready-but-not-closed posture into a checkable coverage map. It asks one
question: for every known way `FT-0181` could be falsely closed, which validator, human artifact,
negative fixture, and release boundary catches it?

A control coverage matrix is not proof that any AI service works. It is proof that the archive knows
which controls exist, what they cover, and where they stop.

## CCM states

| State | Meaning |
|---|---|
| `CCM0` | no coverage matrix exists |
| `CCM1` | risks named but not tied to validators |
| `CCM2` | validators and artifacts tied to each risk |
| `CCM3` | negative fixtures and live followthrough boundary are covered |
| `CCM4` | real import closure reviewed against the matrix |
| `CCMX` | coverage claims are stale, circular, or overclaiming |

## Coverage rows

Each row should include:

- the risk or failure mode;
- the related fixture class, if one exists;
- the validators that detect the failure;
- the human surfaces or records that explain the decision;
- the expected closure effect;
- whether the row can ever close `FT-0181` by itself.

For `FT-0181`, the default answer to the last question is **no**. A control can block false closure;
it cannot itself supply the missing `SRC2+` pilot evidence.

## Minimum FT-0181 coverage

The matrix must cover these failure families:

| Family | Typical failure | Required posture |
|---|---|---|
| source truth | synthetic example relabeled as real import | block closure |
| protected route | protected support fact leaks into public record | reject or quarantine |
| authority | hidden action authority exceeds public/service record ceiling | block or downgrade |
| public claim | public summary exceeds evidence grade/source status | suppress claim |
| calibration | single reviewer or conflicted reviewer approves closure | require calibration/signoff |
| security | prompt/security payload or exploit detail imported as ordinary evidence | quarantine |
| burden | decision-neutral fields add collection burden | trim field |
| waiver | policy exception attempts to bypass non-waivable controls | block closure |
| release posture | release audit or assurance is treated as service evidence | block overclaim |

## Relationship to other late-stage controls

The coverage matrix sits above individual validators. It should name the validators, but it should
not replace them. It complements:

- [`import-negative-fixtures-and-failure-mode-catalog.md`](import-negative-fixtures-and-failure-mode-catalog.md);
- [`synthetic-example-labeling-and-source-status-controls.md`](synthetic-example-labeling-and-source-status-controls.md);
- [`policy-exception-and-waiver-control.md`](policy-exception-and-waiver-control.md);
- [`human-signoff-quorum-and-conflict-attestation.md`](human-signoff-quorum-and-conflict-attestation.md);
- [`ready-but-not-closed-assurance-case.md`](ready-but-not-closed-assurance-case.md);

- [`release-invariants-and-claim-boundaries.md`](release-invariants-and-claim-boundaries.md);
- [`artifact-dependency-graph-and-control-plane.md`](artifact-dependency-graph-and-control-plane.md);
- [`version-delta-manifest-and-change-accounting.md`](version-delta-manifest-and-change-accounting.md);
- [`recovery-drills-for-false-closure-and-leakage.md`](recovery-drills-for-false-closure-and-leakage.md);
- [`ft0181-closure-evidence-checklist.md`](ft0181-closure-evidence-checklist.md).


## Stop rule

Set the matrix to `CCMX` if a new validator, schema, public-summary route, import source, or waiver
path is added without a coverage row. Set it to `CCMX` if any row says it can close `FT-0181`
without real `SRC2+` source evidence and a closure-ready closeout.
