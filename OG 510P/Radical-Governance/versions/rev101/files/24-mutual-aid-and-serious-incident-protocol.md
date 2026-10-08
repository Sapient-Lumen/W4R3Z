# Mutual Aid & Serious Incident Protocol (Cross-Scope Safety Operations)

Mutual aid is how polycentric systems *actually work* under stress: jurisdictions lend personnel, equipment, and authority across boundaries.
It is also a high-risk interface: unclear command, unclear legal basis, weak logs, and conflicted investigations produce abuse, fiscal surprises, and legitimacy collapse.

This memo defines a compact **Mutual Aid & Serious Incident Protocol (MASIP)** that can be used for policing, public order, EMS, fire, and other safety services—especially when coercive powers are exercised.

**See also:** `19-compacts-and-cooperative-governance.md` (compact structure), `05-public-safety-and-coercion.md` (use-of-force constraints), `23-emergency-governance-and-exceptions.md` (emergency declarations and exception logging), `70-interoperability.md` (IDs + ledgers).

**Anchor set (start here):**
- FEMA NIMS *Guideline for Mutual Aid* (activation terms + resource sharing): [BIB-FEMA-NIMS-MUTUALAID]
- FEMA *National Incident Management System* (ICS/command-and-coordination baseline): [BIB-FEMA-NIMS]
- JESIP *Joint Doctrine: The Interoperability Framework* (multi-agency joint working + joint decision models): [BIB-JESIP-JOINTDOCTRINE-2024]
- UN Basic Principles on the Use of Force and Firearms (reporting + review + accountability expectations): see [BIB-UN-UOF].
- OHCHR *Minnesota Protocol* (independent investigation standard when death is potentially unlawful): [BIB-UN-MINNESOTA-PROTOCOL]

---

## 1) Definitions (minimum shared vocabulary)
- **Mutual aid:** provision of resources (people, equipment, services) from an **assisting** jurisdiction to a **requesting** jurisdiction.
- **Aid activation:** the event where aid is requested, accepted, and operational command is established.
- **Operational command:** who sets objectives and directs operations (often “incident command”).
- **Legal authority basis:** the specific statute/compact clause/emergency power that allows the assisting personnel to act (including detention/use-of-force authority, if any).
- **Serious incident:** any event that triggers mandatory independent review. Minimum trigger set:
  - death or life-threatening injury involving state force or custody,
  - firearm discharge at a person (or equivalent lethal-force event),
  - in-custody death or credible torture/ill-treatment allegation,
  - mass-casualty or high-public-impact events where accountability depends on rapid evidence integrity.

---

## 2) MASIP: Minimum Viable Mutual Aid (MVM-AID)

### A) Preconditions (standing readiness)
A mutual aid relationship MUST have:
- a **registered compact** (see `19-...`) with a stable compact ID in the compact register (`70-...`),
- **credentialing + role typing** for deployable staff (who is qualified to do what),
- a **command-and-control doctrine** (e.g., ICS-like) that both sides train on,
- a default **no-coercion** posture unless coercive authority is explicitly granted and logged.

### B) Activation (request → accept → command)
Every activation MUST publish a **Mutual Aid Activation Log (MAAL)** as a joinable **Decision Record/Receipt**:

- issue a `DRR-*` tagged **`DRR-TYPE: AID`** (this `DRR` *is* the MAAL),
- cite the governing compact `CMP-*` (or “NO COMPACT” with legal basis and an urgent fix plan),
- cite `EMR-*` if emergency authority is invoked, and
- provide a clear `AL-*` complaint / review lane for aid operations.

**MAAL (`DRR-TYPE: AID`) minimum fields**
- compact ID + legal authority basis (`RULE-*` as-of; `EMR-*` if used),
- requesting Unit ID, assisting Unit ID(s), start time, expected end time,
- resource types and scale (teams/equipment/services) + credential/role typing,
- operational command designation (who is in command; who retains employer discipline),
- rules of engagement / use-of-force and detention standards that apply (which policy wins on conflict),
- accountability routing (who investigates what; where complaints go; default independent IIA rule),
- cost / reimbursement rule (who pays for what; cap and approvals),
- termination condition (time-bound by default; renewal requires an explicit update `DRR`).

**Rule:** *No joinable record, no aid.* If connectivity prevents publication at activation, the minimum `DRR-TYPE: AID` record MUST be created within 24 hours (with a typed “late entry” reason code).

