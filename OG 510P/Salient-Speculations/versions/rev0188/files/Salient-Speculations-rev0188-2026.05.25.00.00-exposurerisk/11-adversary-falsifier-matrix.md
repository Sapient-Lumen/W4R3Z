# Adversary and Falsifier Matrix

rev0182 adds a stress layer to the datacube. The archive now has many proof objects, status labels, registries, notices, validation reports, wallets, passports, reliance graphs, and appeal states. That is useful, but it creates a bias: a well-described proof object can look like infrastructure before anyone has asked how it fails.

This file is the counterweight. A dossier should not be considered mature merely because it names a plausible artifact. It should survive adversarial, burden, privacy, and falsifier tests.

## Core rule

> A proof object is not infrastructure until the archive can say who attacks it, who is burdened by it, who can appeal it, who pays for its repair, and what would make the thesis false.

This revision treats the following not as side notes but as first-class cube variables:

- forgery;
- laundering;
- stale-proof reuse;
- subject mismatch;
- issuer compromise;
- resolver capture;
- graph poisoning;
- nonresponse leverage;
- over-disclosure pressure;
- exclusion by evidence burden;
- informal-market evasion;
- local-trust override;
- appeal exhaustion;
- false confidence from machine-readable form.

## Stress matrix

| Artifact family | Strong version of the thesis | Main adversarial move | Main burden move | Falsifier |
|---|---|---|---|---|
| Product passports | Product biography gates market access, repair, resale, recall, and recycling | Resolver capture, subject mismatch, forged passport, stale passport, issuer succession failure | Small suppliers cannot maintain required data or service-provider relationships | Passports remain mostly informational and are not used by customs, procurement, recall, resale, or repair workflows |
| Reliance packets | Packet state controls transaction reliance, holds, appeal stays, and correction afterlife | Strategic appeals, forged stay labels, stale non-reliance states, witness nonresponse | Smaller sellers cannot fund replay, appeals, or escrow | Buyers keep accepting bespoke PDFs and warranties without structured status dependence |
| Public conformance registries | Visible listing status becomes market ordering | Listing manipulation, scope gaming, stale listing, registry incompleteness, trusted-list capture | Small vendors fail because listing maintenance cost exceeds value | Buyers ignore registries or use them only after independent review |
| Verifiable credentials | Attribute proofs become portable authorization objects | Issuer compromise, verifier overreach, linkability, wallet lock-in, coerced disclosure | People without stable credentials are excluded from routine transactions | Credentials remain sector-specific and do not travel across procurement, service access, and compliance |
| Model documentation packets | AI assurance travels as structured documentation and redacted evidence | Redaction abuse, benchmark laundering, synthetic audit trails, stale model cards, downstream-use mismatch | Smaller model providers cannot afford repeated documentation, safety evaluation, and redaction review | Procurement accepts narrative policies and never requires structured machine-readable assurance |
| Incident reports | Materiality, routing, and clock-start rules become operational infrastructure | Under-reporting, delayed materiality determination, misrouted third-party evidence, correction suppression | Smaller firms lack reporting counsel and evidence pipelines | Regulators accept coarse narrative reporting without cross-recipient status reconciliation |
| Grid-connection records | Queue position and readiness state become financeable project assets | Queue squatting, readiness spoofing, interconnection-cost gaming | Smaller projects cannot post deposits, studies, and site-control evidence | Queue reforms eliminate speculative positions and reduce queue value sharply |
| Repair records | Repairability becomes enforceable evidence | False repair events, firmware-lock concealment, parts-availability laundering, resale history suppression | Independent repairers lack access to diagnostic data or event-writing rights | Repair rights remain consumer-law claims but do not enter warranties, resale, insurance, or passports |

## Attack vocabulary

### Forgery

A false object claims to be a real proof: a fake due-diligence statement, fake product passport, fake stay label, fake validation report, fake incident notice, fake repair event, fake credential, or fake provenance bundle.

Stress question: **What prevents the forged object from being accepted by a low-friction downstream workflow?**

### Laundering

A weak or compromised proof becomes legitimate by passing through a trusted intermediary, registry, marketplace, broker, certifier, wallet, customs process, or procurement intake.

Stress question: **Which actor can clean bad evidence by repackaging it?**

### Stale-proof reuse

A proof was once true but is reused after the underlying state changed: expired validation report, superseded model card, withdrawn passport, old recall status, obsolete VEX claim, stale source snapshot, pre-appeal score.

