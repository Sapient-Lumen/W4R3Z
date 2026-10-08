# Assurance Case (AC-*) & Governance Safety Case (Claim–Argument–Evidence discipline)

**Purpose:** require structured safety arguments for high-risk governance systems so ‘trust us’ is not a control.

**Person served:** People exposed to high‑discretion, high‑consequence systems who need claims, evidence, and stop conditions stated up front so safety isn’t a promise.

**From-below:** This forces decision‑makers to show their reasoning and evidence, so safety claims can be tested, challenged, and improved.
**EXP pointer:** counters `EXP-07` (Indifference) by forcing claims to include enforceable floors and stop-conditions (`98-persons-path-and-accessibility-invariants.md`).
**As-of & corrections:** safety claims are evaluated “as-of” a stated artifact set; corrections require an explicit update cycle and downstream propagation (`53`, `70`) (see `101-claude-rev142-normative-requirements.md` (NR-07, NR-15)).

When discretion and downside risk are high, “checklists” and generic compliance reports tend to fail: they are hard to contest, hard to update, and easy to game.
An **assurance case** is the smallest public artifact that forces a unit to state:

- **what it claims is acceptably safe/just**,
- **why that claim should be believed**, and
- **what evidence + monitoring will falsify it**.

This memo adapts assurance-case practice from safety engineering to governance (without importing heavyweight bureaucracy). See [BIB-ISO-IEC-15026-2], [BIB-OMG-SACM-2-1], and the GSN community standard [BIB-GSN-COMMUNITY-STD-2011].

## Kernel anchors (do not repeat)
- Metrics/evidence discipline: `03-...`.
- Internal controls + continuous assurance: `84-...`.
- Publication integrity for claims and evidence: `53-...`.
- Records custody / “as-of” access for safety claims: `31-...`.
- Person-facing access + representation duty (who can use the safety case to contest harm): `98-persons-path-and-accessibility-invariants.md`.
- Protective legibility + adoption dynamics (safety cases can become theater; design for power): `99-protective-legibility-and-adoption-dynamics.md`.

## Named tensions (design must surface these)
- Rigor and independence vs feasibility (don’t require impossible assurance).
- Transparency of evidence vs security/attack surface disclosure.
- Narrative coherence vs cherry-picked metrics (assurance as story-with-proof).
- Standard assurance templates vs domain-specific hazards and plural implementations.

---
## A. When an assurance case is required (bright lines)

Publish an `AC-*` when ANY of the following hold:
- **Coercion / deprivation power:** policing, custody, sanctions, forced removal, surveillance at scale (see `05-...`, `43-...`).
- **Emergency / exception power:** time-bounded expansions of authority (see `23-...`, `45-...`).
- **High-stakes automated or data-driven decisions:** eligibility, enforcement targeting, access gating (see `06-...`, `42-...`, `33-...`).
- **Critical infrastructure / cyber operations:** service-critical IT/OT and emergency cyber actions (see `59-...`).
- **Cross-boundary regimes with limited exit:** supranational/global compacts where remedies are otherwise thin (see `50-...`, `60-...`).
- **Material fiscal tail-risk:** policies that can trigger large contingent liabilities or systemic risk (see `07-...`, `18-...`).

**Rule of thumb:** if a reasonable person could ask “*why should I trust this power?*”, require an `AC-*`.

---

## B. Minimum public structure (keep it small, but real)

An assurance case has **two layers**:
1) **Public summary (1–2 pages)**: contestable by non-experts.
2) **Evidence docket (links only)**: points to `REL-*`, `EVAL-*`, `OFR-*`, `DRR-*`, `STD-*`, `CON-*`, etc. (do not paste bulky annexes into the archive).

