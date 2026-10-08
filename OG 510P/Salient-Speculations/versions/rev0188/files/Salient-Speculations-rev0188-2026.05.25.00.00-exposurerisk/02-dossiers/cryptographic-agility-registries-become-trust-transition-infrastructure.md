---
id: ss-0183-cryptographic-agility-registries
revision_promoted: rev0183
title: Cryptographic-agility registries become trust-transition infrastructure
constellation:
- managed-legibility
- standards-and-conformance
- resilience-and-continuity
status: dossier
maturity: S2-artifact-emerging
confidence: medium-high
time_horizon: near-to-mid
domain:
- cyber / software supply chain / vulnerability governance
- cryptography / trust infrastructure
- standards / interoperability / conformance
bottleneck_type:
- version / support-window compatibility
- admissible evidence
- state freshness
- underwritability
enforcement_surface:
- procurement / framework contract
- audit / attestation / assurance
- operational-resilience supervision
- certification / conformity assessment
artifact_type:
- registry entry
- scorecard
- transition plan
- exception record
lifecycle_stage:
- inventory
- transition
- validate
- rely
- retire
primary_actors:
- vendor
- buyer
- certifier
- security-team
- public-agency
failure_modes:
- stale-state
- algorithm-obsolescence
- hidden-dependency
- unsupported-legacy
- false-migration-claim
adversarial_pressure:
- harvest-now-decrypt-later
- compliance-theater
- exception-laundering
- trust-anchor-capture
distributional_effect:
- small-vendor-migration-burden
- incumbent-compliance-advantage
- public-sector-procurement-pressure
---
# Cryptographic-agility registries become trust-transition infrastructure

## Core claim

Cryptographic transitions are usually described as technical upgrades: replace vulnerable algorithms, rotate keys, update libraries, and move on. That framing underestimates the institutional problem.

The speculative claim is: **cryptographic-agility registries become trust-transition infrastructure**. As post-quantum cryptography, certificate automation, signing-key rotation, hardware-root changes, and protocol deprecations collide with long-lived devices and contracts, the scarce object becomes not the algorithm but the **admissible transition state**: inventoried, planned, tested, dual-stacked, exception-approved, migrated, independently verified, or retired.

NIST finalized the first three post-quantum cryptography standards in 2024 [S1516], and its standardization process continues beyond those first standards [S1517]. CISA has begun moving the problem toward product-category planning [S1518]. NIST's NCCoE materials frame PQC migration as a staged journey, not a single switch [S1530]. The archive should therefore stop treating cryptography as a background security primitive and start treating cryptographic transition status as a governed proof object.

## Why this belongs in the archive

The archive already has dossiers on supported-version windows, trust-anchor sunset dates, regression-retirement markers, conformance alerts, backport proof, and security-feed uptime. Cryptographic agility is the same institutional pattern at a deeper layer.

A buyer will not only ask, “Do you use PQC?” It will ask:

- Which products, services, certificates, protocols, firmware images, APIs, logs, backups, archives, signing keys, and customer integrations are in scope?
- Which cryptographic uses are confidentiality-sensitive, signature-sensitive, availability-sensitive, or audit-sensitive?
- Which systems are dual-running classical and post-quantum algorithms?
- Which dependencies cannot migrate yet?
- Which exceptions are time-limited, compensating-controlled, or accepted only for certain data classes?
- Which signed records must remain verifiable after old algorithms are distrusted?

That creates a registry problem. The registry does not merely name algorithms. It records transition state, exception authority, evidence freshness, and the future date on which old proof stops being admissible.

## Speculative consequences worth tracking

### 1. Crypto inventory becomes procurement evidence

A software bill of materials tells a buyer what components exist. A cryptographic bill of materials and agility registry tell a buyer which algorithms, libraries, keys, protocols, certificates, hardware modules, and trust anchors determine whether those components remain acceptable over time.

### 2. Algorithm sunset dates become contract dates

