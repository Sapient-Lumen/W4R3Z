# Software supply-chain and provenance discipline

`SOFTWARE-SUPPLY-CHAIN-LEDGER.json` records source, dependency, build, container, model-weight, workflow, and generated-artifact provenance for support-bearing computational rows.

## Stop rule

A code result is non-spendable above custody/prose status if the source, dependencies, build inputs, model weights, external services, binaries, or generated artifacts cannot be traced to a frozen or auditable state.

## Required provenance checks

| Check | Question | Failure mode blocked |
|---|---|---|
| source identity | Which exact source revision, archive identifier, or content hash was used? | moving-repository drift |
| dependency lock | Which packages, libraries, compilers, runtimes, services, and model weights are pinned? | dependency upgrade laundering |
| build provenance | Can the build inputs, builder, parameters, and produced artifacts be reconstructed or attested? | opaque binary trust |
| generated-artifact trace | Which generated summaries, catalogs, plots, proofs, or likelihood files came from which source command? | generated-output orphaning |
| vulnerability / tamper posture | Are there known compromise, supply-chain, or untrusted-external-service risks? | replaying a compromised artifact |
| citation / credit metadata | Is the software citable and discoverable without confusing citation with evidence? | software-citation-as-support laundering |
| retirement rule | What happens if the repository disappears, the SWHID/hash breaks, or the dependency graph becomes unreplayable? | silent software decay |

## Authority ceilings

Supply-chain integrity can establish that a computational artifact is identifiable, inspectable, and less tamper-prone. It does not establish that the artifact is correct, scientifically adequate, numerically stable, independently replicated, or candidate-identifying. Those debts remain with the computational-replay, numerical-stability, evidence-credit, update, measurement, validity, causal, selection, capacity, semantic, social-authority, and rollback ledgers.

## Non-promotion rule

Supply-chain integrity protects replay and tamper resistance. It does not create candidate-native evidence, independent confirmation, or closure.

- Additional software-identity anchors: `REF-0284`, `REF-0288`; software-citation and software-metadata anchors: `REF-0282`, `REF-0289`.
