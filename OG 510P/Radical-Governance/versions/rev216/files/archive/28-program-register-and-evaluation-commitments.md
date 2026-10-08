# Program Register & Evaluation Commitments (Making Policies Testable)

**Purpose:** ensure programs are auditable over time (goals, metrics, evaluation commitments) so failure can’t hide.

A governance system can publish *data* and still fail to **learn** if nobody can answer:
- *What programs exist?* (with stable identifiers)
- *What were they supposed to achieve?*
- *What evidence will trigger change or shutdown?*

This memo defines a compact **Minimum Viable Program & Evaluation System (MVPES)** that fits the archive’s register pattern (`IOP-9`) and plugs into the competence ledger.

**Anchor set (high-trust):**
- UK Government Evaluation Registry requirement (mandatory registration from 1 Apr 2024): see [BIB-UK-EVALREG-GUIDE].
- US Evidence Act summary (learning agendas / annual evaluation plans): see [BIB-US-EVIDENCEACT-EVALGOV].
- Magenta Book (UK evaluation guidance; updated 2025): see [BIB-UK-MAGENTA-2025].
- OECD cross-country view on ex post evaluation (Government at a Glance 2025): see [BIB-OECD-GAAG2025-EXPOST].

---

## Kernel anchors (do not repeat)
- **Person-facing invariants:** `98-persons-path-and-accessibility-invariants.md` (no AI/digital-only gates; oral/assisted options; safety).
- **Remedy is part of the interface:** `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md` (contestability; time bounds; functional equivalents).
- **Protective legibility (transparency ≠ safety):** `99-protective-legibility-and-adoption-dynamics.md`.
- **Records + publication integrity:** `31-records-foi-and-government-memory.md`, `51-release-registry.md`.
- **Measurement loops:** `03-metrics-and-evidence.md`.

## Named tensions (design must surface these)
- **Learning vs punishment:** evaluation for improvement vs audit-as-weapon.
- **Transparency vs gaming/retaliation:** publish results vs manipulate or target whistleblowers.
- **Experimentation vs rights:** pilot flexibility vs non-consensual harm.
- **Short-term KPIs vs long-term damage:** quick wins vs intergenerational costs (`89-...`).

## A. Minimum Viable promise (what this system must do)
1) Maintain a public inventory of **major programs and policies** with stable IDs.
2) For each major program, publish ≥1 **testable claim** as a joinable `CLM-*` object (predicted effects + which metrics matter). See `37-claims-evidence-and-update-discipline.md`.
3) Publish **evaluation commitments** and results (including negative results) with stable IDs.
4) Make changes legible: versions, effective dates, and a change log (no silent rewrites).
5) For service-heavy programs, publish **person-facing** claims/guardrails: wait-time promises (ack / first contact / decision + tail), proof burden, and safe-to-file signals (fear/retaliation). Treat dignity failures as outcomes, not anecdotes (see `47-...`, `82-...`, `98-persons-path-and-accessibility-invariants.md`).

**Default threshold:** apply MVPES to (a) high-spend programs, (b) rights-affecting programs, and (c) high-discretion programs.

---

## B. The two core registers

### 1) Public Program Register (PPR)
A public inventory of major programs/policies that can be joined to budgets, rules, procurement, and outcomes.

**ID format (recommended):** `UNITID-PROG-SEQ` for programs and `UNITID-EVAL-SEQ` for evaluations (or equivalent namespacing by Unit ID). Never reuse IDs; version changes in-place with a change log.

**PPR — minimum schema (register pattern)**
| Field | Meaning |
|---|---|
| `PROG-*` ID | stable identifier (join-key) |
| Owning unit | Unit ID (competence ledger) |
| Title | short program name |
| Status + version | active/paused/retired + revision |
| Effective dates | start / major revision / sunset (if any) |
| Legal basis | Rule ID(s) (PRR) / statute / compact |
| Scope | population/service/territory (coverage) |
| Budget link | program line(s) / appropriation IDs (where available) |
| Delivery channel | in-house / contracted / grant / transfer |
| Key risks | link to threat models and risk tier |
| Success measures | ≤10 metric IDs (e.g., `[CAD-2]`, `[LRR-4]`) + linked Release IDs where feasible |
| Claims | list of `CLM-*` IDs (falsifiable predictions; status tracked) |
| Evaluation commitment | link to `EVAL-*` ID(s) (see below) |
| Change log | what changed and why (`RULE`/`STD`/`REL` IDs as join-keys) |

**Hard rule:** if a program is used to justify meaningful spend or rights constraints, it MUST have a `PROG-*` ID and MUST be in the register.

### 2) Evaluation Registry (ER)
A public index of planned/live/completed evaluations tied to `PROG-*` IDs, so evaluation doesn’t disappear when leaders change.

