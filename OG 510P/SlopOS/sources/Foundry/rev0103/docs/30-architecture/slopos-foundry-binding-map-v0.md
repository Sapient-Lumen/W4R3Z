# SlopOS / Foundry binding map v0

Purpose: keep Foundry useful to SlopOS without letting Foundry absorb SlopOS authority.

Foundry owns **result meaning after projection**. SlopOS owns its boundary contracts, receipts, profiles, portal/replay semantics, and evidence emission. Sibling cubes own verdict, membrane, lifecycle, retention, artifact, and repair consequences.

## SlopOS surfaces that may need Foundry residue

| SlopOS surface | Foundry residue needed | Foundry must not decide |
| --- | --- | --- |
| `CH-OBS` export | observation-status card, grain card, query/result envelope, source cut | whether the observation is trusted or operationally sufficient |
| `CH-OBSPOL` export policy | disclosure cut, suppression witness, differencing fence, redaction classification pin | privacy-engine approval or publication authority |
| `CH-SNAPSHOT` / diagnostic support bundle | materialization cut, source cut, retention/drillback posture, result envelope | custody, repair outcome, or incident severity |
| attribute-query result | query contract, result envelope, validation witness, disclosure lens | policy authorization or identity/appraisal verdict |
| support-card table | classification pins, control totals, balance fences, observation-status cards | Ward-style trust appraisal or human action consequence |
| materialized support summary | materialization cut, refresh witness, reuse fence | cache product policy or freshness SLA ownership |
| boundary-family summary | classification pin, crosswalk witness, code-drift fence, hierarchy scope | SlopOS boundary-family membership authority |
| portal/network evidence summary | source cut, replay class, lineage/run card, result envelope | portal authority, network lease validity, or capability grant |
| replay/retry support view | query/result envelope, materialization cut, effect-key classification pin, prior-outcome anchor | effect finality or exactly-once claim |
| append/truncation/resume corpus summary | source cut, observation-status card, reconciliation witness, sidecar digest | SlopOS corpus completeness or substrate correctness |

## Residue survival rule

A SlopOS-facing surface that leaves Foundry must either:

1. carry relevant residue in-band;
2. carry a digest-linked `foundry_semantic_sidecar_v0`; or
3. refuse export/rendering with a clear flattening refusal.

## Companion boundary guard

| Companion | Foundry may consume | Foundry must not absorb |
| --- | --- | --- |
| Ward | verdict/appraisal labels as pinned classifications | trust verdicts, acceptance decisions, release verdicts |
| Harbor | outside-fact/correction/status residue as source cuts and aftermath links | membrane truth, compliance workflow, external authority |
| Steward | retry/replay/provisional reconciliation states as observedness/status inputs | lifecycle authority, effect finality, exactly-once truth |
| Schell | retention/minimization budgets that constrain drill-through | forgetting authority or privacy policy engine |
| ViewFS | artifact/projection/semantic-extraction outputs as derived surfaces | filesystem/object identity or path truth |
| Helm | repair-attempt traces and remainder bridges as operational evidence | repair custody, incident workflow, remediation authority |

## Non-goals

- no universal SlopOS datacube ontology;
- no Foundry ownership of SlopOS boundary naming;
- no taxonomy registry or terminology server;
- no policy engine;
- no support-workflow verdict system;
- no assumption that a sidecar authorizes export by itself.

## First consumer

Specimen 77 and the fixture harness are the first v0 consumer of this map. Future consumers should add rows here only when a concrete SlopOS or companion surface needs a specific residue family.

## rev0087 consumer-portability addendum

When a SlopOS-facing support surface is reused by a non-SlopOS consumer, Foundry must emit or verify:

| Source surface | Target consumer | Required Foundry residue | Foundry must not decide |
| --- | --- | --- | --- |
| SlopOS support-card dashboard | external audit notebook | consumer passport, portability witness, interpretation gate, sidecar digest, refusal/waiver links | audit opinion or policy approval |
| SlopOS support-card export | Ward appraisal queue | consumer passport, portability witness, interpretation gate, regression/receipt links | Ward trust or consequence verdict |
| SlopOS dashboard projection | ViewFS projection browser | consumer passport, portability witness, interpretation gate, attached-surface digest, expiry witness | ViewFS object identity or consent status |

The target consumer can receive residue. It cannot receive sibling authority through Foundry.
