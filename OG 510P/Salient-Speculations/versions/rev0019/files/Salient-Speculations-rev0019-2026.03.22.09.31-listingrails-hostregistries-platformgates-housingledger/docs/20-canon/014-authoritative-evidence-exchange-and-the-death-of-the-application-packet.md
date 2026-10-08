# 014 — Authoritative evidence exchange and the death of the application packet

**Status:** canon

## Thesis

As authoritative-source evidence exchange systems spread, more institutions will stop treating the application packet as a bundle of copies that the applicant must assemble and upload.
The operative action shifts from “submit your documents” to “authenticate, consent, preview, and let the current evidence be retrieved from the source.”

## Why it matters

A surprising amount of administration still depends on brittle packet assembly.
Citizens and firms are asked to discover which records matter, obtain copies, keep them current, upload them into portals, and hope that the receiving body can verify them.
That workflow is slow, forgeable, exclusionary, and expensive.
It also scales badly once cross-border activity, remote service delivery, and agentic software increase the volume of low-trust document handling.

If the higher-trust pattern becomes source-to-source retrieval of current evidence, then many procedures change shape.
The scarce asset is no longer the applicant’s patience in compiling paperwork.
It is the quality, reachability, semantic interoperability, and lawful reusability of authoritative data sources.

This is distinct from threshold credentials or authority credentials.
Those notes ask what a person or firm can present.
This note asks when institutions stop requiring presentation in the first place and instead engineer trusted query-and-reuse of evidence from the authoritative source.

## Mechanism sketch

- Regulation (EU) 2018/1724 already requires a technical system for the cross-border automated exchange of evidence and explicitly frames it as application of the “once-only” principle for procedures in scope.
- The 2025–2026 Single Digital Gateway work programme confirms that the Once-Only Technical System (OOTS) was established in line with the legal deadline and is now the implementation path for cross-border automated evidence exchange.
- The OOTS infrastructure has been live since December 2023. Its official architecture material treats direct delivery from the authentic source, consent, preview, evidence-provider catalogues, evidence mapping, and standardised data models as normal design features rather than experimental aspirations.
- The March 2026 v2.0 Technical Design Documents push the system further toward structured evidence types, fuller regulation coverage, and future-proof exchange features. That means the problem is no longer merely legal permission; it is now an actively maintained interoperability stack.
- The European Business Wallets proposal complements OOTS by giving businesses and public bodies a trusted identification and secure exchange layer for reusing verified data and official attestations across borders. In other words, wallets do not only present proofs; they also help route and reuse them.
- The Commission’s 2026 “EU Inc.” communication makes the next pressure point explicit: Member States should prioritise onboarding procedures and evidence critical to the business lifecycle. That is a sign that authoritative-query infrastructure is moving from abstract capability to triaged operational rollout.
- OECD’s recent work shows that the once-only principle is not just an EU curiosity. Korea already embeds administrative data-sharing into project review, budget approval, and tender preparation, while OECD’s digital public infrastructure work treats effective data sharing as foundational for joined-up services and once-only delivery.

The deeper pattern is that some institutions are moving from **proof collection** to **evidence orchestration**.
The decisive work becomes identifying the right source, matching the right subject, requesting the right evidence with the right scope, and logging the retrieval under lawful consent and reuse rules.

## What this speculation predicts

1. More high-value public and quasi-public workflows will replace document-upload steps with consented retrieval of current evidence from authoritative sources, at first in cross-border and regulated procedures and later in more ordinary domestic ones.
2. The strategic chokepoints will shift toward registries, evidence brokers, record-matching systems, access nodes, semantic repositories, and rules for who may query what for which purpose.
3. Fraud and administrative conflict will move away from forged copies and toward wrongful queries, record-matching failures, stale source data, source outages, broken evidence mappings, and disputes over consent, preview, and logging.
4. Private-sector workflows in banking, insurance, employment, education, and compliance will increasingly imitate once-only public-sector patterns by preferring authoritative retrieval or re-usable official attestations over repeated PDF collection.

## Watchpoints

- more procedures being onboarded to OOTS or similar source-to-source evidence exchange systems
- laws, official guidance, or vendor products explicitly requiring authorities to reuse data already held elsewhere instead of requesting re-submission
- growth of evidence directories, evidence brokers, subject-matching services, or shared data models that make authoritative-source retrieval operationally easier than document upload
- disputes or policy debates about preview, consent, access logging, data minimisation, liability for bad source data, or what happens when the authoritative source is wrong or unavailable
- evidence that institutions continue to prefer applicant-assembled packets because data quality, interoperability, legal trust, or governance remain too weak

## What would weaken this

- once-only systems remaining mostly symbolic, cross-border, or pilot-scale while ordinary procedures continue to rely on manual uploads and caseworker validation
- legal fragmentation, privacy concerns, or registry-quality failures preventing receiving institutions from trusting direct retrieval enough to redesign real workflows
- user, vendor, or agency preference for closed document-collection silos over shared authoritative-query infrastructure

## Source anchors

- [SRC-061](../00-meta/bibliography.md#src-061)
- [SRC-062](../00-meta/bibliography.md#src-062)
- [SRC-063](../00-meta/bibliography.md#src-063)
- [SRC-064](../00-meta/bibliography.md#src-064)
- [SRC-065](../00-meta/bibliography.md#src-065)
- [SRC-066](../00-meta/bibliography.md#src-066)
- [SRC-067](../00-meta/bibliography.md#src-067)
- [SRC-068](../00-meta/bibliography.md#src-068)
- [SRC-069](../00-meta/bibliography.md#src-069)
