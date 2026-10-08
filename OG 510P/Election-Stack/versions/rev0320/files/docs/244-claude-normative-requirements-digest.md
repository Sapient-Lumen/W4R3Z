# 244. Claude normative requirements digest (non‑negotiables)

**Track:** Shared

This document is a **compact restatement** of the *normative* (must/should) requirements introduced by the preserved feedback artifact:
`evidence/feedback/claude-opus4_6-feedback_2026-02-27.md`.

**Size discipline:** this digest does **not** copy feedback text. Treat the feedback artifact as the authoritative source; treat this file as a
maintainer-facing *checklist* for coherence.

## How to use

- If you change the archive in a way that might weaken one of these requirements, write an ADR and add an explicit risk acceptance note.
- Each requirement points to its **canonical implementation surface(s)** (where the archive “actually enforces” the requirement).

## Normative requirements (Claude → archive)

### NR‑01 — Mission discipline over specification theater
The archive exists to make contested outcomes **resolvable by portable evidence**. New schemas/evidence objects MUST name the plausible dispute they serve (one sentence) and map into claim→PO→evidence.
If a checklist is never drilled, it is not a capability.

**Canonical surfaces:** `README.md` (mission discipline), `docs/227-refactor-and-growth-protocol.md` (size discipline + dispute-justified schemas), `docs/150-maintainer-bootstrap-and-change-protocol.md` (150.7 coherence gate), `artifacts/checklists/catastrophe-ordering-review-checklist.md` (§6 evidence-object gate), `docs/86-exercises-and-gamedays-program.md`.

---

### NR‑02 — Humans adopt this under crisis; provide strict entry paths
Adopters are humans under time pressure, not machines. Provide a strict “read these first” path that works in ~60 minutes, and briefing artifacts.

**Canonical surfaces:** `README.md` (60‑minute path), `docs/START_HERE.md`, `docs/242-audience-reading-paths-and-what-to-ignore.md`,
`artifacts/templates/adopter-briefing.md`, `artifacts/templates/adopter-slide-deck-outline.md`,
`CHECK:artifacts/checklists/adopter-60-minute-path-smoke-test.md`, `artifacts/registries/adopter-path-smoke-tests.csv`,
enforcement gates: `docs/150-maintainer-bootstrap-and-change-protocol.md` (§150.7), `artifacts/checklists/catastrophe-ordering-review-checklist.md` (§6).

---

### NR‑03 — “Evidence exists” is not enough; evidence must be *usable*
Evidence must be packaged so it can be consumed in dispute lanes (courts, oversight hearings, independent verification), including admissibility
and documentation constraints.

**Canonical surfaces:** `docs/43-evidence-bundles-and-court-proofing.md`,
`artifacts/templates/jurisdictional-admissibility-matrix.md`,
`artifacts/registries/admissibility-jurisdiction-index.csv` (bounded planning index),
`artifacts/templates/court-admissibility-worksheet.md`,
`docs/176-canonicalization-and-signing-rules-for-evidence-envelopes.md`,
`docs/150-maintainer-bootstrap-and-change-protocol.md` (150.7 dispute-lane gate),
`artifacts/checklists/catastrophe-ordering-review-checklist.md` (§6 dispute-lane gate).

---

### NR‑04 — Design for institutional volatility and minimal‑effort compliance
Assume “legibility theater” is possible: requirements may be satisfied *technically* while being undermined operationally.
Design so minimal‑effort compliance is still useful; missed deadlines and missing packets must become checkable evidence.

**Canonical surfaces:** `docs/187-publication-compliance-and-coverage.md` (MAPT),
`docs/181-publication-contract-and-deadline-breach-proofs.md`,
`docs/210-liveness-beacons-and-missingness-surface.md`,
`artifacts/registries/mapt-evaluations.csv` (bounded MAPT results log),
maintainer enforcement `docs/150-maintainer-bootstrap-and-change-protocol.md` (§150.7),
change-review enforcement `artifacts/checklists/catastrophe-ordering-review-checklist.md` (§6),
hazard register `HZ‑027`.

---

