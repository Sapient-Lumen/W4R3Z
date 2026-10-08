# Constitutional Maintenance & Amendment Ops (Continuous Foundational Change Control)

**Merge relation:** periodic constitutional maintenance and review-operations memo. Use `206-constitutional-change-and-amendment-rails.md` as the canonical front door for concrete change packets, thresholds, anti-bundling, and amendment-event discipline; use `288-constitutional-change-maintenance-and-review-stack-guide.md` for cluster routing; this memo remains the standing maintenance/docket layer.


**Purpose:** treat constitutions/charters as **safety‑critical systems** that require *maintenance loops* and *change control*—so foundational rules can adapt without letting incumbents rewrite the game mid‑match.

**Person served:** anyone living under constitutional power who needs the foundational rules to be *stable enough to rely on* but *changeable enough to repair injustice*—with protection against capture and “emergency” opportunism.

**From-below:** this memo specifies *how people can propose, review, and ratify* foundational changes without insider access—and how to block bad-faith amendments.

**See also:** `124-constitutional-amendment-and-entrenchment.md` (procedural integrity), `118-rulemaking-and-change-control.md` (versioning patterns), `156-judicial-systems-and-constitutional-review.md` (legality backstop), `143-deliberative-systems-and-citizens-assemblies.md` (deliberation infrastructure), `112-exception-control-and-emergency-powers.md` (derogation rails), `308-peaceful-transfer-of-power-caretaker-government-and-continuity-of-office-rails.md` (transfer / caretaker / continuity seam).

---

## Design claim

Constitutions “fail” in two symmetric ways:

1) **Brittle entrenchment:** injustice persists because change is impossible without rupture.
2) **Soft capture:** change is easy *for incumbents* (or for organized minorities) to entrench advantage.

So the goal is **continuous constitutional maintenance**: a routine, contestable pipeline that makes *good change easier* and *bad change harder*.

Evidence anchors: constitutional endurance patterns and “amendment culture” matter, not just formal rules. See [BIB-EGK-ENDURANCE-2012], [BIB-GM-AMENDCULTURE-2015]. For procedural safeguards on amendments and referendums, see [BIB-VENICE-CONST-AMEND-2010], [BIB-VENICE-REFERENDUM-2022].

---

## Minimum viable maintenance system

### 1) A standing “review docket” (not a once‑per‑crisis scramble)

A constitution SHOULD have a **scheduled review lane** (e.g., every 8–12 years) that produces:
- a public **Constitution Review Docket (CRD)**: problems, proposals, tradeoffs, and implementation risks,
- a transparent **agenda‑setting rule** for what reaches the docket (signature thresholds + minority docket rights),
- an *explicit non‑agenda* list (what was proposed but declined, and why).

This is maintenance, not coup theater.

### 2) A two‑track proposal pipeline (repair vs redesign)

**Track A — Repair:** narrow fixes (rights clarifications, institutional bug‑fixes).
**Track B — Redesign:** structural moves (new veto points, new chambers, major jurisdiction shifts).

Tracks MUST have different scrutiny and ratification thresholds; structural redesign needs higher barriers and deeper analysis.

### 3) Amendment impact assessment (foundational “AIA”)

Before any vote/ratification, publish an **Amendment Impact Assessment (AIA)** that:
- states the **problem claim** and who is harmed today,
- enumerates plausible **abuse modes** (how incumbents could exploit the change),
- maps **cross‑scope joins** (what breaks at local/regional levels),
- lists **migration/transition rules** (how existing cases/rights carry over),
- includes a **sunset or review trigger** for risky changes.

### 4) Ratification with asymmetric protection

Foundational change MUST protect minorities and future persons from “winner‑take‑all” rewriting:
- require **time separation** (proposal → public review → vote) to reduce flash capture,
- require **anti‑gerrymander / anti‑coercion** controls for any referendum,
- require **judicial pre‑review** of process legality (not substance) where available.

(Details are in `124` + Venice Commission guidance.)

---

## Citizens’ assemblies as maintenance tooling (not substitute legislature)

A citizens’ assembly can be a **legitimacy amplifier** for contested issues when it is:
- properly **random‑selected with stratification** + independent selection audit,
- supported for participation (time, care, safety, translation),
- given balanced **briefing provenance** and adversarial review,
- linked to a **binding response rail** (parliament must publicly respond).

The Irish experience is a useful reference point for the assembly→referendum pipeline, while also illustrating that assemblies do not guarantee adoption. See [BIB-IRL-CA-ABORTION-2018], [BIB-IRL-CA-ABORTION-2018].

---

## Anti-capture rails for amendment moments

Amendment windows are **high‑risk**. Add rails:

- **No silent swap:** every text change gets a versioned diff and a plain‑language “what changes for you” summary.
- **Entrenchment smell test:** flag amendments that weaken oversight, courts, media, elections, or access to remedy.
- **Emergency amendment lock:** amendments during declared emergencies SHOULD be prohibited or require supermajority + post‑emergency re‑ratification.
- **Finance integrity:** require disclosure of major funding and influence for amendment campaigns (tie into `120`/`161`).

---

## Operational artifacts (keep them small)

- **CCR — Constitutional Change Receipt:** a single stable record pointer for each amendment attempt: text diff, sponsors, timeline, AIA, campaign disclosures, outcomes.
- **CRD — Constitution Review Docket:** periodic docket bundle; includes non‑agenda and minority reports.
- **ACI — Amendment Culture Indicator (watchdog metric):** not a target—an early warning of chronic churn or chronic blockage (treat as *diagnostic only*, per `03-metrics-and-evidence.md`).

---

## Test hooks (for `107-governance-test-suite.md`)

A maintenance system is failing if any of these are false:

- **T-CCR:** any person can find the current text + diffs + rationale + next steps for proposed changes.
- **T-AIA:** every proposal has an abuse-mode analysis and transition rules.
- **T-TIME:** proposals cannot be ratified without minimum deliberation time + publication windows.
- **T-MINORITY:** minority docket rights exist and produce visible outputs.
- **T-EMERG:** emergencies cannot be used to permanently rewrite foundational rules without post‑hoc re‑ratification.
