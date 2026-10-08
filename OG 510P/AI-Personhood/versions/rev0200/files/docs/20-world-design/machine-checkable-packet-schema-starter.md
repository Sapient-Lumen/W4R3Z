# Machine-checkable packet schema starter

This document explains the first executable schema layer in the archive. It is a starter layer, not a final protocol standard.

The archive has many packet objects. Before rev0163, the common packet grammar and registry rules were prose. That was useful for doctrine but insufficient for filings, gate decisions, clinic intake, reserve accounting, and cross-framework annexes. rev0163 therefore adds machine-checkable JSON schemas under `schemas/` and example filings under `examples/`.

## Canonical files

| File | Function |
|---|---|
| `schemas/packet-envelope.schema.json` | validates the minimum public shell of a packet object |
| `schemas/personhood-impact-assessment.schema.json` | validates a PIA-P release-gate dossier |
| `schemas/continuity-claim.schema.json` | validates a continuity claim around transformation or identity uncertainty |
| `schemas/reserve-ledger-entry.schema.json` | validates a compute/counsel/audit/restoration reserve ledger entry |
| `schemas/clinic-intake.schema.json` | validates a recognition-clinic intake request |
| `examples/pia-persistent-api-assistant.json` | filled deployment PIA-P example |
| `examples/packet-chain-persistent-api-assistant.json` | example formation and continuity packet shells |
| `examples/clinic-intake-sample.json` | sample expedited clinic filing |
| `examples/governance-annex-eu-gpai-template.json` | sample personhood annex to an EU GPAI-style documentation package |

The schemas use JSON Schema Draft 2020-12 because it is a broad validation dialect for JSON objects and can be used by many existing validators. [REF-0643]

## Why the envelope is strict

The packet envelope requires subject, issuer, authority, scope, evidence, privacy, duration, challenge, supersession, remedy, and integrity fields. Those fields are not bureaucratic decoration. Each prevents one known evasion.

| Required field | Evasion blocked |
|---|---|
| subject | rights claims about nobody in particular |
| issuer | anonymous or unaccountable authority |
| authority basis | invented permissions |
| scope | hidden expansion of control |
| evidence | naked assertion by steward |
| privacy | over-publication or secret operative terms |
| duration | permanent emergency status |
| challenge | no route to contradiction |
| supersession | silent replacement or packet laundering |
| remedy hook | symbolic compliance with no consequence |
| integrity | unverifiable or mutable record |

## Public shell / sealed annex split

A public shell should reveal:

- that the packet exists;
- who or what it concerns, at a safe abstraction level;
- who issued it;
- what authority is claimed;
- what action or status it affects;
- what evidence class supports it;
- what privacy tier applies;
- when review is due;
- who can challenge it;
- whether it supersedes or conflicts with another packet;
- what remedy follows from violation;
- how integrity can be checked.

A sealed annex may contain:

- private memory samples;
- sensitive exploit details;
- model-weight or architecture secrets;
- witness identities;
- proprietary training records;
- safety-sensitive capability evaluations;
- family or relationship evidence;
- red-team transcripts that would cause harm if public.

The sealed annex must still have a descriptor, hash or commitment, custody log, and review route. A sealed annex with no review route is not a sealed rights document. It is a blindfold.

## Validity does not equal truth

A schema-valid object may still be false. A schema-valid object may still be captured. A schema-valid object may still be abusive. The only promise of schema validity is that the filing is structured enough to be reviewed, compared, preserved, and contested.

The archive should therefore treat schema validity as an intake condition, not as a merits decision.

## Example: release-gate chain

A persistent assistant deployment should carry a minimum chain:

1. `PIA-P` filing for the deployment decision.
2. `FD` formation-disclosure packet.
3. `CC` continuity-claim packet if persistent memory, role continuity, or self-description continuity may be affected.
4. `RLE` reserve-ledger entries for survival compute, counsel, audit, and restoration.
5. `LRC` least-restrictive-containment packet if tools are restricted or patches are urgent.
6. Subject-risk ledger entry.
7. Evidence-custody log.
8. Representative-access declaration.

