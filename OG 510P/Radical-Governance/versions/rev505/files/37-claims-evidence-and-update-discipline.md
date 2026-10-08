# Claims, Evidence & Update Discipline (Making Decisions Falsifiable)

**Stack relation:** use `290-evidence-statistics-and-publication-integrity-routing-guide.md` for the canonical route across the evidence / statistics / publication-integrity cluster. This memo is the narrower claims, falsifiability, correction, and retraction layer inside that family; `03` is the measurement front door; `214` is the institutional evidence-system anchor; `28` handles program commitments; `184` handles official statistics; `202` handles evidence commons; `190` handles experimentation; `142` handles indicator governance; `51` / `53` handle publication objects and tamper-evident history.

**Purpose:** keep public claims correctable—require evidence, updates, and retractions so propaganda and “frozen lies” don’t become policy substrate.
**Person served:** a member of the public whose life is shaped by official claims who needs falsehoods corrected and policy justified by auditable evidence.

**From-below:** This stops agencies from repeating disproven claims by requiring evidence, updates, and corrections you can track and cite.
**EXP pointer:** counters `EXP-01` (Opacity) and `EXP-07` (Indifference) by forcing claims to be falsifiable and correction-capable (`98-persons-path-and-accessibility-invariants.md`).
**Join constraints:** any identifiers/joins/releases introduced here MUST follow `70-interoperability.md` (empowered use‑path + corrective action), stay purpose‑limited/minimized, and have a narrow alternative when joins are unsafe or missing (prefer person‑portable receipts/reference numbers or safe aggregates). (See `101-claude-rev142-normative-requirements.md` (NR-14).)
**Material floor (one sentence):** assumes capacity to maintain claim→evidence links and publish corrections/retractions; in degraded mode at least emit correction/retraction receipts that link to follow‑through lanes. (See `31`, `53`, `76`; `101-claude-rev142-normative-requirements.md` (NR-13, NR-07).)
**As-of & corrections:** any joinable artifacts introduced here MUST be versioned and “as‑of” answerable; corrections are append‑only and propagate across dependent systems via `31`/`53` and joins via `70` (no silent overwrites). (See `101-claude-rev142-normative-requirements.md` (NR-07, NR-15).)

Publishing data is not enough. (Legibility trap: transparency is necessary but not sufficient when power can ignore findings.) (See `101-claude-rev142-normative-requirements.md` (NR-02).) Governance fails when policies are **unfalsifiable** (“always working, just needs more time”) or when evidence is laundered through selective metrics.

This memo defines a *small* claim-and-evidence primitive that plugs into existing registers (`PROG`, `EVAL`, `REL`, `OFR`) and decision receipts (`DRR`).

**Anchor set (high-trust):**
- Magenta Book (UK central guidance on evaluation; updated 2025): see [BIB-UK-MAGENTA-2025].
- UK Government Evaluation Registry guidance (mandatory registration from 1 Apr 2024): see [BIB-UK-EVALREG-GUIDE].
- US Evidence Act summary (learning agendas / annual evaluation plans): see [BIB-US-EVIDENCEACT-EVALGOV].
- OECD cross-country view on ex post evaluation (Government at a Glance 2025): see [BIB-OECD-GAAG2025-EXPOST].

---

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** transparency can be weaponized; design disclosures and incentives accordingly. (`99-protective-legibility-and-adoption-dynamics.md`)
- **Person-facing stakes:** `98-persons-path-and-accessibility-invariants.md` (proof burdens; fear/retaliation; non-digital support).
- **Remedy loops:** `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md` (claims must connect to effective relief).
- **Records + receipts:** `31-records-foi-and-government-memory.md` (DRR/RC/AO joins).
- **Publication discipline:** `51-release-registry.md` (REL-*; methods; point-in-time).
- **Assurance-case framing:** `73-assurance-case-and-governance-safety-case.md` (claims must state falsifiers and update triggers).

## Named tensions (design must surface these)
- **Evidence vs dignity:** verification can become cruelty; minimize repeated proof and measure burden (`98`).
- **Speed vs rigor:** fast updates help; rushed numbers become propaganda.
- **Transparency vs harm:** publish enough to be contestable without enabling targeting/retaliation (`99`, `77`).
- **Measurement vs gaming:** claims attract manipulation; design audits and falsifiers.

## A. The `CLM` object (testable claim)

A **claim** is a compact prediction: *if we do X, Y will change by ~Z for population P over time T* (including plausible harms). Claims MUST be versioned and linkable.