### C) Operation (execution constraints)
During operations:
- assisting personnel MUST be clearly identifiable (agency + role), with audit-friendly ID where feasible.
- the requesting jurisdiction’s standards MUST be the baseline **unless** the compact specifies stronger standards (never weaker).
- any **expansion of authority** (e.g., authorizing detention/use-of-force where it was not planned) MUST be logged as an update `DRR` that references the original MAAL `DRR-*` (with approver + legal basis).
- cross-scope data sharing MUST follow `70-...` (role-based access + audit logs).

### D) Demobilization and after-action
Every activation MUST close with:
- a short **after-action record** linked to the MAAL `DRR-*` (what happened; what failed; what changed),
- a **cost reconciliation** record (actuals vs expected; claims/compensation),
- a list of any **complaints / serious incidents** and their join-keys (`AL-*`, `ENF-*`, `OFR-*`).

---

## 3) MASIP: Serious Incident Independence (MVM-SIP)

The key risk in mutual aid is **conflicted review**: “we investigated ourselves / our partners” and everyone loses trust.
MASIP requires a *portable independence rule*.

### A) Default independence rule (who investigates)
For any serious incident involving assisted operations:
- an **independent investigating authority (IIA)** MUST be assigned automatically.
- the IIA MUST be institutionally separate from both (a) the operational chain of command and (b) the employing agency of involved personnel.
- if the requesting jurisdiction lacks a credible IIA, the compact MUST pre-designate an external IIA (regional inspectorate, ombuds office, prosecution-led unit, or other trusted body).

### B) Evidence integrity (minimum)
- immediate evidence preservation protocol (scene, body-worn camera/records, comms logs).
- an `OFR-*` entry created within 24 hours in state `OPEN` with `OFR-KIND: CASE` (this is the Serious Incident Case ID), linked to the MAAL `DRR-*`, any relevant `ENF-*` events, and any `EMR-*` episode/measure IDs.
- initial public notice within a short window (what is known; what is being investigated; what the public can expect next), consistent with due process.

### C) Findings, remedy, and learning loop
Each serious incident MUST produce:
- a determination (facts + legality + policy compliance),
- a remedy path (discipline/prosecution where warranted; compensation and non-repetition commitments),
- a learning artifact: a minimal “what changes now” list, not just blame.

**Rule:** investigations MUST be time-bounded or explicitly extended with reasons; silence is treated as failure.

---

## 4) Failure modes MASIP is designed to prevent
- **Hidden government:** aid happens off-book; no one knows who acted or why.  
  Counter: MAAL + compact register + competence ledger linkage.
- **Command confusion:** unclear operational authority → unsafe escalation.  
  Counter: explicit command designation + doctrine + logged amendments.
- **Standards arbitrage:** weak jurisdiction uses aid to evade stronger constraints.  
  Counter: “stronger standard wins” rule + logged standards in MAAL.
- **Conflicted review:** agencies protect each other.  
  Counter: default IIA assignment + case IDs + public timelines.
- **Fiscal surprises / off-book liabilities:** reimbursements, injuries, claims.  
  Counter: pre-set cost rules + caps + reconciliation.

---

## 5) Minimum metrics (≤10; stable across scopes)
These map primarily to `03-metrics-and-evidence.md` packs: [SAC-5] mutual aid logging, [SAC-3] time-to-independent-review, [LRR-4] complaint/remedy timelines, and [IPM-7]/[IPM-10] reconciliation and transfer predictability (where applicable).
1) # of MAAL activations (by type; by assisting/requesting).  
2) Median time to create MAAL (and % created within 24 hours).  
3) % activations with coercive authority granted (and whether pre-authorized).  
4) # serious incidents linked to activations (rate per activation).  
5) Median time to assign IIA + create case ID.  
6) Median time to initial public notice.  
7) Median time to investigation close (and % time-bounded extensions).  
8) $ reconciliation delta (expected vs actual) and # unresolved claims >90 days.  
9) # policy changes made from AARs (count, not narrative).  
10) Complaint resolution time distribution (with escalation rate).

---

## 6) Integration checklist (where this plugs in)
- Toolkit: add MASIP as an interface primitive under IOP (`02-design-toolkit.md`).
- Safety: scope memos use MASIP for regional/national mutual aid (`05-...`, `14-...`, `16-...` as needed).
- Interoperability: mutual aid activations are `DRR-*` records tagged `DRR-TYPE: AID` (MAAL), and serious incidents open `OFR-*` entries (`70-...`).
- Compacts: mutual aid compacts MUST embed MASIP fields and independence rules (`19-...`).
