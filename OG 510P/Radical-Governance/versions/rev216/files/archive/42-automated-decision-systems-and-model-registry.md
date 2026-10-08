# Automated Decision Systems & Model Registry (ADS/MOD)

**Purpose:** inventory and version automated decision systems so their use is auditable, reason‑giving is possible, and people can reach recourse when systems err.

Public power becomes illegible when decisions are *mediated by systems* without a public inventory, versioning, and recourse. This memo defines a **minimal public register** for automated decision systems (ADS) used in rights-/resource-affecting contexts, and (optionally) a lightweight model registry for reusable/high-impact models.

**Scope note:** this registry covers AI/ADS as governance *tools* used to affect people’s rights/resources. If future systems become governed *participants*, treat their constraints as a rights-affecting interface requiring legible rules, reasons, and recourse (outside scope here).

**Anchors:** risk-based regulation and transparency expectations: see [BIB-EU-AIACT], [BIB-CA-ADM], [BIB-UK-ATRS], and risk management framing [BIB-NIST-AIRMF], [BIB-OECD-AI].; administrative-law framing: [BIB-ENGSTROM-HO-ALGOACC-2019].

---


## Kernel anchors (do not repeat)
- **AI as governance interface:** `06-digital-and-algorithmic-governance.md` (AI as tool + medium; citizen-side contestation).
- **Person-facing invariants:** `98-persons-path-and-accessibility-invariants.md` (no AI-only gate; safe contestation).
- **Receipts + reasons:** `31-records-foi-and-government-memory.md` (DRR fields; rule basis; what-next).
- **Remedy lanes:** `08-remedy-and-grievance.md`, ALR `36-...` (effective relief, not “review-only”).
- **Protective legibility:** `99-protective-legibility-and-adoption-dynamics.md` (auditability without exposure harm).

## Named tensions (design must surface these)
- **Auditability vs privacy/proprietary:** explain enough to contest; protect sensitive data and trade secrets with logged boundaries.
- **Automation vs discretion:** reduce arbitrariness without creating unreviewable rigidity.
- **Stability vs drift:** models change behavior; releases must be testable and comparable (`REL-*`).
- **Joinability vs justice:** linking decisions can expose people; default to least-joinable that still enables remedy.

## 1) Objects

### `ADS-*` (Automated Decision System)
A deployable system that *produces or materially influences* decisions, classifications, scores, priorities, or eligibility outcomes.

### `MOD-*` (Model component; optional but recommended)
A reusable high-impact model (or model family) used by one or more `ADS-*` systems (e.g., a credit-like score model reused across programs).

**Rule:** if a model is **reused across 2+ ADS** or is **high-stakes**, publish a `MOD-*` entry and link it from each `ADS-*`.

---

### AI-mediated interfaces (AI as governance medium)

When AI systems mediate the citizen–state interface (chatbots, eligibility “assistants,” appeal drafting tools offered by the state, automated notice generators), they shape access and outcomes even if they do not make the final decision.

**Rule:** if an AI-mediated interface materially influences a rights-/resource-affecting interaction, it MUST be registered as an `ADS-*` (or linked to the controlling `ADS-*`) and MUST:
- disclose that it is AI-mediated and its known limitations,
- preserve a human-authored pathway for rights-affecting interactions,
- treat AI-generated determinations/communications as requiring the same integrity controls as human ones (if it tells someone “ineligible,” that is a determination and should emit/point to a `DRR-*` receipt).

### AI in the hands of the governed (pro-contestation)
AI can strengthen the archive’s theory of change when used by citizens to understand rights, draft appeals, and analyze public data. Designs SHOULD keep public artifacts machine-readable where safe (`REL-*`, registers), while guarding against new capacity disparities.


## 2) Minimum public register fields (MVS)
Each `ADS-*` entry MUST publish, at minimum:

- **Identity:** `ADS-*` ID; name; owning `UNIT`; operator contact; vendors/contracts (`CON-*` when applicable).
- **What it does:** decision domain; affected population; whether it *decides*, *recommends*, or *triages*; known protected-class sensitivity.
- **Legal basis:** `RULE-*` IDs (**with version/as-of**) for authority + eligibility logic.
- **Inputs/outputs:** high-level feature/data sources; major data flows via `DPR-*`; output types (score, label, rank, recommendation).
- **Risk tier:** low / medium / high (local taxonomy allowed; MUST be stable and published).
- **Human review:** where humans can override; what “meaningful review” means operationally.
- **Contestability:** primary appeal lane(s) `AL-*` (from ALR `36-...`), including fast-track for high-stakes harms.
- **Reason codes:** required `RC-*` taxonomy mapping for explanation and audit (`70-...`).
- **Evidence status:** linked `CLM-*` claims and/or `EVAL-*` where outcome claims are made (`37-...`, `28-...`).
- **Versioning:** current system version; last materially significant change date; change-log pointer.
- **Behavioral test suite (for foundation models):** pointer to a fixed test set + the latest published results `REL-ADS-TEST-*` (because behavior can change without a clean “version”).
- **Availability:** public URL/API endpoint and retention window for prior versions (“as-of” lookup).

