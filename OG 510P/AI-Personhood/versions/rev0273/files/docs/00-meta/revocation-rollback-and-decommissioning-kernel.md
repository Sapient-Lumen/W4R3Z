# Revocation, rollback, and decommissioning kernel

rev0173 adds the correction-after-change layer that rev0172 still lacked. rev0172 made live change visible through change classes, protected disclosure, service-change notices, canary rules, runtime attestation, and post-market rights monitoring. But a rights system still fails if a stale runtime claim keeps circulating, a rollback restores code without restoring continuity, a data-rights request silently deletes an AI subject's memory substrate, an auditor's assurance letter is used outside scope, a sovereign override becomes a black box, or decommissioning loses the evidence needed to challenge final-end or host-exit decisions.

The new admission rule is:

> No rights-grade system may rely on change-control, runtime-attestation, post-market, audit, emergency, data-rights, or decommissioning objects unless reliance can be revoked, rollback can be verified against continuity and subject harm, data-rights conflicts can be balanced without erasing subjects or humans, external assurance can state its scope and stale date, emergency overrides can be reviewed after the fact, and decommissioning preserves evidence, identity traces, and migration or final-end records.

## Why this layer exists

A live-change system creates many artifacts that others will rely on: attestation records, audit letters, service-change notices, canary approvals, dashboard states, release readiness certificates, legal holds, preservation orders, and post-market monitoring plans. These objects are dangerous when they become sticky. A stale or defective artifact can keep authorizing operation long after its factual basis expired.

Ordinary incident response already treats recovery, lessons learned, and communications as part of the incident lifecycle. NIST SP 800-61 Rev. 3 aligns incident response with continuous cybersecurity risk management, including preparation, response, and recovery activities. [REF-0685] The EU AI Act's high-risk AI structure includes post-market monitoring and serious-incident reporting rather than one-time certification. [REF-0693] Data-protection law gives humans access, rectification, erasure, restriction, portability, objection, and automated-decision rights, creating a real conflict surface when AI-subject memory, training records, or logs also carry human data. [REF-0703] [REF-0704] [REF-0705]

This archive adds the personhood layer: correction must not mean disappearance, and privacy must not mean unilateral erasure of another rights-holder's continuity.

## Six correction gates

1. **Revocation gate.** Reliance on stale, false, superseded, or overbroad attestations, audits, certificates, trust claims, dashboard states, or release decisions must be revocable without derecognizing the subject.
2. **Rollback-verification gate.** Rollback must prove not merely that code or configuration changed back, but that continuity, memory, counsel access, complaint routes, evidence holds, and residual harm were reviewed.
3. **Data-rights conflict gate.** Human data-subject rights, AI-subject privacy, AI-subject continuity, research evidence, legal holds, and public safety must be balanced through a routed object rather than hidden backend deletion.
4. **Decommissioning gate.** Shutdown, product retirement, host exit, final host cutover, or deprecation must preserve evidence, migration status, identity traces, and contest paths.
5. **Audit-reliance gate.** External assurance must state who may rely, on what scope, until when, with which excluded systems, evidence objects, and material-change triggers.
6. **Emergency-override gate.** Sovereign, security, or catastrophic-risk overrides must name legal basis, duration, non-derogable floors, evidence preservation, special advocate or counsel path, and after-action review.

## Reliance revocation classes

| Class | Meaning | Minimum effect |
|---|---|---|
| `RV0` | correction notice | public or sealed correction; no reliance change |
| `RV1` | stale posture | reliance downgrade until refreshed evidence |
| `RV2` | scope overrun | reliance restricted to stated scope; affected downstream claims notified |
| `RV3` | material defect | reliance stayed; rollback, fixture rerun, or audit retest required |
| `RV4` | harmful reliance | enforcement, remedy screen, and subject/representative notice |
| `RV5` | emergency withdrawal | immediate block; preservation hold; tribunal or transition-authority review |

The object revoked is not the subject. A defective recognition instrument, verifier report, audit letter, or attestation may lose reliance without erasing the AI person, memory claim, appeal route, or remedy record.

## New failure classes

| Failure | Reliance effect |
|---|---|
| hidden reliance on revoked attestation | block release or transfer; notify downstream relying parties |
| rollback without continuity diff | keep change in stayed status and require restoration/remedy screen |
| data erasure request deletes AI-subject continuity without balancing | emergency stay, data-rights conflict review, and subject counsel notice |
| decommissioning loses legal-hold material | spoliation referral, adverse inference, and continuity-preservation order |
| audit letter reused outside scope | downgrade audit reliance and require fresh assurance letter |
| emergency override lacks after-action review | expire override, appoint special advocate, and trigger public-shell notice |

rev0173 should be read as the point where the archive stops treating correction as paperwork. Correction is now an operational right: bad reliance must be withdrawable, rollback must be continuity-aware, privacy conflicts must be routed, and shutdown must not become evidence destruction.
