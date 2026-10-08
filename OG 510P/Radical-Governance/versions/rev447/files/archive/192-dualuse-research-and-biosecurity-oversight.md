# Dual‑Use Research & Biosecurity Oversight (Research as a High‑Risk Public Interface)

**Purpose:** preserve the benefits of life‑science research while minimizing catastrophic misuse/accident risk, without turning “security” into an unreviewable veto.

**Person served:** a researcher, lab worker, student, or neighbor living near a facility, who needs the rules for risky research to be legible, consistently applied, and contestable—so safety is real, not performative.

**From-below:** this memo makes **biosafety/biosecurity decisions auditable** (who decided what, on what basis, with what mitigations), and creates safe reporting paths when institutions would prefer silence.

**Relationship to existing memos:** this is a **research‑ecosystem extension** of `57-public-health-and-biosecurity-governance.md` (outbreak response) and `168-intelligence-and-secrecy-governance.md` (bounded secrecy). It focuses on *pre‑event* governance: labs, funders, publishers, and suppliers.

**Anchor set:** risk‑based lab biosafety and safety culture framing: [BIB-WHO-LBM4]. US oversight baseline for Dual Use Research of Concern / “PEPP”: [BIB-USG-DURC-PEPP-2024]. International non‑proliferation frame: [BIB-BWC-FINALDOC-2022]. Synthetic nucleic acid screening framework (supply-side): [BIB-OSTP-NASS-FRAMEWORK]. Institutional biosecurity advisory framing: [BIB-NSABB-HUB].

---

## 0) Named tensions (design must surface these)
- **Openness vs misuse** (publication/disclosure can enable harm; secrecy can hide negligence or abuse).
- **Speed vs review** (fast-moving science vs slow governance).
- **Central standards vs local reality** (risk-based controls must be locally workable).
- **Safety vs liability theater** (paper compliance vs real incident learning).
- **National security vs academic freedom** (bounded veto with reasons + appeals).

---

## 1) Minimum Viable Biosecurity Research Governance Spine (MVBRGS)

Design the system as **a set of joinable public artifacts** with protected private details, rather than informal emails and reputational pressure.

### A) Register the *activity*, not just the funding (a “Research Risk Docket”)
Create a **Research Risk Docket** (`RRD-*`) that logs:
- activity / protocol class (high-level), facility category, sponsoring org, and a *risk posture summary* (public);
- the oversight pathway used (committee, national authority, third‑party review);
- required mitigations + verification method (audits, training, access controls);
- incident reporting obligations and escalation contacts.

**Rule:** if an activity is high‑risk enough to need special controls, it’s high‑risk enough to require **a docket entry** (even if the technical details are protected). Use `31` receipt semantics: as‑of basis, change log, and appeal/review lane.

### B) Risk assessment must be *evidence-based* and repeatable
Adopt a risk assessment framework consistent with WHO’s risk‑based approach (not purely prescriptive checklists) and require a short “risk memo”:
- hazard (agent/process), exposure pathways, failure modes, mitigations, residual risk;
- what would change the decision (new evidence, better mitigations, alternative methods).

Publish the **risk memo outline** and the **decision criteria** (not the sensitive details) so decisions are contestable.

### C) Oversight = layered, not single-point (three lines + independence)
Minimum layers:
1) **Local governance** (IBC / biosafety committee + safety officer) with training and SOP enforcement.
2) **Sponsor/funder governance** (grant conditions, audits, stop-work authority).
3) **Independent/national governance** for defined high-risk categories (with clear thresholds and due process).

Avoid “security by rumor”: high‑risk determinations must be written, receipted, and reviewable.

### D) Incident learning: “no‑fault reporting” with hard backstops
Build a **protected incident reporting channel** for lab workers and contractors:
- confidential intake + non‑retaliation enforcement (`121`),
- rapid containment support,
- published aggregate learnings and leading indicators (near misses, training failures),
- **binding** external investigation for severe incidents (tie to `24-mutual-aid-and-serious-incident-protocol.md` patterns).

### E) Publication & disclosure governance (bounded and appealable)
Create a **Disclosure Review Lane** (`DRL-*`) for publications, datasets, and code when misuse risk is credible:
- default presumption is publish; restrictions require **reasoned, written** justification with expiry.
- offer alternatives: method redaction, delayed release, controlled access, or independent replication.
- provide an **appeal lane** to an independent panel; require time bounds (no indefinite “review”).

Use `172` bounded-secrecy logic: *if you restrict disclosure, you owe a structured reason and a sunset*.

### F) Supply-side controls: screening and auditability without chokepoint abuse
For synthetic nucleic acids and other sensitive inputs:
- require procurement to use screened providers (as defined in the applicable framework),
- require providers to maintain auditable screening logs and red‑flag escalation,
- forbid using screening as a covert trade barrier: publish standards + review denials.

(Design note: screening frameworks can change; keep the rule “buy from screened providers” but version the referenced standard.)

### G) International coordination & confidence-building (avoid “trust me”)
Where cross-border risk is material:
- publish confidence-building measures aligned with BWC norms (aggregate disclosures, safety culture metrics, incident learning),
- enable joint exercises and peer reviews under agreed protocols,
- maintain a public “treaty/compact posture” summary in the docket (what norms you claim to follow).

---

## 2) Scope-fit (micro-local to global)
- **Micro-local:** facility siting and community interfaces; emergency info, grievance lanes, and independent inspection visibility.
- **City/region:** health system integration; hazmat response; workforce training pipelines; inspection capacity.
- **National:** thresholds for high-risk categories, licensing/registration, enforcement, and national incident response.
- **Global:** norm-setting, confidence-building, and interoperability of safety expectations (without forcing identical institutions).

---

## 3) Anti-capture & anti-scapegoat rules
- Separate “safety” from “PR”: require independent inspectors and publish aggregate noncompliance stats.
- Avoid scapegoating individuals for systemic failures: protect reporters; focus enforcement on **control failures**.
- Ban “silent swaps”: if rules tighten/loosen, docket entries must show version changes and transition plans (`118`).

---

## 4) What “ideal” looks like in practice (fast checklist)
- Every high‑risk activity has an `RRD-*` docket entry + review lane.
- Risk criteria are published; sensitive specifics are protected but **decisions are receipted**.
- Incidents and near-misses are reportable without retaliation; severe incidents trigger independent review.
- Publication restrictions are bounded, appealable, and time-limited.
- Inputs (e.g., DNA synthesis) are screened and auditable; denials have reasons + review.