**Minimum fields (public summary):**
- **`AC-ID` + owner Unit ID** (`34-...`), effective date, next review date.
- **Scope + boundaries** (what is covered / excluded; interfaces to other units).
- **Material floor + degraded mode:** disclose the staffing/budget/offline/time burdens assumed, and the lowest‑infrastructure variant for contestation and monitoring (paper receipts, low‑bandwidth publishing, independent witness/recordkeeping, minimum service floor). If the claim depends on conditions not met today, state the Phase −1 path explicitly (`80-...`) and the stop‑conditions that prevent indefinite “later.” (See `101-claude-rev142-normative-requirements.md` (NR-13, NR-17).)
- **Top claim(s)** (what “acceptable” means here) and **non-claims** (what is not promised).
- **Threat/hazard mapping:** top `TM-*` threats and how each is controlled (use `72-...` bundles where possible).
- **Argument outline:** 3–7 bullets explaining *why* controls + operations + oversight make the claim credible. (GSN is optional; use it only if it clarifies.)
- **Evidence pointers:** a short list of **docket IDs** (not narrative) that support each argument leg:
 - `REL-*` baselines/outcomes,
 - `EVAL-*` tests,
 - `OFR-*` audits/findings,
 - `DRR-*` approvals and risk acceptances,
 - `STD-*` pinned standards and conformance tests,
 - `CON-*` procurement clauses that make the above enforceable.
- **Monitoring signals:** ≤10 metric IDs + who watches + what happens when thresholds trip (`03-...`, `28-...`).
- **Triggers & stop‑conditions:** the smallest set of events that force pause/review (e.g., incident rate spike, audit failure, repeated adverse outcomes, remedy backlog breach).
- **Remedy + interim protection:** which `AL-*` lanes can provide effective relief, and how emergency relief/stays work (`08-...`, `36-...`). For person-facing harms, include the **Person’s Path** check: comprehension-tested notices/receipts, navigation duty, safe filing/representation, and an offline channel where needed (`98-persons-path-and-accessibility-invariants.md`).
- **Revision log:** versioned; no silent edits (`53-...`).

---

## C. Interfaces (how AC-* joins to the rest of the system)

An assurance case MUST be joinable:
- **Program/policy:** link from `PROG-*` + any `CLM-*` claims it relies on (`28-...`, `37-...`).
- **Rules:** cite `RULE-*` **as-of** for any enforceable constraint (no “dark enforcement”) (`25-...`, `39-...`).
- **Automation/data:** if relevant, link to `ADS-*` and `DPR-*` entries (`42-...`, `33-...`).
- **Oversight:** link to the open `OFR-*` case(s) and closure evidence (`32-...`, `55-...`).
- **Procurement:** link to major `CON-*` artifacts when delivery is outsourced (`38-...`).
- **Incidents:** material failures MUST be tagged to the relevant `AC-ID` in `DRR-TYPE: INCIDENT` so postmortems cannot ignore the governing argument (`31-...`, `24-...`).

---

## D. Anti-theater checks (how to keep AC-* honest)

**The assurance case fails if:**
- the claim is unfalsifiable (“we will be fair” without thresholds, lanes, or evidence),
- evidence is not retrievable by stable IDs,
- monitoring has no decision hook (no action when signals trip), or
- remedies cannot stop harm in time.
- **protective legibility is absent:** the case is “public” but unusable (no standing/safety/independent enforcement to act on evidence), or the design centralizes legibility in ways that are easily weaponized (`99-protective-legibility-and-adoption-dynamics.md`, `32-...`, `77-...`).

**Minimum honesty mechanisms:**
- require **independent challenge** for high-risk `AC-*` (oversight seat, external audit, or adversarial review),
- publish a **staleness report** (cases not reviewed on schedule),
- treat **risk acceptance** as a time-bounded `DRR` (with a review date and reason code).

---

## Sources / anchors (keep tight)
- Assurance-case minimum structure: [BIB-ISO-IEC-15026-2].
- Metamodel / structured representation: [BIB-OMG-SACM-2-1].
- Argument notation baseline (GSN community standard): [BIB-GSN-COMMUNITY-STD-2011].
- Safety-report precedent for high-hazard regimes: [BIB-HSE-COMAH-SAFETYREPORTS]. 