Procurement language will start naming not just current compliance but migration clocks: no new SHA-1-like dependencies, no unplanned RSA-only endpoints after a certain date, no unsupported signing chains, or mandatory PQC readiness for data with long confidentiality life.

### 3. Dual-stack states become reliance labels

During transition, systems may be classical-only, hybrid, PQC-capable, PQC-preferred, PQC-required, exception-approved, or legacy-isolated. Those states will travel into audit reports, customer questionnaires, insurer reviews, and regulated-entity supervisory files.

### 4. Long-lived signatures create archive-afterlife problems

A passport, certificate, log, contract, calibration record, model evaluation, or incident report signed under an older algorithm may need to remain evidentiary for years. Crypto migration therefore creates preservation artifacts: timestamp renewal, evidence re-sealing, signature wrapping, hash-chain migration, and archival validation profiles.

### 5. Exception ledgers become a liability surface

Every migration has exceptions. The question becomes whether exceptions are named, scoped, reviewed, compensated, and expired. Unnamed exceptions will look like hidden risk; overbroad exceptions will look like compliance laundering.

### 6. Trust-anchor rollover becomes an operational outage risk

If root certificates, firmware signing keys, wallet trust lists, or product-passport issuer keys rotate badly, verification fails. Crypto-agility governance therefore belongs with resilience, not only with security.

## Likely artifact shape

The mature artifact is a **cryptographic-agility registry**. It contains:

- cryptographic asset inventory;
- algorithm and parameter profile;
- key, certificate, trust-anchor, and signing-chain inventory;
- protocol and API exposure map;
- data-retention sensitivity and confidentiality half-life;
- PQC readiness state;
- dual-stack and fallback state;
- third-party dependency status;
- exception owner and expiry;
- compensating controls;
- archival-verification plan;
- test evidence and conformance reports;
- customer-facing transition commitment;
- sunset, renewal, and recertification calendar.

## Who pays / who saves / who captures

Vendors pay to inventory and migrate. Buyers, regulated entities, insurers, and public agencies save by turning opaque technical exposure into a reviewable state object. Security-rating firms, certifiers, cloud providers, hardware security module vendors, and compliance brokers capture value by translating messy crypto posture into procurement-ready profiles.

Small vendors may be disadvantaged if cryptographic evidence requirements become complex before public tooling matures. A public-good version of this market would provide low-cost inventory, test, and profile-generation tools rather than force every supplier into bespoke questionnaires.

## How this gets abused

- A supplier claims “PQC-ready” because one endpoint supports a standard while backups, archives, firmware, and signing chains remain classical-only.
- An exception ledger hides an entire legacy estate under vague “compatibility” language.
- A vendor uses hybrid mode as a permanent stall rather than a transition state.
- A buyer demands excessive disclosure of security architecture under the cover of PQC diligence.
- A certifier sells a broad readiness label without checking dependency-level evidence.
- An attacker targets rollover windows, downgrade paths, and forgotten validation chains.

## Near misses

A cryptographic standard is not the thesis. The thesis is the governance of transition state.

A crypto inventory is not enough if it does not tie state to deadlines, reliance permissions, exceptions, and archival validity.

A vendor blog post promising PQC migration is not infrastructure. The artifact hardens only when buyers, auditors, insurers, or regulators rely on structured transition evidence.

## Falsifiers

The thesis weakens if PQC migration remains mostly invisible to buyers; if public tooling makes transition trivial; if regulators avoid asking for cryptographic state evidence; if the market accepts one-time certifications rather than maintained transition registries; or if cryptographic agility is absorbed cleanly into ordinary patch management.

## Signals to watch

- procurement clauses requiring cryptographic inventories or PQC transition plans;
- public-sector buyer guides naming product-category migration status;
- insurer questionnaires about long-confidentiality data;
- audit reports with algorithm sunset and exception tables;
- certificate lifecycle failures during algorithm or trust-anchor rollover;
- conformance profiles for hybrid or PQC-enabled protocols;
- archival validation services for old signatures and evidence bundles.
