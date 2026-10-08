# Rulemaking & Change Control (Power Moves Through Rule Versions)

**Purpose:** Treat rule changes (laws, regulations, policies, platform terms, models-in-production rules) as **power moves** that must be **versioned, legible, contestable, and reversible**.

**Person served:** someone whose rights/resources change because a rule changed—who needs a clear “what changed, why, when, and how to challenge it”.

**Design stance:** if the system cannot *explain and replay* the rule that governed an outcome, it is not rule‑of‑law compatible.

## Minimum artifacts (portable across scopes)

**(1) Rule Registry (`RR-*`)**
- A stable public index of in‑force rules with:
  - **Rule ID** (`RID-*`), scope/jurisdiction, owner, effective date, expiry/sunset date (if any), and bindingness level (law/reg/policy/contract/algorithmic policy).
  - **Machine- and human-readable text** (include an accessible summary).
  - **Link to change history** and **Decision/Reason references**.

**(2) Rule Change Receipt (`RCR-*`)**
Every rule change MUST produce a receipt that includes:
- `RID-*` (target rule), new `RID-*` (if renumbered), and **semantic version** (`vMAJOR.MINOR.PATCH`).
- **Diff** (what changed), **effective time**, **transition policy** (grandfathering, carve‑outs, staged rollout).
- **Reasons** (Decision Receipt link `DRR-*` / reason codes `RC-*`), and **authority** (who can change this).
- **Impact statement**: who is affected, what the new constraints/benefits are, and what remedies exist.
- **Contest window** and **standing** rules (who can challenge; where).
- **Rollback plan** (what triggers rollback; who can invoke it; interim protections).

**(3) Past-rule replay**
- MUST: for any rights-/resource-affecting decision, the Decision Receipt (`DRR`) references the **exact rule version** used.
- MUST: a person can request a **replay under the old rule** if the system applied the wrong version (see `115` record interfaces).

## Change control safeguards (anti-capture + anti-chaos)

**CC-1 Notice + response duty**
- SHOULD: publish proposed changes with a minimum comment window (scaled by risk).
- MUST: publish a **response taxonomy**: adopt / reject / adopt-with-changes / defer, each with reason receipts.

**CC-2 Risk-tiered gates**
- MUST: higher-risk changes (coercion, eligibility, surveillance, benefits/rights) require stronger gates:
  - independent review, red-team, rights impact, and explicit “why less restrictive options fail”.
  - tie into `112` (exception control) for emergency-only pathways.

**CC-3 Anti-retroactivity default**
- MUST: default **no retroactive detriment** (unless a rights-compatible exception is explicitly justified and contestable).
- SHOULD: if retroactivity is used, provide **automatic mitigation** and expedited review lanes.

**CC-4 Sunset + evaluation hooks**
- SHOULD: novel rules ship with a sunset date and an evaluation plan; renewals require a new `RCR-*`.
- Anchor to control loops (`104`) and test suite (`107`).

**CC-5 Seam continuity**
- MUST: when rule changes interact across jurisdictions/providers, preserve continuity:
  - transfer-of-file + non-reset evidence rules (`109`), and no ping‑pong dispute lane (`114`).

## Minimal metrics (publishable)
- Rule-change volume by domain and risk tier.
- Median time from proposal → decision, and from decision → effective date.
- % of changes with completed impact statement + rollback plan.
- Challenge rate and overturn rate (by domain).
- Retroactivity incidents (count; mitigations applied).

## References (citation keys)
- Administrative procedure / notice-and-comment baseline: **[BIB-US-APA]**.
- Regulatory policy / impact assessment practices: **[BIB-OECD-RP]**, **[BIB-EU-BETTER-REG]**.
- Rule-of-law health rubric: **[BIB-VENICE-ROL-2025]**.
