# Service Standards & Minimum Service Guarantees (Make Service Power Measurable)

**Purpose:** define minimum service guarantees (time, access, channels) so people can plan and contest delay-as-policy.

**Person served:** A person relying on an essential service who needs clear minimum guarantees and dignity in delivery, plus a real way to contest failures.

**From-below:** This turns service promises into measurable deadlines so waiting and non‑response become actionable failures.

**EXP pointer:** EXP-02 (Waiting), EXP-07 (Indifference), EXP-03 (Proof burden) — see `98-persons-path-and-accessibility-invariants.md`.

**Assistance & representation:** service standards MUST publish the staffed/assisted/oral path (incl. interpretation) and who can act on behalf of someone who cannot safely/self‑advocate, with conflict controls and an independent advocate option in high‑stakes domains. (See `98-...`, `36-...`, `47-...`; `101-claude-rev142-normative-requirements.md` (NR-12, NR-17).)

Most people experience “government” as **service journeys**. When performance expectations are ambiguous, agencies can “deny by delay,” degrade quietly, or shift costs onto users (administrative burden) without changing any rule text.

This memo defines a compact **Service Standard** layer that plugs into `SRV-*` (service catalog) and existing joinable artifacts (`REL/DRR/OFR/AL/RULE/STD`) without creating a new bureaucracy tier.

**Anchor set:** [BIB-UK-SERVICESTANDARD], [BIB-UK-SERVICE-MEASURING-SUCCESS], [BIB-UK-SERVICE-DATA-YOU-MUST-PUBLISH], [BIB-CA-DIGITALSTANDARDS], [BIB-OECD-GPP-SERVICE-2022].

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** transparency can be weaponized; design disclosures and incentives accordingly. (`99-protective-legibility-and-adoption-dynamics.md`)
- Service catalog and access journeys: `47-...`.
- Person-facing accessibility floors: `98-persons-path-and-accessibility-invariants.md`.
- Records/receipts for eligibility and denials: `31-...`.
- Appeals lanes and escalation: `36-...`.

## Named tensions (design must surface these)
- Uniform minimums vs local capacity and context.
- Metric targets vs lived experience (gaming and “paper compliance”).
- Speed/throughput vs correctness and contestability.
- Scarcity triage vs equal-rights floors (avoid rationing by opacity).

---
## A. Definitions (tight)

**Service standard (SS)**
A published, user-facing set of commitments for a service: what the service does, what “success” means, how performance is measured, and what happens when the service fails (remedy/escalation).

**Minimum Service Guarantee (MSG)**
A **floor** for essential services (`ESS-1`) that MUST be met even during outages, fiscal shocks, or emergency mode: e.g., minimum channels, maximum queue time for urgent categories, and a continuity backstop.

**Service performance release (`REL-*`)**
A publishable performance snapshot (cadence-defined) for one or more `SRV-*` entries, with method notes and disaggregation rules.

---

## A1. Waiting is harm (deny-by-delay control)
For essential or rights-affecting services, **time** is a first-class obligation.
- Standards MUST publish a maximum **time to acknowledgement**, **time to first substantive contact**, **time to decision**, and (where relevant) maximum **queue/hold time** for urgent categories.
- Published time commitments are not just targets—they are **promises**. Missing them MUST trigger a duty to account (reasons + revised estimate) and the defined remedy trigger, not silence.
- Standards MUST state **no‑response semantics**: after a missed acknowledgement deadline, filing is presumed received (“safe filing”) and auto‑escalates to a named lane; after a missed decision deadline, interim protection/stay or a deemed outcome triggers where appropriate. The acknowledgement receipt MUST say what happens if the unit misses its own deadline (analogous to `31` “If you do nothing”).

- Standards SHOULD publish **tail harm** signals (not just medians): share waiting >2×, >5×, and >10× the published standard, because the tail is where waiting harm concentrates.
- Missed deadlines MUST trigger a defined consequence (auto-escalation, interim protection, or deemed outcome) rather than silence (see `08-remedy-and-grievance.md`, ALR `36-...`, and `98-persons-path-and-accessibility-invariants.md`).

(See `101-claude-rev142-normative-requirements.md` (NR-05, NR-03).)

## A2. Dignity is an obligation (not a vibe)
Procedural fairness fails if service interactions humiliate people, treat them as suspects, or force repeated proof of identity/eligibility.
Repeatedly requiring people to prove facts the state already holds (or could retrieve with consent) is a design defect and a form of institutional cruelty; if it must happen, it requires explicit justification and alternatives.
- For any rights-/resource-affecting `SRV-*`, the standard MUST include a **dignity + voice commitment**: respectful treatment, clear explanations, minimal repeated documentation, a credible way to be heard, and acknowledgment/apology when the system is wrong.
- Dignity failures are actionable: they belong in complaint/oversight loops (`08-...`, `09-...`) and can be tracked via a small user‑reported measure (bounded, privacy‑safe).
(See `101-claude-rev142-normative-requirements.md` (NR-17, NR-06).)
## B. Minimum Service Standard (one screen per `SRV-*`)

A service SHOULD have an SS once it is public-facing and rights-/resource-affecting (benefits, permits, licensing, bills, enforcement-adjacent interactions).

Common high-stakes `SRV-*` families include benefits delivery (`64-...`), permits/licensing (`29-...`), and tax/fees billing + refunds (`93-...`).

The SS is not a manifesto; it is a **small contract** between authority and user.

