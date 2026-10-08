---
id: ss-0187-custody-break-certificates
revision_promoted: rev0187
title: Custody-break certificates become litigation and assurance artifacts
constellation:
- managed-legibility
- adversarial-governance
- standards-and-conformance
status: dossier
maturity: S2-artifact-emerging
confidence: medium
time_horizon: near
domain:
- audit / assurance
- legal / litigation / discovery
- AI / model governance / automated decisions
- product identity / passports / traceability
bottleneck_type:
- provenance / custody
- admissible evidence
- fraud resistance
- appealability / redress
- underwritability
enforcement_surface:
- litigation / discovery
- audit / attestation / assurance
- underwriting / insurance renewal
- certification / conformity assessment
artifact_type:
- custody-break certificate
- lineage exception
- reliance caveat
- holdback schedule
lifecycle_stage:
- dispute
- correct
- archive
- rely
failure_modes:
- lineage-gap
- broken-signature-chain
- unverifiable-source
- redaction-laundering
- manual-rekeying
refactor_cluster:
- provenance-lineage
- remedy-lifecycle
- exposure-liability
lineage_role: auditor-regulator and custodian-escrow
lineage_stage:
- dispute
- correct
- archive
- verify
remedy_role: evidence-reviewer and correction-recipient
remedy_stage:
- admissibility
- review
- outcome
- closure
state_family:
- provenance
- remedy
- exposure
state_terms:
- lineage-gap
- signature-chain-broken
- provenance-disputed
- archive-evidentiary
- coverage-position-reserved
- reserve-held
- subrogation-impaired
consolidation_status: standalone-mechanism
evidence_grade: E2-signal-cluster
decision_grade: DG-B
decision_total: 15
source_refs:
- S1565
- S1570
- S1571
- S1572
exposure_role: claims-reviewer and auditor-regulator
exposure_stage:
- classify
- defend
- reserve
---
# Custody-break certificates become litigation and assurance artifacts

## Core claim

Proof systems often fail in a boring way: a log is missing, a source system aged out, a file was manually rekeyed, a signature chain broke, a resolver migrated, a redaction cannot be reconstructed, a vendor transformed data without retaining code, or a service provider cannot prove which input produced the output. Today these failures are often described informally as caveats.

**Custody-break certificates become litigation and assurance artifacts** when a missing or unverifiable segment in the evidence chain must be formally declared, scoped, priced, and routed into remedy. The certificate does not repair the break. It prevents the break from masquerading as ordinary provenance.

## Why this belongs in the archive

PROV, SLSA, in-toto, and SPDX all push toward explicit process, source, artifact, and responsibility metadata [S1565][S1570][S1571][S1572]. But explicit lineage also reveals gaps. Once institutions rely on proof objects, the failure state itself needs a controlled representation.

The archive has already modeled appeal stays, non-reliance packet states, correction materiality, and source-witness nonresponse. Custody-break certificates connect those families to provenance. They answer: what exactly is missing, what can still be relied on, which uses are blocked, and what cure is possible?

## Certificate contents

A useful custody-break certificate includes:

- affected object and subject;
- missing segment type: source, transform, signature, resolver, redaction, retention, transfer, or archive;
- time window and responsible custodian;
- whether the break is technical, procedural, adversarial, legal, or unknown;
- remaining trustworthy fields;
- prohibited reliance classes;
- allowed limited reliance classes;
- required holdback, manual review, or non-reliance state;
- evidence requests outstanding;
- cure path and deadline;
- appeal or dispute route.

## Speculative consequences worth tracking

### 1. Custody breaks become priced exceptions

Insurers, lenders, buyers, and auditors may distinguish harmless lineage gaps from material gaps. A missing optional log may be a schedule note; a missing source snapshot for a core claim may trigger holdback or non-reliance.

### 2. The certificate becomes a safer disclosure than silence

Without a formal break state, actors hide gaps because any admission looks like failure. With a certificate, a broker can say: this segment is broken, but this reliance class remains valid.

### 3. Litigation asks for break histories

Discovery and expert review may ask not only for the evidence chain but for all known breaks, repair attempts, witness nonresponses, and prior reliance decisions.

### 4. Assurance providers compete on break detection

Audit and assurance firms may sell custody-break detection, classification, and remediation services. Their classification grammar becomes an underappreciated quasi-standard.

## Abuse and burden

Break certificates can be laundered into blanket disclaimers. They can also over-penalize smaller actors whose systems are less automated but substantively reliable. A certificate should narrow reliance, not become a magic waiver.

## Falsifiers

The thesis weakens if custody gaps remain informal caveats; if courts and auditors treat broken lineage as binary inadmissibility rather than typed partial reliance; or if proof systems become centralized enough that custody breaks are rare.