**ER — minimum schema**
| Field | Meaning |
|---|---|
| `EVAL-*` ID | stable identifier |
| `PROG-*` ID(s) | what is being evaluated |
| Tested claims | list of `CLM-*` IDs tested (if applicable) |
| Evaluation question | 1–3 priority questions |
| Method | design type + key assumptions (link) |
| Protocol | evaluation protocol / pre-analysis plan / preregistration link (if any) |
| Data / releases | Release IDs used + privacy tier |
| Timeline | start date; expected publication date |
| Publication | report link + redactions policy |
| Decision hook | what decision follows (revise/scale/stop) |
| Independence | internal/external + conflict disclosure |
| Evaluator selection (optional) | internal assignment / open call / random assignment from accredited pool (publish which) |
| Status | planned/live/completed + change log |
| Cancellation / slippage | if delayed/cancelled: updated publication date + published reasons (log as a register change; see below) |

**Rule:** evaluation results MUST be linked back into the Program Register entry (`PROG-*`), including “null/negative” findings.

**Rule:** if an evaluation is delayed or cancelled, the ER entry MUST be updated with a reasoned change log and a new expected publication date (no silent cancellations).


## C. Claims discipline (`CLM`)
Treat predictions as first-class join-keys. Programs reference `CLM-*` IDs; evaluations cite which claims they tested.

**Canonical spec:** `37-claims-evidence-and-update-discipline.md`.

**Minimum practice**
- Each major `PROG` has ≥1 `CLM` with: outcomes, ≤3 metric IDs, baseline (`REL` where possible), target range, harms/guardrails, review trigger.
- Each `EVAL` cites the `CLM` IDs tested and links to the response (program revision or follow-on `DRR`).

---

## C. Learning agenda + annual plan (lightweight)
To avoid “evaluation theatre,” keep a **small learning agenda**:
- a rolling set of priority questions (≤15) for the scope,
- an annual evaluation plan that maps questions → `EVAL-*` IDs,
- an explicit capacity statement (what can’t be evaluated and why).

This pattern is compatible with Evidence Act-style “learning agendas” and annual evaluation plans, without importing the whole bureaucracy.

---

## D. Failure modes (and countermeasures)
- **Zombie programs:** programs continue by inertia; no sunsets or reviews.  
  Counter: default review dates and “decision hooks” in ER; publish retirement/continuation reasons.
- **Measurement without agency:** numbers move but nothing changes.  
  Counter: each PPR entry includes a decision hook (what changes if `[CAD-2]` degrades).
- **Evaluation capture:** results suppressed, spun, or quietly cancelled.  
  Counter: independence disclosure; publish protocols; publish negative results; treat cancellation/slippage as a logged register change; publish a reasoned response when a tested `CLM` is contested/falsified (`37-...`).
  Hardening options (pick ≥1; keep simple): (a) **random assignment** of evaluators from an accredited pool, (b) an **external replication** micro‑grant for high‑stakes findings, (c) a ring‑fenced evaluation budget line, (d) a rule that “counter‑evaluations” must be preregistered + published by a deadline (or logged as slippage).
- **Register drift / silent rewrites:** program is renamed or re-scoped without trace.  
  Counter: register versioning + change log; major changes require a new version + effective date.
- **Over-instrumentation:** everything becomes a “program” and the register becomes noise.  
  Counter: threshold rule + “major programs only”; cap success measures at ≤10.

---

## E. Interfaces (how MVPES plugs into the stack)
- **Competence ledger:** each unit links to its PPR and ER (who owns what programs). (`70-interoperability.md`)
- **Rules:** PPR entries cite the Rule IDs authorizing them (PRR). (`25-...`)
- **Money:** PPR entries point to budget lines; where transfers fund delivery, link Transfer IDs. (`18-...`)
- **Procurement:** contracted delivery links to contract IDs (OCDS) for anti-capture auditing. (`22-...`)
- **Evidence:** success measures reference metric IDs and (where feasible) Release IDs from the PDRR (methods + revision logs). (`51-release-registry.md`, `26-...`, `03-...`)
- **Compacts:** when cooperation is formal, PPR entries link Compact IDs. (`19-...`)
- **Services:** where programs govern high-volume services, PPR entries SHOULD reference `SRV-*` IDs and service standards (`82-...`), and evaluations SHOULD test person-facing invariants (comprehension, no-wrong-door routing, wait-time tails) (`98-persons-path-and-accessibility-invariants.md`).



---

## F. Minimal metrics (choose ≤6)
Prefer metric IDs from `03-metrics-and-evidence.md`.
- PPR coverage for major spend/rights-sensitive programs (share) [IPM-7]
- share of major programs with evaluation commitments (ER linked) (assumption: registry exists)
- on-time publication rate for completed evaluations (share) (assumption)
- share of evaluations with an explicit decision hook (revise/scale/stop) (assumption)
- share of program changes that cite a `PROG-*` ID + change log entry (assumption)
- median time from evaluation completion → decision update (assumption)
