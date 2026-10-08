# Claude rev142 Normative Requirements (Compact Integration Anchor)

**Purpose:** provide a *small, citable* list of Claude rev142 normative constraints so the archive can integrate them without copying prose or inflating every memo.

**Person served:** Maintainers and reviewers who need an auditable checklist of “what must be true for this archive to count as from‑below.”

**From-below:** This prevents the archive from drifting into technical elegance that people can’t use when harmed.

**Status:** integration anchor (use this memo for new citations; retire `sources/claude-feedback/rev142/` when feasible per its README).

---

## How to use this memo
- Treat each requirement as a **constraint on designs in this archive** (and on the archive itself).
- Prefer citing the **canonical anchor** listed here rather than citing the raw feedback files directly.
- If you add a new memo/interface, run the checklist in `96-archive-governance.md` and ensure any relevant requirements below are satisfied (or explicitly scoped out with reasons).

---

## Requirements (compressed)

### NR-01 — Person-at-the-counter is the test
Designs MUST stay legible and usable “from below”: a person encountering a decision must be able to find the relevant rule, reason, and path to correction without insider status.
- **Canonical anchors:** `98-persons-path-and-accessibility-invariants.md`, `31-records-foi-and-government-memory.md`, `96-archive-governance.md`.
- **Source:** `../sources/claude-feedback/rev142/feedback-from-claude-04-what-this-is-about.md` §17–§18; `../sources/claude-feedback/rev142/feedback-from-claude-05-persons-path.md` §21–§23.

### NR-02 — Transparency is necessary but not sufficient (legibility-with-bite)
If the archive proposes new receipts, registries, or publications, it MUST also specify what gives them bite (who can compel action; consequence triggers; how the person/advocate invokes follow‑through).
- **Canonical anchors:** `21-legitimacy-architecture.md` (counter‑power floor), `32-oversight-institutions-and-follow-through.md`, `08-remedy-and-grievance.md`, `96-archive-governance.md` (legibility-with-bite rule), `04-threat-models.md` ([TM-33]), `31-records-foi-and-government-memory.md` (Decision Receipt minimum fields).
- **Source:** `../sources/claude-feedback/rev142/feedback-from-claude-01-structural.md` §1, §4; `../sources/claude-feedback/rev142/feedback-from-claude-03-tensions-and-architecture.md` §11a.

### NR-03 — Adoption dynamics are part of the spec
The archive MUST not assume power will voluntarily accept constraints; designs SHOULD identify adoption coalitions, internal champions, external pressure points, and minimum viable subsets for hostile environments.
- **Canonical anchors:** `99-protective-legibility-and-adoption-dynamics.md`, `80-implementation-roadmap.md`.
- **Source:** `../sources/claude-feedback/rev142/feedback-from-claude-01-structural.md` §2.

### NR-04 — Governed person’s experience is an invariant test suite
Interfaces MUST be judged by lived failure modes (proof burdens, error propagation, delay/limbo, fear/retaliation, “no category fit,” indifference/correct-but-harmful outcomes).
- **Canonical anchors:** `98-persons-path-and-accessibility-invariants.md`, `08-remedy-and-grievance.md`, `82-service-standards-and-minimum-service-guarantees.md`, `47-service-catalog-and-access-journeys-register.md`, `36-appeal-lanes-and-redress-registry.md`.
- **Source:** `../sources/claude-feedback/rev142/feedback-from-claude-05-persons-path.md` §20–§23; `../sources/claude-feedback/rev142/feedback-from-claude-10-thinking.md` “On Language”.

### NR-05 — Waiting is harm (deny-by-delay is a control)
Delay and limbo MUST be treated as contestable harm in high-stakes contexts: deadlines, duty-to-account, interim protections where delay moots rights or subsistence.
- **Enforcement convention:** for hard-edge lane/enforcement interfaces, include `**Time bounds & escalation:**` (ack/decision deadlines, no-response rule, tail waits) per `96-archive-governance.md`.
- **Canonical anchors:** `98-persons-path-and-accessibility-invariants.md`, `82-service-standards-and-minimum-service-guarantees.md`, `31-records-foi-and-government-memory.md`, `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md`.
- **Source:** `../sources/claude-feedback/rev142/feedback-from-claude-05-persons-path.md` §20a–§20b.

### NR-06 — Proof burdens must be measurable and contestable
Where eligibility/verification is required, systems MUST publish what the person must prove, what the state already holds, and the time/cost/interaction burden; default to “once-only” and burden‑minimizing design.
- **Canonical anchors:** `47-service-catalog-and-access-journeys-register.md`, `44-identity-credential-and-eligibility-systems-register.md`, `29-permissioning-and-approvals.md`, `81-verification-inspection-and-compliance-ladders.md`, `82-service-standards-and-minimum-service-guarantees.md`, `31-records-foi-and-government-memory.md`.
- **Source:** `../sources/claude-feedback/rev142/feedback-from-claude-05-persons-path.md` §20c.

