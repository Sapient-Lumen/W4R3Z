# Computational artifact risk taxonomy

This surface names route-local failure modes introduced by code, workflows, containers, generated summaries, proof assistants, notebooks, catalogs, simulations, benchmark harnesses, solver stacks, and software supply chains.

The controlling open question is `OQ-0071`; the controlling ledgers are `COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json`, `NUMERICAL-STABILITY-LEDGER.json`, and `SOFTWARE-SUPPLY-CHAIN-LEDGER.json`.

## Risk classes

| Risk | Looks like | Must not be retold as |
|---|---|---|
| runnable-but-unreplayed artifact | code or container exists | reproduced result |
| author-local replay | original team can rerun workflow | independent confirmation |
| benchmark overfit | artifact wins declared benchmark | candidate-native inverse map |
| generated-summary orphan | summary table exists without trace to command/source | public-record carrier |
| proof-script brittleness | proof replay depends on fragile library/kernel state | theory-level proof closure |
| stochastic cherry-pick | favorable seed/split/training run survives | robust generalization |
| floating-point nondeterminism | parallel order, hardware, BLAS, compiler, or precision changes output | stable observable |
| tolerance-sensitive solver | convergence/stopping rule changes route language | severe support |
| dependency drift | package update changes output | same artifact |
| opaque binary / service | executable, model, API, or firmware cannot be audited | public replay |
| container polish | well-formed container masks unstable inputs or outputs | reproducibility |
| software-citation polish | package has DOI/SWHID/metadata | physical evidence |
| supply-chain attestation | build provenance is present | scientific correctness |
| metadata wrapper | clean provenance and indexing | route promotion |

## Cross-ledger consequences

- Replay failure triggers rollback before severity, contrast/update, prediction, or consensus language may be used.
- Numerical instability triggers measurement/update and capacity/selection caps before it is treated as disagreement among candidates.
- Software supply-chain failure is a custody defect first; it does not prove the scientific claim false, but it can make the claim non-spendable.
- Successful computational replay can at most support the route-local computational object unless negative controls, public-record carriers, measurement models, validity domains, and claim-language permissions also clear.

## Non-promotion reminder

Computational artifact quality is necessary for code-backed claims and generated summaries. It is not an extra physical experiment, not an ontology commitment, not an independent route, and not a candidate-native closure event.

- Numerical-stability anchors: `REF-0286`, `REF-0287`.
- Software-identity / supply-chain anchors: `REF-0284`, `REF-0288`.
- Software-metadata and citation anchors: `REF-0282`, `REF-0289`.