If `MOD-*` is used, each `ADS-*` SHOULD link: `MOD-*` + model version/hash + evaluation/monitoring pointer.

**No stable version note:** for foundation-model-based systems, treat *prompts, policy layers, and toolchains* as versioned configuration, and rely on published behavioral test releases (`REL-ADS-TEST-*`) in addition to version strings.

---

### Substantive notice + contestability (when a system is used against a person)
If an `ADS-*` system materially affects a person’s rights/resources, the person-facing notice/receipt (`DRR-*`) MUST include:
- the `ADS-*` (and `MOD-*` where applicable) identifiers **and versions**,
- the **role** of the system (decide / recommend / triage),
- a short **factors list** (“top reasons”) in plain language (not just a score), and
- the **appeal lane** (`AL-*`) and what evidence can change the outcome.

**When explainability is technically constrained:** require governance substitutes:
- independent performance and bias audits (publish summaries + methods; link as `REL/OFR`),
- override logging (human overrides and their rates are visible),
- stability constraints (model/version changes are logged; significant changes trigger review),
- a fallback path for essential services (no “ADS-only” access for `ESS-1` services).

**Minimum meaningful packet (even for opaque models):**
- decision threshold policy (what cutoffs or rank/queue rules were applied),
- factor categories + recourse: what kinds of evidence/actions can change the outcome,
- known error modes + monitoring indicators (at least one published quality/bias metric by cohort, privacy-safe).



## 3) Required joins for decisions (DRR rule)
If an `ADS-*` is used for a rights-/resource-affecting decision, the **Decision Record/Receipt** MUST include:
- `DRR` + `ADS-*` (and `MOD-*` when material)  
- `RULE-*` basis (version/as-of)  
- `RC-*` reason codes sufficient to contest the outcome  
- `AL-*` lane ID for appeal/remedy  

This is the “no silent algorithms” rule: a person must be able to *see the system, the rule basis, and the lane to challenge*.

---

## 4) Governance gates (risk-tiered)
- **Low risk:** publish `ADS-*`; basic QA; incident channel.
- **Medium risk:** add impact assessment; monitoring; periodic audit sampling.
- **High risk:** independent review/audit rights; red-team testing where appropriate; stricter change-control; mandatory fast appeal lane and human review SLA.

**Procurement rule:** contracts for `ADS`/`MOD` MUST include auditability, logging, portability/exit, and independent testing rights (tie to CPR `38-...` and integrity `22-...`).

---

## 5) Failure modes and mitigations
- **Vendor opacity / trade-secret veto** → procurement clauses; publish what can be published; independent escrow/audit; no-deploy if un-auditable.
- **Policy laundering (“the model decided”)** → DRR join rule + `RULE` basis; named accountable officer; override + sign-off logs.
- **Opaque/limited explainability** → publish the *policy layer* (thresholds, override rules, rebuttable factors) and **recourse categories**; require independent audit access under controlled conditions; publish redacted findings; log overrides and corrections so contestation can work in practice.
- **Drift and silent changes** → versioned `ADS`/`MOD` entries; change-log; revalidation triggers; incident register linkage.
- **Denial of remedy** → mandatory `AL-*` lanes, fast-track, and accessible explanations (`RC-*`).
- **Data function creep** → bind to `DPR-*` and purpose limitation; periodic review and deletion discipline.

---

## 6) Minimal templates (one-screen)
**ADS register entry skeleton (publishable):**
- `ADS-ID:`  
- `Name:`  
- `Owning UNIT:`  
- `Domain / decision role:` (decide / recommend / triage)  
- `Legal basis RULE(s):`  
- `Data flows DPR(s):`  
- `Risk tier:`  
- `Appeal lane(s) AL:`  
- `Reason codes RC taxonomy:`  
- `Vendors / CON:`  
- `Evidence links CLM/EVAL:`  
- `Current version + last material change:`  
- `Public URL/API + “as-of” access:`  

**MOD entry skeleton (optional):**
- `MOD-ID:`  
- `Used-by ADS:`  
- `Version/hash:`  
- `Monitoring / evaluation:`  
- `Known limitations / bias notes:`
