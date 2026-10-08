# Protective Legibility & Adoption Dynamics (When Transparency Helps — and When It Hurts)

**Purpose:** prevent legibility from becoming a weapon by analyzing adoption incentives, material floors, and misuse risks.

**Person served:** People who could be harmed by transparency theater or weaponized registries and who need legibility that is protective, not predatory.

**From-below:** This helps you decide what to publish and what to shield so transparency protects people instead of enabling targeting or capture.

The archive’s core move is **contestable power**: decisions emit receipts; rules are inventory‑able; remedies are discoverable; money emits traces. This is a design for legitimacy.

This memo adds two missing layers:
1) the **conditions** under which legibility protects the governed (and how it can be weaponized), and  
2) the **political economy** of getting institutions to adopt systems that constrain them.

**See:** `21-legitimacy-architecture.md`, `04-threat-models.md`, `72-threat-response-bundles.md`, `80-implementation-roadmap.md`, `77-sensitive-information-and-secrecy-governance.md`.

## Kernel anchors (do not repeat)
- Person’s path and accessibility floors: `98-persons-path-and-accessibility-invariants.md`.
- Records + publication integrity (what must be visible, as-of): `31-...`, `53-...`.
- Remedy/systemic redress as the purpose of visibility: `08-...`, `36-...`, `76-...`.
- Interop join keys (what gets linked and why): `70-...`.

## Named tensions (design must surface these)
- Legibility for accountability vs legibility for coercion/surveillance.
- Transparency vs retaliation (design for safety and collective action).
- Adoption of constraints vs power’s incentive to evade (paper compliance).
- Standardization for auditing vs plural functional equivalents and local legitimacy.

---
## A) The legibility trap (necessary, not sufficient)

Transparency is often required for accountability, but it is not enough on its own. Legibility protects people when **countervailing power** exists to use it.

Do not treat joinability/coverage as an end state: it is infrastructure; **justice requires use** (actors with power who can act on what’s revealed). (See `101-claude-rev142-normative-requirements.md` (NR-14).)

**Minimum political preconditions (name them explicitly):**
- **independent enforcement capacity** (courts/auditors/ombuds with teeth; not fully captured),
- an enforceable remedy path (`AL-*`) that can compel relief,
- **organized countervailing power** (unions, civil society, independent media) capable of acting on evidence,
- **credible exit options** where feasible (mobility, alternative providers, jurisdictional competition),
- a cultural expectation that authority must explain itself (reasons are not optional).

Where these are absent, increasing legibility can merely help stronger actors optimize.

---

## B) Registry weaponization (legibility vs safety)

Centralized registries can be turned against the people they describe (minorities, dissidents, migrants, the poor). The archive’s safeguards—purpose limitation, access controls, independent oversight, remedy lanes—are necessary but not complete.

**Design posture:** treat “what happens when regimes change?” as a first‑class threat (see `77-...` and `04-threat-models.md`).

**Operational mitigations (compact):**
- minimize what is centralized; prefer federated or compartmentalized designs,
- publish redacted “existence proofs” (possession‑based verification) rather than enumerably queryable personal data,
- enforce role‑based access + audit logs + independent inspection,
- design lawful, logged secrecy (and time‑bounded declassification) rather than ad‑hoc opacity.

---

## C) This is a proposal, not a mandate (pluralism)

The archive describes a high‑confidence path to **contestable governance in written, registry‑friendly systems**. Some societies govern through different legitimate forms (consensus processes, oral or relational authority, customary mechanisms). Where functional equivalents genuinely protect the governed, they should be respected.

**Design test:** do these mechanisms still provide (a) reason‑giving, (b) contestability, and (c) protection for the vulnerable?

---

## D) Adoption dynamics (why would power accept constraints?)

The hardest implementation problem is not technical. It is political: the people who must build legible systems often benefit from opacity.

**Implementation requirement:** any “roadmap” MUST include a minimal coalition analysis:
- who loses discretionary power,
- who gains contestation capacity,
- what incentives (funding access, procurement eligibility, legitimacy benefits) can align adoption,
- what sequencing reduces sabotage risk.

**Coalition prompts (keep tight):**
- **Internal champions:** auditors, ombuds, service delivery managers, and integrity staff who gain from clarity.
- **External pressure points:** courts, media, unions/civil society, donor/credit/trade conditions, and procurement market access requirements.
- **Hostile environments:** prioritize receipts + rules inventory + one record‑compelling front door; treat deeper stacks as direction‑of‑travel.

See `80-implementation-roadmap.md` for practical sequencing.
**Demonstration effects:** prioritize high‑volume services and coercive interactions where receipts and deadlines immediately reduce confusion/waiting and create a constituency for compliance (defense counsel, advocates, frontline managers).

**Compliance ratchet (make gains hard to roll back):** design early artifacts so rollback is costly: mirror public releases, require “as‑of” access + retention, embed the artifacts in routine practice (courts/tribunals, audits, procurement eligibility), and ensure multiple independent consumers exist (media, watchdogs, civil society).

(See `101-claude-rev142-normative-requirements.md` (NR-02, NR-03, NR-20).)
---

## D2) Agency layer (who contests; who uses the joins)

Legibility does not become accountability by itself. **Someone has to use the artifacts**—and the capacity to do so is distributed unequally (time, safety, subsistence, literacy).

Minimal actor-map (each uses public/joinable artifacts):
- **Governed people + advocates:** DRR + cited rules + reason codes + lane registry + service standards (`31`, `52`, `36`, `82`, `98`).
- **Community organizations/unions:** collective filing + participation lanes + systemic redress (`36`, `41`, `76`, `98`).
- **Journalists/researchers:** releases, records, audit traces, and omission signals (`51`, `31`, `03`, `83`).
- **Inspectors/ombuds/oversight:** intake tracking + audit/inspection loops + sanction triggers (`47`, `72`, `83`, `84`).
- **Courts/tribunals:** portable record bundles + reason codes + correction propagation (`31`, `52`, `70`).
- **Funders/donors/procurement:** condition access on specific artifacts, not rhetoric (`80`, `30`, `46`).

The design implication is **friction minimization**: one-screen receipts, navigation duty, low‑travel channels, and automatic advocate hooks for those who cannot self‑contest (`98`, `08`, `64`, `68`).

---

## E) Degraded modes and Phase −1 (severe constraint)

The archive works without high tech, but this must be explicit.

Material floor reality: the infrastructure here assumes a minimum substrate (revenue/clerks, literacy/translation/navigation support, and enough safety + time/subsistence to contest). Where those preconditions are absent, read recommendations as a **direction of travel**: start with the simplest, person‑proximate artifacts (receipts at points of coercion) while building capacity.

**Phase −1 (bootstrap) baseline:**
- paper, numbered receipts for the highest‑coercion/highest‑harm points (detention, checkpoints, tax collection, aid distribution, benefits cutoffs),
- a public place to post rules and service standards (bulletin boards, radio, community intermediaries),
- a mobile/field ombuds intake (or equivalent) with tracking numbers.

These artifacts are a minimum viable join‑key layer: they make later registries possible.

---

## F) “If you can only do three things” (minimal package)

When capacity is low, start with the smallest set that makes abuse contestable:

1) **Receipts for rights‑affecting actions** (`DRR-*`, with `RULE-*` as‑of, ≥1 `RC-*`, and ≥1 `AL-*`).  
2) **A public rules inventory** (even if crude) so people can know what is being enforced.  
3) **One independent front door with teeth** (ombuds/tribunal or equivalent): accepts filings offline, can **compel production of records**, and can trigger interim protection / escalation where stakes are high.

Everything else can grow around these.
