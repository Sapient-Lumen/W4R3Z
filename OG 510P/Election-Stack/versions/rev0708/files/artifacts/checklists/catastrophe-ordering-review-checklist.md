# Catastrophe ordering review checklist (C1..C5)

**Track:** Shared (cross-cutting)


Use this checklist when proposing a protocol/tooling change, adding a new public surface, or changing UX.
It keeps the archive’s priority ordering explicit and prevents “availability-first” instincts from silently
increasing worst-case outcome risk.

Reference: `artifacts/registries/catastrophe-classes.csv`.

## 1) Classify the *worst credible* failure
- ☐ If this change fails under active attack, what is the worst credible catastrophe class it enables (C1..C5)?
- ☐ Did we accidentally trade a loud failure (C4) for silent manipulation or ecosystem capture (C1/C2)?

## 1.5 Special gate — remote ballot return / other C1–C2 scope expansions (non‑waivable)
If this change introduces **remote ballot return** (or otherwise expands vote casting outside controlled polling places), treat it as a *promotion-under-pressure* risk.

- ☐ Confirm this is not silent Track B/C → Track A leakage (see `docs/229.7`).
- ☐ Require **independent security review** (not funded by deploying jurisdiction/vendor) with a publishable summary.
- ☐ Require **adversarial review of the public non‑claims statement** (skeptical posture; review for completeness, not endorsement).
- ☐ Require a **published rollback plan** with pre‑committed triggers/procedure returning to Track A paper‑first workflows.
- ☐ Update `docs/166` (claims) and `docs/167` (non‑claims) and repeat the boundary in operator/public comms.
- ☐ Record the above as release gates in an ADR and link the decision to hazard `HZ‑025`.
- ☐ Create/update a bounded row in `artifacts/registries/promotion-events.csv` capturing the guardrail evidence pointers + ADR ID (store only refs/digests).


## 2) C1 — Silent outcome manipulation
- ☐ Does any new trust or discretion point allow outcome-affecting changes without a portable proof of misbehavior?
- ☐ Is there an explicit evidence object that would be produced when the change fails (fork proof, drift proof, mismatch proof)?

## 3) C2 — Verification-ecosystem capture
- ☐ Does the change rely on a single monitor cohort, vendor, or channel (monoculture risk)?
- ☐ If the adversary shapes routing/cohorts (docs `127–130`), do we still have detectable anomalies (coverage reports, beacons, path correlation)?

## 4) C3 — Irrecoverable ambiguity
- ☐ Are we creating states where observers can no longer determine what happened (missing receipts, missing manifests, unverifiable “confirmed” UX)?
- ☐ Are deadlines/PublicationContract triggers updated so “missingness” becomes portable (suppression reports + beacons)?

## 5) C4/C5 — Loud failure and non-lying UX
- ☐ On failure, do user-facing and public-facing surfaces fail *loudly* (NOT RECORDED / “evidence unavailable”) rather than implying success?
- ☐ Are any caches, retries, or fallback mirrors constrained so they cannot mask evidence loss or serve stale “success” states?

## 6) Register updates (minimum)
- ☐ If the change introduces a new failure mode: add/update hazards in `artifacts/hazards/hazard-register.csv` (including CatastropheClass).
- ☐ If the change affects response: add/update drills in `artifacts/registries/drill-scenarios.csv` and/or a checklist/playbook.
- ☐ If you add or materially change drill scenarios or operator checklists, add at least one **planned drill run** row in `artifacts/registries/drill-runs.csv` (status=`planned`, scenario_id + expected outputs).
- ☐ If this change adds/updates an operator-facing checklist/playbook/template: ensure it is **drillable** (add/update a scenario + expected evidence outputs; see `DOC:docs/86-exercises-and-gamedays-program.md`).
- ☐ If this change touches **entry-path / adopter briefing surfaces** (`README.md` 60‑minute path, `docs/START_HERE.md`, `docs/242`, adopter templates): run `CHECK:artifacts/checklists/adopter-60-minute-path-smoke-test.md` and log a bounded row in `artifacts/registries/adopter-path-smoke-tests.csv`.
- ☐ If this change touches **voter-facing legitimacy framing surfaces** (`docs/track-a/VOTER_VERIFICATION.md`, `docs/track-a/PERSONS_PATH.md`, `artifacts/templates/witness-profile.md`, observer-kit docs): ensure representation duty + material floor are explicit and remain discoverable from the 60‑minute outside view.
- ☐ If this change touches **public-facing comms surfaces** (PublicNotice content rules, public statement / incident comms templates, Track A narrative docs, observer-kit README): use explicit epistemic tags + confidence (`DOC:docs/218-epistemic-status-tags-and-confidence-rubric.md`) and uncertainty-safe update commitments (`DOC:docs/219-uncertainty-safe-public-updates.md`); avoid hedge-language; run `python3 scripts/check_no_hedging_in_public_templates.py`.
- ☐ If this change touches **publication pointer surfaces** or delivery paths (discovery pointer, PublicNotice feed/directory, status board, low-bandwidth fallback): run MAPT (`DOC:docs/187-publication-compliance-and-coverage.md`, `CHECK:artifacts/checklists/minimal-adversarial-publication-test.md`) and log the evaluation (bounded pointers/digests only) in `artifacts/registries/mapt-evaluations.csv` (recurring failure → `HZ‑027`).
- ☐ If this change touches authenticity/disinformation response posture (time-to-refute workflow, rumor-control/status board semantics, authenticity response cell checklist): ensure a measured TTR drill (or incident retrospective) exists and log a bounded row in `artifacts/registries/time-to-refute-evaluations.csv` (`DOC:docs/240-deepfake-frontier-and-time-to-refute.md`).
- ☐ If this change touches **witness governance surfaces** (witness policy/roster, witness checklists, witness incentives): ensure publishable behavioral health signals remain supported (`DOC:docs/135-witness-governance-incentives-and-capture-resistance.md` WIT‑7) and add/update bounded rows in `artifacts/registries/witness-health-log.csv`.
- ☐ If this change touches **eligibility/revocation transparency surfaces** or any public aggregation that could leak turnout timing/geography (Track B): run `CHECK:artifacts/checklists/turnout-oracle-risk-quickcheck.md` and log a bounded row in `artifacts/registries/turnout-oracle-risk-assessments.csv` (treat failures as hazard `HZ‑026`).
- ☐ If this change introduces or materially changes a **dispute-lane evidence surface** (new envelope kind, bundle contract semantics, “what gets filed”): update the court-proofing lane (`DOC:docs/43-evidence-bundles-and-court-proofing.md`) and refresh at least one admissibility plan artifact (`TEMPLATE:artifacts/templates/court-admissibility-worksheet.md` / `TEMPLATE:artifacts/templates/jurisdictional-admissibility-matrix.md`).
- ☐ If this change introduces a **new evidence object** (new schema, new kind, new proof obligation, new verifier output): name the plausible dispute it serves (one sentence) and update the claim→PO→evidence mapping (`artifacts/claims/claim-evidence-matrix.csv`, `DOC:docs/159-proof-obligations-ledger.md`). Prefer to also link it to at least one drill scenario (`artifacts/registries/drill-scenarios.csv`) or a court bundle recipe (`DOC:docs/211-court-evidence-bundle-recipes.md`).
- ☐ If the change **promotes Track B/C into Track A** (or expands scope toward remote ballot return): run `docs/229` and update `docs/166`/`docs/167` (no silent scope creep).