### NR-07 — Error correction must propagate
If a record is corrected, dependent systems MUST update, and the person must be notified of downstream effects; “fix it here, still denied elsewhere” is a governance failure mode.
- **Canonical anchors:** `70-interoperability.md`, `31-records-foi-and-government-memory.md`, `44-identity-credential-and-eligibility-systems-register.md`, `98-persons-path-and-accessibility-invariants.md`.
- **Source:** `../sources/claude-feedback/rev142/feedback-from-claude-05-persons-path.md` §20d.

### NR-08 — Fear/retaliation is a first-order constraint
Remedy, whistleblowing, and oversight channels MUST account for retaliation risk; designs MUST include anti‑retaliation safeguards and monitoring, and provide safe channels for those at risk.
- **Canonical anchors:** `83-whistleblowing-and-protected-disclosures.md`, `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md`, `03-metrics-and-evidence.md` (retaliation metric).
- **Source:** `../sources/claude-feedback/rev142/feedback-from-claude-05-persons-path.md` §20e.

### NR-09 — Authority clarity: lanes must disclose whether they can bind
Appeal/redress routes MUST disclose their authority (binding vs advisory); “file here” without power semantics is legibility theater.
- **Canonical anchors:** `36-appeal-lanes-and-redress-registry.md`, `31-records-foi-and-government-memory.md`, `08-remedy-and-grievance.md`.
- **Source:** `../sources/claude-feedback/rev142/feedback-from-claude-05-persons-path.md` §20f.

### NR-10 — “No category fit” must not erase the person
Systems MUST include an explicit residual path when a person does not fit predefined categories (authorized human adjudication + reasoned receipt + measurable “edge review”).
- **Canonical anchors:** `47-service-catalog-and-access-journeys-register.md`, `82-service-standards-and-minimum-service-guarantees.md`, `12-identity-and-recognition.md`.
- **Source:** `../sources/claude-feedback/rev142/feedback-from-claude-05-persons-path.md` §20h.

### NR-11 — Indifference boundary: “correct-but-harmful” outcomes must route to systemic change
When rules operate as written yet produce harmful outcomes, governance MUST make the pattern legible and route it into systemic redress and rule/policy change participation (not endless individual appeals).
- **Canonical anchors:** `76-systemic-redress-and-pattern-remediation.md`, `41-public-participation-and-deliberation-register.md`, `08-remedy-and-grievance.md`.
- **Source:** `../sources/claude-feedback/rev142/feedback-from-claude-05-persons-path.md` §20g.

### NR-12 — Those who cannot contest need structural representation
High-stakes systems MUST provide accessible representation paths for people who cannot safely/self‑advocate (children, detained people, disability/language barriers) **and for communities facing collective harms** (collective filing + recognized representatives).
- **Canonical anchors:** `98-persons-path-and-accessibility-invariants.md`, `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md`, `47-service-catalog-and-access-journeys-register.md`, `44-identity-credential-and-eligibility-systems-register.md`, `82-service-standards-and-minimum-service-guarantees.md`, `41-public-participation-and-deliberation-register.md`.
- **Source:** `../sources/claude-feedback/rev142/feedback-from-claude-07-material-world.md` §31; `../sources/claude-feedback/rev142/feedback-from-claude-06-resistance-hope-community.md` §25.

### NR-13 — Material substrate: governance requires a floor
MUST-level requirements must disclose staffing/budget/time assumptions, degraded modes, and “salvage core” obligations when systems collapse (including offline, non-reading, and continuity of records).
- **Canonical anchors:** `09-public-service-and-state-capacity.md`, `80-implementation-roadmap.md` (Phase −1), `31-records-foi-and-government-memory.md`, `96-archive-governance.md` (material floor disclosure).
- **Source:** `../sources/claude-feedback/rev142/feedback-from-claude-07-material-world.md` §30–§32.

