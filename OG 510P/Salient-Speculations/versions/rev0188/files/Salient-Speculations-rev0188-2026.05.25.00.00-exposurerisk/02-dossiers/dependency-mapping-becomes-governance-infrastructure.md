---
id: ss-0183-dependency-mapping-becomes-governance-infrastructure
revision_promoted: pre-rev0180
title: Dependency Mapping Becomes Governance Infrastructure
constellation:
- place-and-climate
- standards-and-conformance
- model-governance
- managed-legibility
- market-and-state-capacity
status: dossier
maturity: S3-enforcement-surface
confidence: medium
time_horizon: mixed
domain:
- climate / retreat / habitability
- land / parcel / place-proof
- standards / interoperability / conformance
- compute / AI / data centers
- simulation / forecasting / counterfactual capacity
- identity / credentials / delegated authority
- procurement / purchasing / offtake
- insurance / risk transfer / underwriting
bottleneck_type:
- conformance capacity
- interoperability translation
- version / support-window compatibility
- model credibility
- admissible evidence
- state freshness
- source-of-truth precedence
- appealability / redress
- underwritability
- small-actor evidence capacity
enforcement_surface:
- permit / license
- title / conveyancing / property transfer
- underwriting / insurance renewal
- certification / conformity assessment
- procurement / framework contract
- audit / attestation / assurance
- platform eligibility / ranking
- lending covenant / credit agreement
artifact_type:
- registry entry
- notice
- state label
lifecycle_stage:
- publish
- rely
- dispute
- correct
primary_actors:
- municipality
- insurer
- property-owner
- standards-body
- certifier
- buyer
- model-provider
- auditor
- broker
- source-vendor
- supplier
failure_modes:
- stale-state
- nonpropagation
- false-match
adversarial_pressure:
- strategic-delay
- overbroad-disclosure
distributional_effect:
- small-supplier-burden
- incumbent-compliance-advantage
migration_status: inferred-rev0183-minimal
migration_note: Metadata was inferred from title, source references, and local keyword context; review before treating as authoritative.
---
# Dossier: Dependency Mapping Becomes Governance Infrastructure

## Core claim

The important shift is not just that systems are interconnected, supply chains are complex, or outages reveal hidden fragility. It is that **more institutions are being required to maintain inspectable representations of the dependencies that keep critical services running**.

The stronger version of the thesis is that **organizations increasingly stop being judged only by whether they have continuity plans or secure products and start being judged by whether they can enumerate, classify, update, and submit the people, processes, software components, suppliers, facilities, and subcontractors on which those services depend**. In that world, the decisive question is no longer only *what is your critical service?* It becomes *show the dependency graph, show the third parties and fourth parties, show the components, show the substitutability assumptions, and show which dependencies are common enough to become systemic.*

That sounds administrative until the layer thickens. Once dependency mapping becomes infrastructural, registers of ICT contracts, software bills of materials, cross-sector interdependency diagrams, critical-operations inventories, supplier registers, and sub-outsourcing disclosures begin to shape supervision, concentration-risk analysis, procurement, incident response, and the politics of who is allowed to remain opaque.

## Why this belongs in the archive

The archive already has dossiers on hidden chokepoints, governed objects, proof of place, and conformity assessment. The missing layer was **dependency legibility**: the operational fact that more regulators and operators now want formal, reusable answers to *what exactly does this service depend on, how concentrated is that dependency, and who else shares it?*

Europe is making that demand explicit in finance. ESMA says the European Supervisory Authorities expect to collect DORA registers of information from competent authorities, while the EBA says that since DORA became applicable on 17 January 2025, all financial entities in scope need a comprehensive register of their contractual arrangements with ICT third-party providers at entity, sub-consolidated, and consolidated levels [S604][S605]. The EBA also says these registers serve three purposes: entities use them to monitor ICT third-party risk, competent authorities use them to supervise third-party risk management, and the ESAs use them to designate critical ICT third-party providers [S605]. The subsequent 2025 designation of CTPPs then made the logic fully visible: the ESAs used data collected from the registers of information maintained by financial entities to identify and designate providers whose disruption could become systemically important [S606].

The same pattern is now appearing in cyber policy. The European Commission’s 2026 ICT Supply Chain Security Toolbox says it provides a common approach to identify, assess, and mitigate cybersecurity risks of ICT supply chains and explicitly recommends measures for overcoming dependencies on high-risk suppliers [S607]. CISA and its international partners now frame the software bill of materials in almost the same infrastructural terms: their 2025 shared-vision guidance says an SBOM is a formal record detailing the components and supply-chain relationships used in building software, and treats SBOMs as a core way to illuminate software dependency structure [S608]. The point is not just better documentation. It is that **dependency disclosure is becoming part of how software trust is administered**.

