# Automated Decision Systems & Model Registry (ADS/MOD)

Public power becomes illegible when decisions are *mediated by systems* without a public inventory, versioning, and recourse. This memo defines a **minimal public register** for automated decision systems (ADS) used in rights-/resource-affecting contexts, and (optionally) a lightweight model registry for reusable/high-impact models.

**Anchors:** risk-based regulation and transparency expectations: see [BIB-EU-AIACT], [BIB-CA-ADM], [BIB-UK-ATRS], and risk management framing [BIB-NIST-AIRMF], [BIB-OECD-AI].; administrative-law framing: [BIB-ENGSTROM-HO-ALGOACC-2019].

---

## 1) Objects

### `ADS-*` (Automated Decision System)
A deployable system that *produces or materially influences* decisions, classifications, scores, priorities, or eligibility outcomes.

### `MOD-*` (Model component; optional but recommended)
A reusable high-impact model (or model family) used by one or more `ADS-*` systems (e.g., a credit-like score model reused across programs).

**Rule:** if a model is **reused across 2+ ADS** or is **high-stakes**, publish a `MOD-*` entry and link it from each `ADS-*`.

---

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
- **Availability:** public URL/API endpoint and retention window for prior versions (“as-of” lookup).

If `MOD-*` is used, each `ADS-*` SHOULD link: `MOD-*` + model version/hash + evaluation/monitoring pointer.

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
