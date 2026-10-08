# 150. Maintainer bootstrap and LLM-safe change protocol

**Track:** Shared


This document is written for a future maintainer (human or LLM) who starts “cold” and must make safe changes without relying on memory.

The goal is to make every security-relevant change:

- evidence-backed,
- mechanically reviewable,
- and versioned in a way that prevents silent interoperability or governance breaks.

## 150.1 Non-negotiable invariants

0. **Software independence is the recovery anchor.** If this system is used in binding public elections, a **human-readable ballot of record** (or voter-verifiable paper record) + **risk-limiting audits** remain the legitimacy backstop.

1. **No long-term credential signs ballots.** Citizen credentials (e.g., WebAuthn) may authenticate only to mint **unlinkable eligibility tokens**. Ballots are encrypted/signed only with *ballot-specific* keys and protocols.

2. **No “RECORDED” without proof.** A client MUST NOT display a definitive “RECORDED”/“ACCEPTED” status unless it holds a valid inclusion proof against a quorum-cosigned checkpoint.

3. **EPB is the only “official parameter” object.** Ballot definitions, crypto policies, witness sets, disclosure policy, and deadlines MUST be committed in the ElectionParameterBundle (EPB), included in the log, and quorum-witnessed.

4. **Fail loud on split-world risks.** If witnesses/monitors disagree or checkpoints diverge, the system must emit fork/suppression artifacts, not “best effort” UX.

5. **Evidence is content-addressed.** Public evidence bundles must be immutable, hashed, signed, and (optionally) timestamped/notarized. No silent edits.

## 150.2 Read-this-first map (30-minute cold start)

1. `00–05` (goals, threat model, architecture, protocol, transparency log, key management)
2. `09–10` (audit/recovery, assurance plan)
3. `55` (parameter/key transparency) + `60–62` (ballot definition integrity)
4. `63–72` (public results/ENR, results pipeline, comms)
5. `86–90` (exercises, comms proof, SLOs, scenarios)
6. `91–99` (observer kit, notarization, provenance)
7. `109–116` + `100–103` (availability + gossip / anti split-view)

## 150.3 Mechanical bootstrap steps (before changing anything)

- Validate JSON Schemas: `python3 scripts/validate_schemas.py` (see template)
- Run minimal checkers:
  - `python3 tools/bundle_gossip_checker.py --help`
  - `python3 tools/enr_drift_detector.py --help`
  - `python3 tools/challenge_sampler.py --help`
- Verify artifact index consistency: `python3 scripts/check_index.py` (see template)

If the baseline fails, fix that first. Don’t stack unrelated changes.

## 150.4 Evidence-backed change protocol

Every security-relevant change SHOULD follow this sequence:

If you are doing a structural refactor (renames/moves/splits), follow `227` first (tombstones + stable pointers).

0. **Claude coherence check.** Identify which normative requirements in `docs/244-claude-normative-requirements-digest.md` this change touches.
   - If you are adding/changing an operator checklist or playbook, ensure it is drillable (scenario + expected evidence outputs; see `docs/86`).

1. **Write the question.** What is changing and why? What attacker capability does it address?
2. **Find authoritative sources.** Prefer standards bodies / election authorities / peer-reviewed work.
3. **Pin sources.** Add entries in `evidence/lock/external-sources.toml` with immutable references and sha256.
4. **Update spec text.** Modify the relevant `*.md` specs and/or create an ADR.
5. **Update artifacts.** Add example objects, schemas, test vectors, and/or checklists.
6. **Update detection/evidence lanes.** Ensure there is a way to detect regression (tooling, drills, monitors).
7. **Decide versioning.** If message formats / schemas / policy invariants change, bump the pack version and add a migration note (see `docs/173` versioning rules).
8. **Record the decision.** Add an ADR + update `../artifacts/risks/risk-register.csv` if risk posture changed.

## 150.5 Drift triggers (mandatory periodic review)

When these upstreams change, you MUST re-check the relevant specs and record a decision:

- EAC VVSG/Test Assertions and E2E evaluation process
- NIST Common Data Formats (BD/CVR/ERR/Event logs)
- CISA election guidance updates (ballot return, IR comms, VRDB)
- Relevant IETF RFCs/drafts used here (CT, OHTTP/ODoH, HTTP message signatures, Privacy Pass)

## 150.6 “Ask yourself” prompts

Before you merge anything, answer these in writing (ADR or change note):

- What attacker capability does this change address?
- Which invariant does it rely on?
- What evidence lane detects regression?
- What breaks if an operator deploys this change mid-election?