**Minimum fields**
- **Scope:** which `SRV-*` entry(ies) this standard covers; channels included/excluded (and why).
- **User promise:** plain-language “what we will do for you” (bounded).
- **Dignity:** respectful treatment + minimal repeated proof + clear explanations; how to report dignity failures.
- **Assistance & representation:** how to get a staffed navigator/assisted/oral path (incl. interpretation), and who can file/act on behalf of someone (authorized representative/advocate), with conflict controls; for high‑stakes services, name an independent advocate intake path. (See `101-claude-rev142-normative-requirements.md` (NR-12, NR-17).)
- **Proof burden inventory:** required evidence/attestations; which items are already held by the state (and how consented retrieval works) vs truly user-supplied; acceptable alternatives; **interaction count + estimated time/cost** for a typical user. (See `101-claude-rev142-normative-requirements.md` (NR-06).)
- **Residual / “no category fit” path:** what happens when a person’s situation does not match the eligibility categories; MUST route to authorized human adjudication (with a reasoned `DRR-*` + `AL-*` lane), not an algorithmic dead‑end. (See `101-claude-rev142-normative-requirements.md` (NR-10).)
- **Corrections / re-adjudication:** when an upstream record used for eligibility/verification is corrected (by the person or by the state), the service MUST re-adjudicate within a stated time bound and issue an updated Decision Receipt (`31`), and where feasible unwind/repair downstream adverse actions. (See `101-claude-rev142-normative-requirements.md` (NR-07, NR-15).)
- **Measures (4–8):** chosen from `CAD-2`, `CAD-1`, `LRR-4`, `LRR-10`, and a small equity slice (disaggregated where relevant).
- **Targets / floors:** at least one **time-to-first-action** target and one **time-to-final-outcome** target (median + 90p).
- **Exception policy:** what counts as a legitimate exception (and what doesn’t), including an explicit **hardship/compassionate discretion** path where lawful; govern departures with the waivers/variances discipline (`85-...`). (See `101-claude-rev142-normative-requirements.md` (NR-16).)
- **Remedy triggers:** what users get when targets are missed (priority escalation, fee waiver/refund, interim protections, auto-open grievance lane, or a compensation rule where lawful).
- **Review cadence:** review date + revision discipline (tie to `74-...` lookback discipline). Include a small category-edge review (mismatch denials + non-application signals) and publish what changed as a `REL-*` release so “invisibility” becomes auditable rather than anecdotal. (See `101-claude-rev142-normative-requirements.md` (NR-10).)
- **Evidence pointers:** the `REL-*` performance release(s) and method note.

---

## C. Join rules (keep it auditable; avoid new ID families)

**1) Put the standard on the service page**
Each `SRV-*` record MUST include a pointer to:
- the governing SS artifact (often a `RULE-*` of kind `POLICY`/`GUIDE`, or a `STD-*`), and
- the current performance `REL-*` release.

**2) Publish performance at a stated cadence**
For material services, publish `REL-SRV-PERF-*` releases at a cadence appropriate to harm (monthly for high-stakes, quarterly for low-stakes). Each `REL` MUST include method notes (definition of “processing time,” exclusion rules, channel coverage, and disaggregation rules).

**3) Bind underperformance to follow-through**
- Chronic SS misses MUST trigger an `OFR-*` case scoped to the service (root cause, corrective actions, deadlines, closure evidence).
- If misses create patterned harms (by group/place), apply `76-systemic-redress-and-pattern-remediation.md` (systemic triggers → scoped corrective cases).

**4) Make emergency mode explicit**
If emergency operations alter service floors, log the change as `EMR-*` and preserve an `ESS-1` MSG floor unless explicitly overridden (and reviewable).

---

## D. Minimum Service Guarantee (MSG) for `ESS-1`

For `ESS-1` services (life/health/rights-critical), the SRV record MUST define a **continuity floor** and this memo adds a user-facing MSG clause:

**MSG minimum**
- **Urgent category definition** (what qualifies).
- **Guaranteed channels** (at least one non-digital channel unless impossible; **no AI‑only front door**—if chatbots/portals exist, a staffed alternative MUST exist; see `98-persons-path-and-accessibility-invariants.md`).
- **Assistance channel:** for high‑stakes queues and filings, provide navigator/interpreter support and a non‑reading option (oral explanation or audio/pictogram summaries) for notices and next steps (`98`, `09`).
- **Maximum urgent queue time** (or interim protection rule if queues exceed).
- **Backstop owner + funding path** (who takes over if the service operator collapses).
- **Public status signal** (how outages/slowdowns are announced; correction timeline).

---

## E. Failure modes this memo blocks (and how)

- **Procedural denial / “deny by delay”** → performance targets + remedy triggers + publishable dashboards.
- **Quiet degradation** → cadence-defined performance `REL` releases + `OFR` triggers.
- **Channel exclusion** → explicit channel coverage and MSG for `ESS-1`.
- **Gaming metrics** → required method notes + disaggregation + stop conditions for perverse incentives.
- **Blame shifting across units** → `SRV-*` ownership + competence ledger joins + “wrong door rate” (`MCL-5`).

---

## F. Minimal metric hooks (do not proliferate)

Default to existing packs, but service standards SHOULD at least cover:
- **[CAD-2] Response/queue times + access friction** (key by `SRV-*`).
- **[LRR-4] Time-to-remedy** (for contestable decisions, including correction propagation + re-adjudication when records are corrected).
- **[MCL-5] “Wrong door” rate** (misrouted users).
- **[IPM-4] Protected disclosure + complaint-channel health** (retaliation/chilling risk signals for high-stakes services; privacy-safe; MUST name at least one degraded/offline safe channel — no personal device required).

See also: `47-service-catalog-and-access-journeys-register.md`, `03-metrics-and-evidence.md`, `09-public-service-and-state-capacity.md`.