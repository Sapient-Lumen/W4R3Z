# Civic Lottery & Deliberation Infrastructure (Cross‑Scope)

**Stack relation:** use `284-deliberation-stack-binding-and-legitimacy-guide.md` for the canonical route across the deliberation cluster. This memo is the infrastructure and institutionalization layer; `143` is the front door; `111` is the binding kernel; `224` is the process-rails layer; `88` is the institution-design specialization; `180` is the legitimacy-stack comparison memo.

**Merge relation:** implementation-facing civic-lottery subsystem memo. Use `143-deliberative-systems-and-citizens-assemblies.md` as the canonical deliberation front door; this memo specializes in institutionalizing representative selection, participant support, and binding-response infrastructure.


**Purpose:** specify a **minimum viable, institutionalizable deliberation stack** (civic lottery + supported deliberation + binding response obligations) that can plug into micro‑local to global governance without turning participation into theatre.

**Person served:** a person affected by policy who needs **credible voice** (not symbolic consultation) and a **checkable chain** from “what we heard” → “what we decided” → “what changed”.

**From‑below:** this memo treats deliberation as an **accountability interface**. It is designed so an ordinary person can verify whether a process was representative, safe, informed, and consequential (and can challenge it when it was not).

**Key citations:** OECD good‑practice principles for representative deliberation [BIB-OECD-DEL], evaluation guidance [BIB-OECD-RDP-EVAL-2021], and institutionalization patterns [BIB-OECD-8WAYS-2021]; fairness-aware selection algorithms for citizens’ assemblies [BIB-FLANIGAN-FAIR-ALGO-2021].

---

## Why this exists (failure modes)

Representative deliberation is often deployed as:
- **Consultation theatre:** “we listened” with no obligation to respond or change.
- **Selection capture:** self‑selection and “usual participants” dominate.
- **Information capture:** expert briefings are one‑sided; framing does the work.
- **Harassment & exclusion:** participation is costly, unsafe, or humiliating.
- **No memory:** outputs are not preserved, indexed, or traceable into decisions.
- **No evaluation:** process quality is asserted, not evidenced.

OECD principles explicitly foreground consequences, representativeness, integrity, transparency, and evaluation as quality conditions for deliberative processes [BIB-OECD-DEL] [BIB-OECD-RDP-EVAL-2021].

---

## Design stance: deliberation as an interface, not an event

This archive treats civic lotteries / assemblies as **a reusable subsystem**:
- **Input:** a scoped question + constraints + what authority is delegating.
- **Process:** representative selection + supported deliberation + record.
- **Output:** recommendations + minority reports + confidence/uncertainty notes.
- **Binding response:** decision makers MUST publish a structured response (accept/adapt/reject with reasons) and route accepted items into implementation dockets.

Institutionalization matters: one‑off “projects” are easy to ignore; recurring, standard‑bound processes are harder to dissolve or co‑opt [BIB-OECD-8WAYS-2021].

---

## Minimal Viable Deliberation Infrastructure (MVDI)

### MVDI‑1: Civic lottery protocol (representative selection)
A commissioning authority MUST publish:
- **Population definition** (who is eligible; why).
- **Stratification dimensions** (e.g., age, gender, geography, income proxies) and targets.
- **Recruitment + response-rate plan** (to avoid systematic exclusion).
- **Selection algorithm and auditability** (including randomness source).
- **Participation supports** (see MVDI‑3).

Where representativeness and equal selection probabilities conflict due to differential participation, authorities SHOULD use fairness-aware selection methods (e.g., approaches described by Flanigan et al.) and MUST disclose tradeoffs and achieved representativeness [BIB-FLANIGAN-FAIR-ALGO-2021].

**Artifact:** `CA-SEL` (Selection & representativeness report)
**Join keys:** `CA-ID`, `CA-POP`, `CA-STRATA`, `CA-RAND`, `CA-WEIGHT`

### MVDI‑2: Consequence contract (no theatre)
Before recruitment begins, the authority MUST publish a “consequence contract”:
- What decisions are in scope.
- What is **delegated** to the assembly vs reserved.
- The response obligation format and deadlines.
- What happens if leadership changes mid‑process.
- How recommendations map to implementation mechanisms (dockets, budgets, rules).

**Artifact:** `CA-CON` (Consequence contract)

