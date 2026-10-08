# 276. Contingency planning and continuity of operations as evidence surfaces

**Track:** Shared

Elections must keep operating during disruptions (weather, facility issues, staffing shocks, cyber incidents, vendor outages, civil unrest).
“Having a plan” is not enough: plans must be **drillable**, **bounded**, and **publishable** without leaking sensitive details.

This doc defines **minimal publishable artifacts** that prove preparedness and continuity posture
*without* publishing facility layouts, rosters, detailed network diagrams, or step-by-step adversarial playbooks.

## Why this exists

Two failure modes recur:

1. **Opaque continuity:** operators have plans but outsiders cannot tell whether they exist, are current, or were exercised.
2. **Dangerous disclosure:** trying to be “transparent” results in publishing operational targeting details.

We want the narrow middle: publish **digests + commitments + summaries** that are independently checkable and can be cross-linked
to incident comms (`247`, `259`), drills (`258`), change control (`256`), and proof packaging (`265`).

## The deliverables (minimal)

### 276.1 Continuity Posture Statement (CPS)

A public statement that answers, at a high level:

- which disruption classes are planned for (weather, facility closure, cyber, supply-chain, staffing),
- what “degraded mode” means in this jurisdiction (see `276.3`),
- where official updates will appear (PublicNotice feeds: `200`, official channel directory: `203`),
- how to verify that plans are current (hash commitments + change history; `261`, `265`).

**Publish:** CPS as a small markdown/pdf *and* a hash commitment (CommitLog Entry; `261`).

### 276.2 Continuity Plan Digest (CPD)

A bounded, publishable summary of the internal continuity plan.

**CPD should include:**
- `cpd_id`, `election_id`, `jurisdiction_id` (see `262`)
- scope: which systems/processes are covered (registration, EPBs, VBM processing, tabulation reporting, public comms)
- **RTO/RPO classes** (targets, not step-by-step procedures)
- dependency overview (see `276.4`)
- **exercise history pointers**: link to exercise AAR digests (`258`)
- **change linkage**: link to Change Control Packets (`256`) and a CommitLog entry (`261`)

**Do not publish:** internal contact lists, vendor escalation trees with phone numbers, facility maps, detailed recovery runbooks.

### 276.3 Degraded Mode Register (DMR)

A small registry of what the jurisdiction treats as acceptable “degraded” operations modes.

Examples (illustrative, not prescriptive):
- “EPB offline mode with reconciliation”
- “VBM intake continues, verification pauses pending staffing”
- “ENR updates paused; only PublicNotice updates until restoration”

**DMR should include:**
- `mode_id`, description, triggers (high-level), and **verifier-visible outputs**
- which evidence surfaces continue to publish (e.g., queue/outage capsules, ENR snapshot packs, corrections logs)
- explicit **stop conditions** (“do not publish location-targeting details”, “no voter-PII exposure”)

### 276.4 Dependency Inventory Digest (DID)

A publishable digest of critical dependencies, at the level needed to explain resilience *without enabling targeting*.

**DID should include:**
- dependency categories (hosting/CDN/DNS/email/telephony/logistics/vendor support)
- single-point-of-failure flags (yes/no, without topology)
- alternates by category (yes/no, without naming vendors if that increases targeting risk)
- last review date and hash commitment (`261`, `265`)

### 276.5 Continuity Incident Capsule (CIC)

When disruption occurs, publish a bounded capsule that composes with incident comms docs:

- references the CPS/CPD/DMR by digest,
- states current mode: `normal | degraded:<mode_id> | suspended:<process>`
- “known / unknown / next update time”
- verification pointers (where the authoritative digests will appear; `200`, `203`, `204`, `205`)
- link to the incident reporting surfaces (`259`) when applicable

CIC is a *PublicNotice-shaped* artifact; treat it as comms-as-security (`247`).

## Stop conditions (hard)

Do not publish anything that meaningfully increases operational targeting risk, including:
- detailed physical security procedures, camera placements, door schedules
- vendor escalation phone trees / personal contacts
- detailed network diagrams, admin URLs, firewall rules
- polling-place–level outage details if it enables intimidation

If a request pushes toward these, route through the PRR/access bounds posture (`253`) and publish only a refusal rationale + safe summaries.

## Composition map (how it fits the rest of the stack)

- **Preparedness:** CPD + DMR + DID (commit via `261`, package via `265`)
- **Exercises:** link to TTX/drill artifacts (`258`)
- **During an incident:** CIC + incident disclosure surfaces (`259`) + rumor-control pack if needed (`268`)
- **Results integrity:** if ENR is affected, keep the non-finality banner + corrections log discipline (`252`)
- **Recovery / drift:** record changes as Change Control Packets and Drift Ledgers (`256`)

## Primary external anchors (cite-first)

- EAC Contingency Planning Quick Start Guide (PDF): xref: eac_quickstartguides_contingency_planning_eac_quick_start_guide_508
- EAC Contingency Planning resource page: xref: eac_officials_contingency_planning
- EAC EMG — Contingency Planning and Change Management (PDF chapter): xref: eac_6_chapter_11_contingency_planning_and_change_management
- NIST SP 800-34 Rev. 1 — Contingency Planning Guide (PDF): xref: nist_nistpubs_legacy_sp_nistspecialpublication800_34r1
- CISA Tabletop Exercise Packages (CTEP): xref: cisa_ctep_packages_html
- Election Security CTEPs (resource page): xref: cisa_security_cisa_tabletop_exercise_packages_cteps