Stress question: **Where is freshness checked, and who is liable if the stale proof is still accepted?**

### Subject mismatch

The proof is real but attached to the wrong subject: wrong product batch, wrong model version, wrong supplier entity, wrong parcel, wrong component lineage, wrong person, wrong facility, wrong dependency.

Stress question: **What identity object binds the proof to the thing that downstream systems actually rely on?**

### Issuer compromise

The issuing institution or key is compromised, captured, insolvent, defunct, coerced, merged, or no longer recognized.

Stress question: **How do old proofs survive issuer failure without becoming unverifiable or over-trusted?**

### Resolver capture

A resolver, pointer service, lookup API, URL namespace, QR-code route, wallet trust list, product-passport service provider, or registry endpoint controls what the verifier sees.

Stress question: **Who governs the pointer layer between a physical thing and its official state?**

### Graph poisoning

An attacker poisons the relation graph that determines identity, dependency, eligibility, package lineage, remediated state, or relevance.

Stress question: **Can the system distinguish a bad node from a bad edge?**

### Nonresponse leverage

A party refuses, delays, or strategically times a response so another actor cannot prove, correct, appeal, close, report, or rely.

Stress question: **What happens when the witness required for proof is silent?**

### Over-disclosure pressure

A verifier demands more data than the purpose requires, and the weaker party discloses because refusal looks like noncompliance.

Stress question: **Is there a public proof profile that defines sufficient proof and forbidden over-collection?**

### Exclusion by evidence burden

The proof requirement is substantively defensible but operationally impossible for small suppliers, informal workers, low-connectivity regions, older people, or firms outside rich compliance ecosystems.

Stress question: **Who funds evidence capacity for actors who are compliant but not proof-ready?**

## Dossier scoring rubric

Use this as an editorial grade, not a mathematical score.

| Grade | Meaning |
|---|---|
| A | Names a state transition, artifact, relying actor, enforcement surface, abuse path, burden path, appeal path, and falsifier. |
| B | Names the artifact and enforcement surface, with at least one credible abuse or burden path. |
| C | Names a plausible artifact but relies on generalized institutional momentum. |
| D | Mostly a trend label; no state transition, enforcement surface, or adversarial story. |

## Immediate application

rev0182 uses this matrix to add or strengthen dossiers on:

- public proof-profile registries;
- graph poisoning;
- resolver capture;
- informal-market refuge;
- redaction-boundary ledgers;
- recall-state propagation.

These are not meant to sprawl the archive. They are stress tools. Each new dossier is a way to pressure-test existing proof-object theses.

## Editorial consequence

Future promotions should slow unless they answer at least four of the following questions:

1. What state changes?
2. Which artifact carries the state?
3. Who relies on it?
4. What makes reliance enforceable?
5. How is it forged, laundered, poisoned, or made stale?
6. Who cannot comply even when substantively eligible?
7. What is the appeal or repair path?
8. What would prove that the thesis is not hardening?


## rev0183 adversary additions

### Algorithm-obsolescence laundering

A vendor claims transition readiness while legacy cryptography remains in archives, firmware, backups, signing chains, or third-party integrations.

Stress question: **Does the transition proof include all cryptographic uses that downstream parties rely on?**

### Authority spoofing

A person, firm, bot, tool endpoint, or agent falsely claims delegated authority to act for another party.

Stress question: **Can the relying party verify scope, expiry, revocation, and replayable action history?**

### Provenance stripping

A media or document pipeline removes provenance metadata, intentionally or accidentally, creating ambiguous absence.

Stress question: **Can the system distinguish legacy absence, privacy-preserving absence, technical stripping, and malicious laundering?**

### Assessor-capacity capture

A dominant actor captures scarce review capacity, assessor attention, or queue priority in a way that delays competitors or smaller entrants.

Stress question: **Is queue position a legitimate readiness signal or a strategic exclusion device?**

### Data-space access laundering

A data user obtains access through a trusted intermediary or role profile and then uses the data outside the permitted purpose.

Stress question: **Do use-policy receipts, audit logs, and revocation paths survive cross-space transfer?**

## rev0188 adversary patch: exposure gaming

New adversary patterns after the exposure refactor:

- threshold gaming below deductibles or self-insured retentions;
- late-notice laundering;
- exclusion-state ambiguity used as settlement pressure;
- generic certificate evidence masking nonresponsive protection;
- vendor settlement waiving subrogation rights;
- reserve-release optimism before tail closure;
- indemnity maps that assign responsibility to insolvent or capped entities.