If you can’t answer these, the change is not ready.

## 150.7 Claude feedback coherence gate (maintainer non‑negotiables)

Before merging a change that touches Track A public/operational surfaces:

- Re-read the compact non‑negotiables: `docs/244-claude-normative-requirements-digest.md`.
- If you touch **entry-path / adopter briefing surfaces** (`README.md` 60‑minute path, `docs/START_HERE.md`, `docs/242`, adopter templates): run `CHECK:artifacts/checklists/adopter-60-minute-path-smoke-test.md` and log a bounded row in `artifacts/registries/adopter-path-smoke-tests.csv`.
- If you touch **voter-facing legitimacy framing surfaces** (`docs/track-a/VOTER_VERIFICATION.md`, `docs/track-a/PERSONS_PATH.md`, `artifacts/templates/witness-profile.md`, observer-kit docs): ensure the representation duty and material floor remain explicit, and keep these surfaces discoverable from the 60‑minute outside view.
- If you add or materially change an **operator checklist/playbook**, also add or update:
  - at least one **drill scenario** (`artifacts/registries/drill-scenarios.csv`) and
  - an expected **publishable output** (AAR + packet pointers; see `docs/86`).
  - a **planned drill run** row in `artifacts/registries/drill-runs.csv` (status=`planned`, scenario_id + expected outputs)
- If you are making a scope/claims change, update `docs/166` + `docs/167` and record an ADR.
- If you attempt or authorize a **Track B/C → Track A promotion** that touches remote ballot return (or other C1–C2 scope expansion), record a bounded row in `artifacts/registries/promotion-events.csv` (pointers to independent review, adversarial non‑claims review, rollback plan, ADR ID).
- If you introduce a **new evidence object** (schema/kind/PO/verifier output), name the plausible dispute it serves and update the claim→PO→evidence mapping (`artifacts/claims/claim-evidence-matrix.csv`, `docs/159-proof-obligations-ledger.md`). Prefer to also link it to at least one drill scenario or court bundle recipe.
- If you introduce or materially change a **dispute-lane evidence surface** (new envelope kind, bundle contract semantics, “what gets filed”), update the court-proofing lane (`docs/43`) and refresh at least one admissibility planning artifact (`artifacts/templates/court-admissibility-worksheet.md` and/or `artifacts/templates/jurisdictional-admissibility-matrix.md`).
- If you touch **witness governance surfaces** (Witness Policy, witness roster/profile templates, rotation procedures): ensure publishable behavioral health signals remain supported (`docs/135` WIT‑7) and record/update bounded rows in `artifacts/registries/witness-health-log.csv`.
- If you touch **eligibility/revocation transparency surfaces** or publishable aggregates that could leak turnout timing/geography (Track B): run `CHECK:artifacts/checklists/turnout-oracle-risk-quickcheck.md` and record a bounded row in `artifacts/registries/turnout-oracle-risk-assessments.csv` (treat failures as hazard `HZ‑026`).
- If you cannot satisfy a requirement, record an explicit risk acceptance note (ADR + hazard mapping).
- If you touch a **spec/tool correctness surface** (canonicalization, envelope semantics/kinds, offline verifier behavior, PublicNotice effective-state rules, results hashing) or promote a new Track A claim, run at least one **surface-focused external review session** and record it in `artifacts/registries/external-review-log.csv` (use `artifacts/checklists/external-review-session-checklist.md`; store only bounded refs/digests, not long appendices).
- If you touch **public-facing comms surfaces** (public statement templates, incident comms templates, Track A narrative docs, observer-kit README), enforce explicit epistemic tags (`218`) and uncertainty-safe update mechanics (`219`), avoid hedge-language, and run `python3 scripts/check_no_hedging_in_public_templates.py` as a drift firewall.
- If you touch **publication pointer surfaces** or “bytes are public” delivery paths (discovery pointer, PublicNotice feeds/directories, low-bandwidth fallbacks, status boards), run MAPT (`DOC:docs/187-publication-compliance-and-coverage.md`, `CHECK:artifacts/checklists/minimal-adversarial-publication-test.md`) and record a bounded result row in `artifacts/registries/mapt-evaluations.csv` (treat recurring failures as `HZ-027`).
- If you touch authenticity/disinformation response surfaces (time-to-refute posture, rumor-control/status-board workflow, authenticity response cell checklist), ensure a measured TTR drill (or incident retrospective) exists and log a bounded result row in `artifacts/registries/time-to-refute-evaluations.csv` (`docs/240`).