### MVDI‑3: Participant safety, dignity, and cost removal
Representative deliberation fails if participation is costly or unsafe. Processes MUST provide:
- **Paid time** (or stipend), childcare, transport, accessibility supports.
- **Trauma‑informed facilitation** when topics involve harm.
- Clear anti‑harassment protocols and confidentiality lanes where needed.
- **Right to withdraw** without penalty and with support.

These align with integrity and inclusiveness principles [BIB-OECD-DEL].

**Artifact:** `CA-SAF` (Safety & supports plan)

### MVDI‑4: Balanced information & contestable framing
Authorities MUST:
- Publish a **briefing pack provenance log**: who wrote what, what was excluded, conflicts of interest.
- Include **adversarial review** of framing (red team the question; list what would be “begged” by alternative framings).
- Provide a mechanism for participants to request additional expertise and for the public to propose missing evidence.

**Artifacts:** `CA-INF` (Information pack + provenance); `CA-FRM` (Framing audit)

### MVDI‑5: Records, memory, and minority protection
Outputs MUST be legible and preserved:
- Recommendations with **rationale**, dependency notes, and expected tradeoffs.
- **Minority reports** and “unresolved disagreements”.
- A structured summary for non‑experts.
- A public archive with stable IDs and change history.

**Artifacts:** `CA-OUT` (Outputs bundle); `CA-MIN` (Minority reports); `CA-REC` (Record index)

### MVDI‑6: Evaluation as a first‑class deliverable
Every process MUST be evaluated using a published framework and questionnaire set, with results made public (redacting only what is necessary for safety/privacy). OECD provides a concrete evaluation methodology and questionnaires for representative deliberative processes [BIB-OECD-RDP-EVAL-2021].

**Artifact:** `CA-EVAL` (Evaluation report)

---

## Binding response rail (connect deliberation to power)

Decision makers MUST publish a `CA-RESP` response within a fixed time window:
- For each recommendation: **ACCEPT / ADAPT / REJECT / DEFER**.
- Reasons in plain language plus technical annex if needed.
- If ACCEPT/ADAPT: a link to the implementation docket entry (budget line, rulemaking docket, procurement plan).
- If REJECT: state what evidence would change the decision and whether a future assembly could revisit.

This memo inherits the archive’s “Decision Receipt” logic: outputs without a response rail are not governance; they’re comms.

**Artifact:** `CA-RESP` (Structured response)

---

## Where this plugs in (scope guidance)

- **Micro‑local:** use MVDI for zoning, school boundaries, policing policies; keep questions narrow; prioritize lived-experience evidence.
- **Municipal / regional:** recurring assemblies for budget priorities and service tradeoffs; pair with participatory budgeting modules when allocating discretionary funds [BIB-WB-PB-GUIDE] [BIB-SCHUGURENSKY-PB-2024].
- **National:** standing “deliberation office” that commissions assemblies and maintains standards; multiple institutionalization pathways exist [BIB-OECD-8WAYS-2021].
- **Cross‑border / global:** use federated assemblies (country panels feeding a global synthesis) with explicit legitimacy limits; avoid pretending it is “world parliament”. Bind outputs into treaty/standard-setting dockets and publish response obligations.

---

## Test hooks (for `107-governance-test-suite.md`)

Add/verify checks:
- **RDP‑REP:** achieved representativeness vs target; disclosed deviations (`CA-SEL`).
- **RDP‑SAFE:** participation supports exist; no-cost barrier eliminated (`CA-SAF`).
- **RDP‑INF:** briefing provenance + framing audit present (`CA-INF`, `CA-FRM`).
- **RDP‑RESP:** structured response published on time (`CA-RESP`).
- **RDP‑EVAL:** evaluation published and linked (`CA-EVAL`).

---

## Implementation starter kit (smallest useful form)

If you can only ship one version:
1. Publish `CA-CON` and `CA-RESP` templates first (consequence + response rails).
2. Run a pilot with `CA-SEL`, `CA-SAF`, `CA-INF`, `CA-OUT`.
3. Publish `CA-EVAL` and iterate on representativeness + safety barriers.

This keeps deliberation from becoming an aesthetic: consequence and evaluation are the anti-theatre anchors [BIB-OECD-DEL] [BIB-OECD-RDP-EVAL-2021].