Financial resilience rules are moving in the same direction but at the service layer. The Bank of England says firms and FMIs must have robust plans to deliver important business services through disruptions including third-party supplier failure [S609]. Its 2026 supervisory statement for central counterparties makes the requirement more concrete: firms should identify important business services and document the people, processes, technology, facilities, and information required to deliver them; this process is called mapping; and the Bank expects firms to understand how third parties, supply chains, and sub-outsourcing arrangements support those services [S610]. That is a major threshold crossing. A regulator is not merely asking for assurance that resilience exists; it is asking for a structured account of the dependency topology behind the service.

Australia is making a closely related move in prudential regulation. APRA’s CPS 230 requires regulated entities to identify and maintain a register of material service providers, manage the risks associated with those providers, account for fourth parties relied on by providers, and submit the register to APRA annually [S611]. APRA’s accompanying operational-risk page then turns the requirement into an operational artefact by publishing a preferred material-service-provider register template and a submission deadline [S612]. Again, the telling feature is that the dependency register itself becomes a governed object.

Energy-security planning shows the cross-sector version of the same logic. DOE’s State Energy Security Plan resources now include dedicated cross-sector interdependency diagrams and energy supply-chain diagrams for state planning [S613]. That matters because it shows dependency mapping moving beyond individual firms or software products into state-level preparedness and infrastructure governance: not just *what assets exist*, but *which other systems they depend on and which failures will cascade first*.

Taken together, these sources suggest a real shift: **societies are beginning to discover that invisible dependencies are no longer acceptable background complexity. They are becoming things that must be named, standardised, submitted, and supervised.**

## Speculative consequences worth tracking

### 1. Dependency inventories become examination artefacts

In more sectors, regulators and major buyers may ask not only whether a service is secure or resilient, but whether its dependency register is complete, current, and comparable across firms.

### 2. Concentration risk becomes computable

Once many entities submit structured dependency data, shared dependence on the same cloud, telecom, software library, logistics provider, or contractor becomes easier to aggregate and harder to dismiss as anecdotal.

### 3. Fourth-party opacity becomes politically unstable

Organizations may find that it is no longer enough to know their vendors; they will be pushed to know which vendors their vendors rely on when those chains support critical operations.

### 4. Substitutability becomes a first-class governance variable

The more dependencies are enumerated, the more institutions will be asked which ones are replaceable, within what time, at what cost, and under what legal or technical constraints.

### 5. Procurement starts buying maps, not just services

Large buyers may increasingly require SBOMs, supplier disclosures, dependency attestations, and exit-readiness evidence as part of ordinary procurement rather than exceptional due diligence.

### 6. Incident response shifts from local debugging to graph operations

When outages happen, the key question may increasingly be not only which node failed, but which registered dependency edges explain why apparently separate firms, regions, or services failed together.

### 7. Architectural choices become reportability choices

Designers may begin preferring components, service boundaries, identifiers, and vendor arrangements that are easier to classify, monitor, and disclose under multiple regimes.

### 8. Dependency custodians become hidden power centres

The maintainers of taxonomies, identifiers, data models, registers, and aggregation systems may become strategically important because they decide which dependency structures are visible enough to govern.

## What could falsify or weaken the thesis

- Registers and maps remain stale compliance paperwork that is rarely used for actual supervision, procurement, or incident response.
- Confidentiality, burden, or legal-fragmentation concerns prevent dependency data from becoming comparable across firms or jurisdictions.
- Most important sectors stop at top-level vendor disclosure and never meaningfully reach components, sub-outsourcing chains, or cross-sector interdependencies.
- Major incidents continue to be analysed mainly through local root-cause narratives rather than through shared dependency data.

## What to watch next

- Whether more regulators publish templates, taxonomies, LEI requirements, or data dictionaries for dependency registers and service-resource maps.
- Whether SBOMs, supplier maps, or dependency attestations become routine procurement requirements outside high-security niches.
- Whether authorities begin publishing aggregate concentration findings based on submitted dependency data rather than only after crises.
- Whether fourth-party disclosure and exit-readiness planning become standard clauses in material service-provider contracts.
- Whether dependency-data quality starts appearing in enforcement actions, supervisory letters, or post-incident remediation programs.