### NR‑05 — Size discipline is a security property
Archive growth is a risk. Keep a bounded outside‑view map, consolidate indexes, and avoid duplicative copies of the same content.

**Canonical surfaces:** `docs/242-audience-reading-paths-and-what-to-ignore.md`,
`docs/13-artifact-index.md`,
`docs/227-refactor-and-growth-protocol.md`,
`FEEDBACK_INTEGRATION_LEDGER.md`.

---

### NR‑06 — Treat the voter as a person; name the representation duty and material floor
Voters must not appear only as threat‑model personas. The archive must include a human verification story, the role of representatives
(monitors/witnesses), and what happens when devices/internet/literacy are absent (paper + observers).

**Canonical surfaces:** `docs/track-a/PERSONS_PATH.md`, `docs/track-a/VOTER_VERIFICATION.md`,
`docs/91-public-verification-and-observer-kit.md`, `artifacts/templates/witness-profile.md`,
`docs/131-monitor-accountability-and-public-inspections.md`, `docs/135-witness-governance-incentives-and-capture-resistance.md`,
`docs/track-a/PILOT.md`.

---

### NR‑07 — Drill the human process under overload and political pressure
The hardest failures are social: conflicting reports, forged statements, and pressure to publish prematurely. Drills must exercise these conditions.

**Canonical surfaces:** `docs/86-exercises-and-gamedays-program.md`, `docs/90-exercise-scenario-library.md`,
`artifacts/registries/drill-scenarios.csv`,
`artifacts/registries/drill-runs.csv`,
`artifacts/checklists/authenticity-response-cell-checklist.md`,
`artifacts/templates/after-action-report.md`.

---

### NR‑08 — Supply chain transparency expectations must be explicit
Track A may wrap proprietary systems, but must say what opacity it cannot eliminate and how evidence value depends on system transparency.

**Canonical surfaces:** `docs/track-a/README.md`, `docs/track-a/PILOT.md`,
`docs/track-c/README.md`, `artifacts/templates/procurement-language.md`.

---

### NR‑09 — The archive can be wrong; provide a bounded external challenge loop
Treat “spec error” as a first‑class hazard with a minimal response loop and a repeatable external review capability.

**Canonical surfaces:** `docs/243-archive-self-threat-model-and-spec-correctness.md`,
`artifacts/checklists/external-review-session-checklist.md`,
`artifacts/registries/external-review-log.csv`,
`artifacts/templates/external-challenge-report.md`,
`artifacts/playbooks/spec-error-response-playbook.md`,
hazard register entries (e.g. `HZ‑024`).
---

### NR‑10 — The witness ecosystem is load‑bearing; design for capture and bootstrapping
Technical evidence is only useful if independent witnesses/monitors exist and behave honestly.
Name bootstrapping assumptions, detect partial capture behaviorally, and track witness “health” over time.

**Canonical surfaces:** `docs/135-witness-governance-incentives-and-capture-resistance.md`,
`docs/139-ct-policy-inspired-admission-and-removal.md`,
`artifacts/templates/witness-profile.md`,
`artifacts/registries/witness-health-log.csv` (bounded health signals),
`artifacts/checklists/witness-ops-checklist.md`,
`artifacts/checklists/witness-rotation-execution-checklist.md`,
maintainer enforcement `docs/150-maintainer-bootstrap-and-change-protocol.md` (§150.7),
change-review enforcement `artifacts/checklists/catastrophe-ordering-review-checklist.md` (§6).

---

### NR‑11 — The deepfake frontier demands measurable time‑to‑refute
The archive must treat authenticity disputes as time‑critical and operationally measurable (time‑to‑refute), not just as cryptographic theory.

**Canonical surfaces:** `docs/240-deepfake-frontier-and-time-to-refute.md`,
`docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`,
`docs/86-exercises-and-gamedays-program.md`,
`artifacts/templates/time-to-refute-test-plan.md`,
`artifacts/checklists/authenticity-response-cell-checklist.md`,
`artifacts/checklists/time-to-refute-refutation-packet-checklist.md`,
`artifacts/registries/time-to-refute-evaluations.csv`,
`docs/150-maintainer-bootstrap-and-change-protocol.md` (150.7 gate),
`artifacts/checklists/catastrophe-ordering-review-checklist.md` (§6).


