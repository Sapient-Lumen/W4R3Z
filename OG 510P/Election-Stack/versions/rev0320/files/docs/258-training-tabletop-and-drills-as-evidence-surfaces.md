# 258 — Training, tabletop exercises, and drills as evidence surfaces

**Track:** Shared (operations / resilience)

We treat **training and exercises** as *integrity controls* because they reduce response latency, prevent improvisation failures, and make public communication more consistent under stress. The goal is **publishable, privacy-first evidence** that preparedness work happened — without publishing sensitive details, target lists, or operational playbooks.

## Scope and non-claims
This doc defines **minimal publishable artifacts** for:
- training (roles + responsibilities),
- tabletop exercises (TTX),
- functional drills (communications / logistics / contingency operations).

It does **not** define attack playbooks, exploit steps, or “how to disrupt elections.”

## External anchors (cite-first)
- **CISA Election Security CTEPs** (customizable tabletop packages for election stakeholders). https://www.cisa.gov/resources-tools/resources/election-security-cisa-tabletop-exercise-packages-cteps
- **CISA Tabletop Exercise Packages (CTEP)** overview (general). https://www.cisa.gov/resources-tools/services/cisa-tabletop-exercise-packages
- **EAC Contingency planning** overview (why planning/exercising matters for election operations). https://www.eac.gov/election-officials/contingency-planning
- **NIST SP 800-61r3** (incident response recommendations; supersedes 800-61r2). https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r3.pdf
- Optional: **NASS TTX issue briefing** (exercise design basics; includes mis/disinfo/physical). https://www.nass.org/sites/default/files/Cybersecurity/TTX_Issue_Briefing_9.8.20.pdf

## Minimal publishable artifacts (MPA)
All MPAs should be **hashes-first** and **PII-minimized**. Prefer role labels (e.g., “PIO”, “County EMS Admin”, “Legal Counsel”) over names.

### MPA-1: Exercise Charter (EXCH)
Publishable summary of:
- exercise type (training / TTX / drill),
- objectives (3–7 bullets),
- participating org *types* (not named individuals),
- date window (day-level),
- constraints: “no live systems”, “no voter data”, “discussion-based”, etc.

### MPA-2: Scenario Abstract (SCAB)
A **high-level** scenario description that is safe to publish:
- category tags (weather, physical disruption, cyber incident, rumor-control, supply-chain, power/network outage),
- assumed constraints (e.g., “public rumors begin at T0”, “primary website unreachable for N hours”),
- *no* sensitive facility details, staffing schedules, precise network diagrams, or response thresholds.

### MPA-3: Roles & responsibilities card (RRC)
One page mapping:
- who decides (authority lines),
- who communicates publicly,
- who touches systems vs who observes,
- how approvals and sign-offs happen.

### MPA-4: Decision and communications log (DCL)
Append-only log of:
- decision points (what decision, by what authority role, at what time),
- public messaging decisions (what was said and where, with link to `PublicNotice` / rumor-control surface if used),
- corrections (if a draft message was wrong, link forward to corrected version using the archive’s correction discipline).

### MPA-5: After-action summary + improvement ledger (AAR+IL)
Publishable “hotwash” summary:
- top 5 strengths,
- top 5 gaps,
- improvement items with an owner role, target date, and status.
This is the key **anti-amnesia** artifact: improvements must be tracked to closure.

## Stop conditions (dual-use / safety / privacy)
Do **not** publish:
- detailed “injects” that reveal adversary pathways or detection blind spots,
- facility layouts, equipment storage locations, delivery routes, or staffing schedules,
- system configs, network maps, remote-access details, or admin procedures,
- any voter PII or case-level adjudication details,
- observer/poll-worker identity lists.

If a public records request or dispute demands these, route through: `docs/253-public-records-requests-retention-and-access-bounds.md` and the safe-red-teaming guardrails in `docs/249-threat-model-ledger-and-safe-red-teaming.md`.

## Integration points in this archive
- Tie exercise comms outputs to the **public communications control** surfaces: `docs/247-ops-security-controls-comms-and-chain-of-custody.md`
- Use the **uncertainty-safe update discipline**: `docs/219-uncertainty-safe-public-updates.md`
- For cyber incidents, align the incident lifecycle language with NIST 800-61r3.


## Primary anchors

- [CISA — Election Security: Building Trust through Secure Practices](https://www.cisa.gov/resources-tools/resources/election-security-building-trust-through-secure-practices-0)
- [CISA — Best Practices for Securing Election Systems](https://www.cisa.gov/best-practices-securing-election-systems)
- [NIST — SP 800-61r3 Computer Security Incident Handling Guide (PDF)](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r3.pdf)