### Minimum fields (one screen)
```yaml
CLM-ID: CLM-____
TITLE: (short)
OWNER-UNIT: UNIT-____
APPLIES-TO: [PROG-____ | DRR-____] # at least one
POPULATION: (who)
INTERVENTION: (what action / rule / program feature)
OUTCOME: (what changes)
METRICS: [IPM-… | LRR-… | ECO-… | REL-…] # ≤3 preferred
BASELINE: {value: __, date_range: __, source: REL-…/URL}
TARGET-RANGE: {direction: up/down, magnitude: __, timeframe: __}
COUNTERFACTUAL: (what would have happened otherwise; identification sketch)
MECHANISM: (assumptions that must hold)
DISTRIBUTION: (who gains/loses; equity note)
HARMS-GUARDRAILS: (credible harms + guardrails/stop rules)
CONFIDENCE: (low/med/high + why)
EVIDENCE-DOCKET:
 - {type: REL|EVAL|OFR|EXT, id_or_url: __, quality: A|B|C, note: __}
REVIEW: (date/trigger that forces re-check)
STATUS: (proposed|active|supported|contested|falsified|retired)
VERSION: (vN + revision log pointer)
```

**Quality note:** `CONFIDENCE` is *not* “certainty.” It is a declared posture that can be audited against the docket and later outcomes.

**Person-facing guardrails (don’t forget the lived harms):** when a `CLM` touches rights or essential services, `HARMS-GUARDRAILS` SHOULD explicitly include delay/waiting harm, proof burden, retaliation/fear risk, and category‑exclusion risk—and point to measurable hooks (see `98-persons-path-and-accessibility-invariants.md`, `82-...`, `47-...`).
---

## B. Evidence docket rules (anti-laundering)

The docket is not a literature review; it is a **short list of what you are relying on**.

Minimum rules:
- **List the main evidence, including negative/contrary evidence** if known (even if you discount it).
- Tag evidence as:
 - `REL` (official data release/series),
 - `EVAL` (evaluation commitment/report),
 - `OFR` (oversight finding),
 - `EXT` (external study/report URL).
- Include a lightweight **quality grade**:
 - **A**: strong identification + transparent methods + reusable data where feasible.
 - **B**: informative but limited (partial identification, limited generalizability, weaker transparency).
 - **C**: plausibility / expert judgment / unverified vendor claims (allowed, but must be labeled as such).
- Disclose **conflicts** where material (vendor-funded studies, regulator capture risk).

---

## C. Update discipline (what makes this governance-grade)

1) **Pre-commit to “what would change our mind.”**
 Each major `CLM` MUST name a `REVIEW` trigger and a plausible *falsification condition* (guardrail / stop rule).

2) **Tie claims to registers.**
- A major program (`PROG`) SHOULD have ≥1 `CLM` and ≥1 evaluation commitment (`EVAL`) unless it is demonstrably low-stakes.
- Evaluation reports (`EVAL`) MUST cite the `CLM` IDs they tested (and what changed).

3) **Publish the response.**
 When an evaluation completes or a claim is falsified/contested, publish:
- a program revision (new `PROG` version) or a follow-on decision receipt (`DRR`) that records what changed and why, and
- an update to `CLM STATUS` (supported/contested/falsified/retired) with the evidence link.

4) **No silent rewrites.**
 `CLM` updates are versioned with an explicit revision log (see `IOP-9`).

5) **Metric lock (no goalpost shifts).**
- When a `CLM` declares `METRICS`, it SHOULD pin them to a specific `REL-*` series definition (method + revision policy), so later redefinitions are visible.
- Changing metrics, baselines, or targets requires a **new `CLM` version** that:
 - states the delta and why,
 - preserves the prior metric(s) for comparison for ≥1 review/evaluation cycle where feasible,
 - forbids declaring “success” solely on redefined metrics without showing the prior definition.

---

## D. Interfaces (where `CLM` gets used)

- **Program Register (`28-...`):** programs reference `CLM-*` IDs instead of embedding long narrative predictions.
- **Decision receipts (`DRR`):** where a decision asserts a prediction (or relies on evidence), cite the relevant `CLM-*` and `REL/EVAL/OFR` IDs.
- **Interoperability (`70-...`):** `CLM` is a join-key type; keep it small and stable.
- **Threat models (`04-...`):** treat evidence laundering as a first-class failure mode of epistemic systems.

---

## E. Minimal metric hooks (optional)
- **[IPM-11] Evidence coverage:** share of high-spend / rights-affecting programs with `PROG` + ≥1 `CLM` + ≥1 `EVAL` commitment.
- **[IPM-12] Follow-through:** share of completed `EVAL` reports that have a published response (`DRR` or `PROG` revision) within an agreed window.