---

### NR‑12 — Coercion is a human dignity problem, not only a crypto property
Non‑claims and deployment guidance must describe the *person’s experience* under coercion and failure modes, and require honest supervision postures.

**Canonical surfaces:** `docs/167-non-claims-and-boundaries.md` (coercion boundary notes),
`artifacts/playbooks/coercion-response-playbook.md`,
`docs/07-coercion.md`.

---

### NR‑13 — Promotion protocol must have a political immune system
Any promotion that introduces remote ballot return into a Track A candidate MUST include: independent security review, adversarial review of the
public non‑claims statement, and a published rollback plan. No silent scope creep.

**Canonical surfaces:** `docs/229-experiment-to-spec-promotion-protocol.md`,
`docs/166-scope-and-claims-contract.md`, `docs/167-non-claims-and-boundaries.md`,
`artifacts/checklists/catastrophe-ordering-review-checklist.md` (§1.5), `artifacts/templates/procurement-language.md` (§10),
`artifacts/registries/promotion-events.csv` (bounded decision log),
hazard register `HZ‑025`, drill scenario `premature_promotion_remote_return`.

---

### NR‑14 — A checklist is not a capability unless it is drilled
If an operational checklist, playbook, or “minimum posture” is never exercised under overload and political pressure, it is not a capability.
New operational surfaces should come with at least one drill scenario and a publishable after‑action artifact.

**Canonical surfaces:** `docs/86-exercises-and-gamedays-program.md`, `docs/90-exercise-scenario-library.md`,
`artifacts/registries/drill-scenarios.csv`,
`artifacts/registries/drill-runs.csv`, `artifacts/templates/after-action-report.md`,
`artifacts/checklists/catastrophe-ordering-review-checklist.md`, `docs/150-maintainer-bootstrap-and-change-protocol.md`,
`docs/227-refactor-and-growth-protocol.md`.
---

### NR‑15 — Accountable uncertainty replaces hedge-language in public comms
Public-facing statements and adopter-facing narrative docs MUST use explicit epistemic tags (`218`) and uncertainty-safe update mechanics (`219`).
Avoid bespoke hedge-language (e.g., “likely”, “appears”); if uncertainty exists, tag it and state what would change it.

**Canonical surfaces:** `docs/218-epistemic-status-tags-and-confidence-rubric.md`, `docs/219-uncertainty-safe-public-updates.md`,
`artifacts/templates/public-statement-template.md`, `artifacts/templates/incident-communications.md`,
`artifacts/checklists/public-update-epistemic-quickcheck.md`,
release-gate drift firewall `scripts/check_no_hedging_in_public_templates.py`,
maintainer enforcement `docs/150-maintainer-bootstrap-and-change-protocol.md` (§150.7),
change-review enforcement `artifacts/checklists/catastrophe-ordering-review-checklist.md` (§6).


---

### NR‑16 — Privacy vs verifiability: avoid turnout surveillance (turnout oracle)
Transparency surfaces MUST NOT become a turnout‑surveillance feed (who voted/when/where) via timing, geography, small batches, or joinability.
Track B work that touches eligibility/revocation transparency MUST define a metadata budget + batching rule, preserve private dispute lanes, and treat deanonymization risk as an incident (hazard **HZ‑026**).

**Canonical surfaces:** `docs/75-revocation-and-eligibility-transparency.md`, `docs/81-privacy-preserving-eligibility-token-minting-protocol.md`, `docs/172-open-research-questions-and-experiment-backlog.md` (172.3.1), `docs/167-non-claims-and-boundaries.md` (N‑2 privacy boundary note), `CHECK:artifacts/checklists/turnout-oracle-risk-quickcheck.md`, `artifacts/registries/turnout-oracle-risk-assessments.csv`, hazard register `HZ‑026`, enforcement gates: `docs/150-maintainer-bootstrap-and-change-protocol.md` (§150.7), `artifacts/checklists/catastrophe-ordering-review-checklist.md` (§6).