### NR-14 — Joinability is not justice (avoid join-key sprawl)
Interop and join-keys MUST be justified by a use-path that yields corrective action for the person; do not add join surfaces just because they are technically elegant. **Convention:** memos that introduce or depend on joins/IDs/data sharing must include a one‑line `**Join constraints:**` field near the top (see `96`).
- **Canonical anchors:** `70-interoperability.md`, `33-data-protection-and-personal-data-governance.md`, `44-identity-credential-and-eligibility-systems-register.md`, `42-automated-decision-systems-and-model-registry.md`, `96-archive-governance.md` (join constraints rule), `99-protective-legibility-and-adoption-dynamics.md`, `93-tax-and-revenue-administration.md`, `67-migration-and-mobility-governance.md`, `64-social-protection-and-benefits-governance.md`, `22-public-integrity-and-procurement.md`.
- **Source:** `../sources/claude-feedback/rev142/feedback-from-claude-07-material-world.md` §34.
### NR-15 — Version semantics: “as-of” must be answerable
Joinable artifacts (rules, registers, models, decisions) MUST support point‑in‑time semantics so a person can contest “what was true when I was decided upon.”
- **Canonical anchors:** `31-records-foi-and-government-memory.md` (Decision Receipt minimum fields), `70-interoperability.md`, `73-assurance-case-and-governance-safety-case.md`, `51-release-registry.md`, `96-archive-governance.md` (as-of + receipts rules).
- **Source:** `../sources/claude-feedback/rev142/feedback-from-claude-03-tensions-and-architecture.md` §13c.

### NR-16 — Accountability infrastructure must preserve mercy
Designs MUST keep bounded discretion/exception paths structurally possible and auditable (so mercy is possible without favoritism and cruelty cannot hide as procedure).
Operationalization: hard-edge interfaces should include a one-line `**Mercy / interim protection:**` field (waiver/exception + stay/interim relief triggers) per `96`.
- **Canonical anchors:** `85-waivers-variances-and-exceptions-discipline.md`, `82-service-standards-and-minimum-service-guarantees.md`, `96-archive-governance.md` (hard-edge memo rule), `01-principles.md`
- **Source:** `../sources/claude-feedback/rev142/feedback-from-claude-08-final-words.md` §37.

### NR-17 — Culture and relational infrastructure are real constraints
Legitimacy requires dignity/voice and relational capacity; designs SHOULD include emotional/relational infrastructure obligations (not only informational interfaces), and treat culture as a limit on purely structural solutions.
- **Canonical anchors:** `09-public-service-and-state-capacity.md`, `98-persons-path-and-accessibility-invariants.md`, `82-service-standards-and-minimum-service-guarantees.md`, `47-service-catalog-and-access-journeys-register.md`.
- **Source:** `../sources/claude-feedback/rev142/feedback-from-claude-02-culture-capacity-ai.md` §10; `../sources/claude-feedback/rev142/feedback-from-claude-07-material-world.md` §32b.

### NR-18 — Archive self-application (mirror test)
Treat edits to this archive (and AI governance proposals) as governance acts: avoid silent drift; preserve contestability; do not smuggle personhood claims into tool governance. When AI mediates the citizen–state interface or upstream decisioning, treat it as a rights-affecting interface that must be inventoried/versioned and routed to recourse.
- **Canonical anchors:** `96-archive-governance.md`, `06-digital-and-algorithmic-governance.md`, `42-automated-decision-systems-and-model-registry.md`.
- **Source:** `../sources/claude-feedback/rev142/feedback-from-claude-09-what-i-see.md` §43; `../sources/claude-feedback/rev142/feedback-from-claude-06-resistance-hope-community.md` §26; `../sources/claude-feedback/rev142/feedback-from-claude-02-culture-capacity-ai.md` §9a–§9c.

### NR-19 — Deprecate feedback (no feedback doctrine)
External feedback is an input to refactoring, not a permanent archive layer; integrate or reject with reasons, then delete the vendored corpus once citations retire.
- **Canonical anchors:** `100-claude-feedback-integration-tracker.md`, `96-archive-governance.md`, `../sources/claude-feedback/rev142/README.md`.
- **Source:** `../sources/claude-feedback/rev142/feedback-from-claude-03-tensions-and-architecture.md` §14b.

### NR-20 — Resist adding (stay small; interfaces over interiors)
Default to interfaces, obligations, and failure modes rather than long interior process descriptions; avoid country-specific guides, tech prescriptions, and sprawling private-governance redesign.
- **Canonical anchors:** `96-archive-governance.md` (resist adding + density budget), `02-design-toolkit.md` (primitive-first).
- **Source:** `../sources/claude-feedback/rev142/feedback-from-claude-01-structural.md` §6; `../sources/claude-feedback/rev142/feedback-from-claude-07-material-world.md` §34.

---

## Open integration work (use this to steer future turns)
- Replace remaining direct citations to `sources/claude-feedback/rev142/…` with citations to **canonical internal anchors** (often `96`, `98`, `70`, `31`, `08`, `36`, `99`) so the feedback folder can be deleted without losing traceability.
- Where multiple memos encode the same norm, prefer refactoring into one canonical home + cross-links (see `96` refactoring rules).