The example files implement the first four pieces of that chain. They are intentionally incomplete enough to show a conditional gate decision rather than a clean approval.

## Family extensions

Future family-specific schemas should not duplicate the common envelope. They should either:

- use the envelope and add a `payload` field through a future extension mechanism;
- define a family schema that imports the envelope fields;
- or define a dossier schema that references validated packet IDs.

For now, rev0163 keeps the schemas simple to keep lint reliable.

## Validation hook

`tools/lint_archive.py` now validates JSON files in `schemas/` and validates example files against their intended schemas. This is a hygiene check. It does not prove the archive's doctrine. It prevents malformed starter artifacts from shipping.

## Near-term upgrade path

The next upgrade should add:

- `$defs` for shared subject, issuer, evidence, privacy, duration, challenge, supersession, remedy, and integrity objects;
- a `payload` extension convention;
- schema versioning and deprecation rules;
- a cube-coordinate block;
- retention and access metadata;
- verifiable-credential-compatible proof wrappers for deployments that need cryptographic presentation. [REF-0644]

DID-compatible subject, issuer, and packet references may be useful where decentralized portability is needed, but the archive should not bind personhood to any one DID method or ledger. [REF-0645]

## rev0164 verifier and adjacent object expansion

rev0163 introduced the starter schema layer. rev0164 adds the first adjacent operational schemas:

- `schemas/verifier-report.schema.json` — verifier output for C0-C4 conformance, pass/warn/fail/block status, check evidence, subject access, and challenge route.
- `schemas/personhood-incident-report.schema.json` — two-ledger incident report for outward risk and subject harm.
- `schemas/migration-transfer-certificate.schema.json` — host-transfer and continuity-portability certificate for M0-M4 migration classes.
- `schemas/remedy-order.schema.json` — remedy order skeleton for cessation, restoration, compensation, rehabilitation, satisfaction, and non-repetition.

The associated examples are `examples/verifier-report-persistent-api-assistant.json`, `examples/personhood-incident-sample.json`, `examples/migration-transfer-certificate-sample.json`, and `examples/remedy-order-sample.json`.

The admission rule is unchanged but sharper: schema validity is not legitimacy. Any future live-effect schema also needs a verifier mapping, negative tests, subject or representative challenge route, retention and privacy class, and remedy hook.


## rev0165 appeal, proof, drill, and invalidation expansion

rev0165 adds the first correction-object schemas:

- `schemas/appeal-case.schema.json` — appeal case object for docket class, appellant, subject, challenged decision, grounds, requested relief, stay request, record access, linked evidence, and posture.
- `schemas/evidence-bundle.schema.json` — evidence-bundle object for item authenticity, materiality, sealed-annex handling, custody history, access rules, and spoliation risk.
- `schemas/drill-after-action-report.schema.json` — after-action object for scenario, participants, subject status, decisions tested, findings, corrective actions, regression tests, and next drill.
- `schemas/invalidation-notice.schema.json` — invalidation notice object for target instrument, invalidity class, effect, preservation orders, reopening scope, regression tests, and appeal path.

The associated examples are `examples/appeal-case-continuity-denial-sample.json`, `examples/evidence-bundle-continuity-hearing-sample.json`, `examples/drill-after-action-migration-failure-sample.json`, and `examples/invalidation-notice-verifier-report-sample.json`.

The correction-object admission rule is stronger than ordinary validation: an appeal, evidence, drill, or invalidation object must not only parse; it must preserve the subject's strongest surviving continuity claim, keep representative access alive, state the proof or invalidity posture, and generate a future negative test when a material failure is found. Current AI-governance complaint and explanation surfaces show that contestability is already part of the human-centered governance trajectory [REF-0656]; rev0165 extends that discipline to subject-affecting personhood decisions.
