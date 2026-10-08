# 152 — Algorithmic Impact Assessment and Public AI Governance

**Purpose:** make algorithmic/AI use by public authority *contestable by design* by requiring a **joinable impact assessment + monitoring plan** for any automated or algorithmically assisted decision that can materially affect a person’s rights, resources, liberty, or safety.

This memo is a bridge between:
- `146-ai-assurance-and-public-sector-ai-ops.md` (run-time discipline: no-silent-swap, incident loop),
- `73-assurance-case-and-governance-safety-case.md` / `139-risk-and-safety-assurance-governance.md` (assurance-case spine), and
- `31-records-foi-and-government-memory.md` / `36-appeal-lanes-and-redress-registry.md` (receipts + remedy).

It treats “AI in government” as a **governance infrastructure** problem, not a tech procurement problem.

**Evidence anchors:** Canada’s Algorithmic Impact Assessment (AIA) tool and its role under the Directive on Automated Decision-Making (`[BIB-CAN-AIA]`, `[BIB-CA-ADM]`); NIST AI RMF lifecycle functions (`[BIB-NIST-AIRMF]`); the EU AI Act as product-safety + lifecycle control for AI systems (`[BIB-EU-AIACT]`); OECD AI principles (`[BIB-OECD-AI]`).

**See also:** `173-ai-standards-and-regulatory-mapping.md` (joinable compliance mapping)

---

## Design claim

**If an algorithm changes what a person can do, receive, keep, or appeal, then the system MUST publish a joinable impact assessment and MUST run a monitoring loop.**

The assessment is not PR. It is a *machine-readable* record that:
- binds the deploying institution to claims (purpose, legal authority, performance envelope),
- defines who gets harmed by error and how that harm is mitigated, and
- exposes the remedy lane in the same namespace as decisions.

---

## AIA as a first-class public artifact

Define a canonical artifact:

- `AIA-*` — **Algorithmic Impact Assessment record** (public by default; redact only the minimum needed for safety/abuse prevention).

`AIA-*` MUST be referenced by:
- the relevant `AIS-*` (system inventory record) (`146`), and
- any downstream `DRR-*` Decision Receipt that relied materially on the system.

### Minimum fields for `AIA-*`

`AIA-*` MUST include:
1. **Identity + ownership:** system name, version, operator, accountable official, vendor(s), procurement identifier(s) (`REL-*` join), and contact point.
2. **Decision scope:** what decisions are made or influenced; whether the output is binding/recommendatory; and where humans can override.
3. **Legal authority:** the statute/rule(s) this system implements; which rights/resources are at stake.
4. **Affected people map:** populations impacted, disproportionate impact risks, and language/accessibility constraints (tie to `98-persons-path-and-accessibility-invariants.md`).
5. **Data map:** primary data sources, data provenance, access/sharing logs expected (`127-data-governance-and-privacy-interfaces.md`), and retention rules.
6. **Risk tier + rationale:** explicit tiering and why; list the risk drivers (scale, irreversibility, vulnerability, coercion).
7. **Performance envelope:** what “good” means, what failure looks like, and where the system MUST NOT be used.
8. **Contestability commitments:** how a person can learn the role the system played, request correction, and appeal with deadlines (join to `AL-*` lanes in `36`).
9. **Monitoring plan:** what is monitored, at what frequency, with what triggers, and who reviews (see “post-deployment loop”).
10. **Change control rule:** what constitutes a material change requiring re-assessment (no-silent-swap).

**Implementation note:** Canada’s AIA is explicitly a questionnaire used to determine an impact level and requires mitigations (`[BIB-CAN-AIA]`, `[BIB-CA-ADM]`). Treat that model as a reusable baseline, but ensure this archive’s joinability constraints are met.

---

## Risk tiers and scope-fit

Risk tiers are an enforcement aid: they determine *which* controls are mandatory.

