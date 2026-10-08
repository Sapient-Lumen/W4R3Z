---
id: ss-0181-repair-right-evidence
revision_promoted: rev0181
title: Repair-right evidence becomes consumer infrastructure
constellation:
- maintenance-and-repair
- product-biography
- managed-legibility
status: dossier
maturity: S2-artifact-emerging
confidence: medium
time_horizon: near
domain:
- product identity / passports / traceability
- standards / interoperability / conformance
- civic services / casework / appeals
bottleneck_type:
- admissible evidence
- state freshness
- correction throughput
- selective disclosure / minimization
- appealability / redress
enforcement_surface:
- consumer disclosure
- statute / regulation
- certification / conformity assessment
- platform eligibility / ranking
artifact_type:
- repair record
- notice
- certificate / attestation
- resolver / pointer
- appeal record
lifecycle_stage:
- publish
- route
- rely
- dispute
- correct
- archive
primary_actors:
- consumer
- independent repairer
- manufacturer
- marketplace
- regulator
failure_modes:
- false-refusal
- stale-state
- warranty-chill
- unverifiable-repair
- procedural-debt
refactor_cluster:
- remedy-lifecycle
- exposure-liability
remedy_role: repair evidence remedy
remedy_stage:
- request
- investigate
- correct
consolidation_status: standalone-mechanism
state_family:
- remedy
- exposure
exposure_role: manufacturer and consumer-insurer
exposure_stage:
- condition
- pay
- close
state_terms:
- condition-precedent-pending
- warranty-breached
- claim-closed
---
# Repair-right evidence becomes consumer infrastructure

## Core claim

Right-to-repair policy will not become real merely because consumers are legally entitled to repair. It becomes real when repairers, marketplaces, warranty administrators, insurers, recyclers, refurbishers, and public authorities can exchange reliable evidence about diagnostics, parts, tools, refusals, completed repairs, safety-relevant modifications, and remaining product status.

The speculative claim is: **repair-right evidence becomes consumer infrastructure**. Repairability moves from a product attribute to an operational evidence layer: proof that parts were available, proof that diagnostics were provided, proof that a manufacturer refused or delayed, proof that a repairer used an approved or equivalent part, proof that the repaired product remains safe, and proof that a warranty denial was or was not justified.

The EU repair directive is a near-term signal. The European Commission says the directive was adopted on 13 June 2024, entered into force on 30 July 2024, and must be transposed and applied by Member States from 31 July 2026 [S1494]. The Digital Product Passport consultation shows a parallel product-biography infrastructure for product data, instructions, and conformity information [S1484]. The likely convergence is repair evidence attached to product identity.

## Why this belongs in the archive

The archive has product passports, product biographies, data-access rights, source-object identity, and correction afterlife. Repair is where those ideas meet households.

A consumer right without evidence is hard to exercise. A manufacturer can say the part was unavailable, the repair was unsafe, the product was tampered with, the warranty is void, or the repairer lacked proper tooling. A repairer can say the manufacturer withheld diagnostic access or refused parts. A marketplace can downgrade refurbished goods unless it trusts the repair history. An insurer can price devices differently if repairs are unverifiable. Evidence becomes the operational path between right and remedy.

## Speculative consequences worth tracking

### 1. Repair refusal reason codes become regulated objects

A refusal to repair, delay parts, deny diagnostics, or void warranty will need a code. The code determines whether a consumer can complain, whether a repairer can appeal, and whether regulators can see patterns.

### 2. Independent repairer credentials become selective proofs

Consumers and marketplaces may need to know that a repairer is competent for a class of product without seeing all of the repairer's commercial data. That creates credential and proof-profile infrastructure.

### 3. Product passports gain repair-event appendices

A product's passport or resolver may point to repair events, parts replacement, safety checks, firmware state, battery health, calibration, and end-of-life handling. The repair history becomes part of resale value.

### 4. Warranty disputes become evidence disputes

The key question will often be whether a repair caused a failure, whether the manufacturer can prove misuse, or whether refusal was lawful. Repair logs and diagnostic access receipts become consumer claims evidence.

### 5. Repair-data minimization becomes contested

Manufacturers will want detailed diagnostic telemetry. Consumers and independent repairers will resist overbroad disclosure. Good repair evidence will prove repair-relevant facts without turning every repaired object into a surveillance endpoint.

### 6. Secondary markets become evidence-sensitive

Refurbished goods, used EV batteries, phones, appliances, medical devices, farm equipment, and industrial components may be ranked by repair-history quality, not only cosmetic condition.

## Likely artifact shape

The mature artifact is a **repair evidence record** attached to product identity and exportable to consumers, repairers, manufacturers, marketplaces, insurers, recyclers, and regulators. It may include:

- product identifier and model scope;
- repairer credential or role proof;
- diagnostic-access request and response receipt;
- parts request and fulfillment record;
- refusal / delay / nonavailability reason code;
- repair event timestamp and component class;
- safety or calibration confirmation;
- firmware or software state if relevant;
- warranty-preservation statement;
- consumer-consent and disclosure scope;
- dispute / appeal / complaint record;
- resale disclosure profile;
- end-of-life or refurbisher handoff.

## Who pays / who saves / who captures

Consumers save if repair evidence prevents warranty chill and supports resale. Independent repairers save if credentials and event records travel across products and marketplaces. Manufacturers may pay or be forced to provide repair-data endpoints, but can also capture value if they control passport resolvers. Marketplaces capture value by ranking trusted refurbished goods.

The policy risk is manufacturer-controlled evidence. If the only trusted repair record is inside a proprietary manufacturer system, right-to-repair becomes a permissioned repair market.

## How this gets abused

- Manufacturers use safety evidence requirements to exclude independent repairers.
- Repairers falsify records to support resale.
- Marketplaces demand excessive repair telemetry and penalize privacy-preserving records.
- Warranty administrators deny claims because a repair event exists, even when unrelated.
- Counterfeit parts are laundered through weak repair attestations.
- Consumers lose control over product histories that reveal household behavior.

## Near misses

A receipt is not the thesis. The thesis begins when the repair record is accepted by other institutions as evidence of right, compliance, safety, warranty status, or resale quality.

A product manual is not the thesis. The thesis is the operational record of access, repair, refusal, dispute, and afterlife.

A manufacturer app history is not the thesis if the consumer cannot export or contest it.

## What could falsify or weaken the thesis

- Right-to-repair obligations remain narrow and mostly symbolic.
- Consumers do not use complaint or evidence mechanisms enough to justify infrastructure.
- Marketplaces accept informal repair histories.
- Manufacturers successfully keep repair evidence inside closed ecosystems.
- Low product prices make repair economically unattractive outside a few categories.

## Research queue

- Which product category first requires interoperable repair records: batteries, appliances, phones, vehicles, medical devices, or farm equipment?
- Do independent repairer credentials become wallet-style credentials?
- Do product passports include repair appendices or merely static repairability information?
- Do warranty denials create the first large corpus of repair-evidence disputes?
- Does repair evidence become a resale ranking input before it becomes a regulatory input?
