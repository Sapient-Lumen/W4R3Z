# Witness governance, incentives, and capture resistance

**Track:** A (Deployable core)


This document specifies how the **witness set** (cosigners / checkpoint notaries / monitors) is governed, funded, rotated, and audited so that it remains **independent, diverse, and hard to capture** over time.

## Threats (governance-level)

1. **Monoculture / capture**: a single stakeholder class (party, vendor, agency, donor) controls a quorum.
2. **Soft capture**: dependence on a shared funder, managed service provider, or shared security team.
3. **Silent non-participation**: witnesses stop cosigning (or selectively cosign) to create delays or split views.
4. **Witness substitution**: a compromised authority quietly swaps the witness list or witness keys.
5. **Collusion with the log**: witnesses see equivocation but do not disclose it.

## Design principles

* **Clients verify policy, not promises**: clients MUST verify that checkpoints are cosigned according to a *published Witness Policy*.
* **Diversity is a requirement**: quorum is invalid unless it satisfies *stakeholder diversity constraints*.
* **Rotation is routine**: rotation is not a crisis action; it is scheduled and auditable.
* **Funding is transparent**: witnesses MUST disclose funding sources and controlling parties.

## Normative requirements

### WIT-1 Witness Charter
Each witness operator MUST publish a signed **Witness Charter** (see schema `schemas/WitnessCharter.json`) that includes:

* legal entity name, jurisdiction, controlling persons
* operational security contact + incident disclosure commitment
* funding sources and relationships that could create conflicts
* the category(ies) it claims (e.g., "civil society", "academic", "party", "court", "vendor")

### WIT-2 Conflicts of interest (COI)
Witness operators MUST publish a signed **COI disclosure** (schema `ConflictOfInterestDisclosure.json`) at least:

* 60 days before election open
* immediately upon any material change

### WIT-3 Admission and removal
Witness admission/removal MUST follow a published **admission policy** modeled after public transparency ecosystems:

* published requirements and review process
* probation / staged rollout
* explicit removal triggers (SLA violations, equivocation, refusal to disclose COI)

See `139-ct-policy-inspired-admission-and-removal.md`.

### WIT-4 Diversity constraints
The Witness Policy MUST define **diversity constraints**, e.g.:

* at least 1 witness from each of *k* stakeholder classes
* no more than *x%* of witnesses funded by the same donor
* no more than *y* witnesses hosted by the same cloud provider / MSP

The federation MUST publish a periodic **Stakeholder Diversity Report** (schema `StakeholderDiversityReport.json`) anchored into checkpoints.

### WIT-5 Term limits and rotation
Witness operators MUST have term limits and a rotation schedule:

* default term: 2–4 years
* staggered rotation so quorum availability remains stable
* emergency rotation procedure for compromise

Rotation MUST be published as a signed `WitnessRotationSchedule.json`.

### WIT-6 Incentive model (minimum viable)
Witnesses SHOULD be funded in ways that minimize capture:

* multi-source funding (public funds + multiple private sources) with caps
* fixed-fee contracts not tied to outcomes
* open procurement, public rate cards

When incentives are used (e.g., decentralized trustee selection), the system SHOULD prefer models where **clients choose trustees/witnesses** and incentives are transparent.

## Operational checks

* quarterly: COI refresh + diversity report
* pre-election: witness key validation drill + compromise response tabletop
* election week: daily availability check + cosignature completeness check

## Outputs

* `WitnessCharter` (one per witness operator)
* `ConflictOfInterestDisclosure` (per witness operator)
* `WitnessRotationSchedule` (per election cycle)
* `StakeholderDiversityReport` (periodic)
* `FundingTransparencyReport` (periodic)