AIA tiering SHOULD be compatible with multiple regimes, e.g.:
- **Canada ADM** risk/impact levels (`[BIB-CAN-AIA]`, `[BIB-CA-ADM]`),
- **EU AI Act** risk-based obligations and lifecycle controls (`[BIB-EU-AIACT]`), and
- a voluntary lifecycle control model like **NIST AI RMF** (GOVERN/MAP/MEASURE/MANAGE) (`[BIB-NIST-AIRMF]`).

### Tier-to-control mapping (tight default)

- **Tier 0 (low materiality):** publish `AIS-*`; `AIA-*` MAY be short-form.
- **Tier 1 (moderate):** require `AIA-*` + public model/system card + periodic monitoring report.
- **Tier 2 (high):** require independent pre-deployment review, red-team, and an assurance-case excerpt; stricter appeal protections.
- **Tier 3 (highest / coercive / liberty / essential services):** require *independent* certification/approval, continuous monitoring, incident reporting, and strong interim protections during appeal.

`146` already defines “no silent swap” change control; higher tiers MUST tighten the definition of “material change” and shorten re-approval clocks.

---

## Post-deployment loop (monitoring, incidents, and recourse)

An AIA without monitoring is a one-time performance.

For Tier 1+ systems, the operator MUST run:
- **Monitoring:** drift, error rates, subgroup performance, complaint signals, override rates, and safety envelope violations.
- **Incident handling:** log harms and near-misses to `AIIR-*` (from `146`) and publish a public incident summary when it affected people.
- **Remedy linkage:** ensure every impacted person can reach an `AL-*` lane with interim protection where delay is harm (`36`, `98`).

The monitoring plan SHOULD use the NIST AI RMF lifecycle frame (govern/map/measure/manage) as a checklist for “what exists and who is responsible” (`[BIB-NIST-AIRMF]`).

---

## Procurement boundary clauses (stop governance-by-vendor)

Any contract for a Tier 1+ system MUST include:
- **Artifact obligations:** vendor must provide documentation needed for `AIA-*`/`AIS-*`/`AICR-*` and must support public disclosure with narrow redactions.
- **Audit + test rights:** government (and designated independent auditors) can test, inspect, and reproduce key claims.
- **No silent swap:** model updates, retrains, feature changes, and dependency changes require notice + change receipt + (for higher tiers) approval (`146`).
- **Exit + portability:** data, configs, and documentation to migrate without losing continuity.

(Join to `138-public-investment-and-capital-projects-integrity.md` for change-control discipline and to `31` for records custody.)

---

## Failure modes (what to watch for)

- **AIA-as-theater:** long documents that do not bind decisions, lack joins, and cannot be tested.
- **“Human in the loop” fiction:** humans rubber-stamp; override is discouraged; accountability is unclear.
- **Opacity-by-IP:** procurement uses trade-secret claims to block reasons/appeals.
- **Silent scope creep:** system shifts from “assist” to “decide,” or expands to new populations without re-assessment.
- **Monitoring without consequence:** dashboards exist but do not trigger remedy, rollback, or suspension.

Countermeasures:
- `AIA-*` MUST include enforceable triggers (suspend/rollback thresholds) and the authority who can execute them.
- Missing required artifacts are governance incidents (see `00-README.md` “Absence is a signal”).

---

## Integration points

- **Decision receipts:** `DRR-*` MUST indicate when a Tier 1+ system materially contributed and MUST link to the `AIA-*` and relevant `AIS-*`.
- **Appeals:** `AL-*` lanes MUST have an “algorithmic assist” path: obtain explanation, request correction, and contest the model’s role.
- **Records:** custody and retention of training/decision logs MUST be explicit; absence triggers incidents (`31`).
- **Public reporting:** publish a catalog of `AIS-*` + `AIA-*` with a stable identifier scheme (`70`, `128`).

---

## Minimal starter (if you can only ship one thing)

Ship a **short-form `AIA-*` + `AIS-*`** for the *single highest-harm* automated decision in your system, plus:
- a Decision Receipt that links to it (`DRR-*`),
- a reachable appeal lane (`AL-*`), and
- a monitoring trigger that forces review if complaints spike.

Then iterate outward.
