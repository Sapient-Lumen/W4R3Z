# 90 — Exercise Scenario Library (Election Ops Reality)

**Track:** A (Deployable core)


## Overview
This library provides scenario “cards” for tabletop exercises and gamedays.

Each scenario includes:
- Trigger
- Technical reality (what can actually happen)
- Decision points
- Required public artifacts (hashes/checkpoints)
- Pass/fail criteria

## Scenario cards (canonical registry)

Canonical scenario registry:
- `artifacts/registries/drill-scenarios.csv`

Canonical drill run log (planned/completed; bounded pointers to AAR + packet digests):
- `artifacts/registries/drill-runs.csv`

This doc is intentionally a **thin index** so scenarios don’t drift across prose files.
Use the registry row for the authoritative pointers (triggers, required envelope kinds, checklists, playbooks).

### Ops-reality starter set (maps to common tabletop prompts)

- **S1 — DDoS + selective submission dropping** → `scenario_id: ddos_selective_drop`
  - Expected artifact: a fast `hfv.public.notice` describing scope + receipt states/time windows.
- **S2 — Split-view (equivocation) attempt** → `scenario_id: sequencer_equivocation`
  - Expected artifact: fork proof pointers + witness gossip transcript digests.
- **S3 — Ballot definition substitution** → `scenario_id: ballot_definition_substitution`
  - Expected artifact: canonical EPB digest + canary evidence pointers.
- **S4 — VRDB snapshot regression / rollback attempt** → `scenario_id: vrdb_snapshot_regression`
  - Expected artifact: last-known-good snapshot digest + explicit freeze decision when needed.
- **S5 — ENR drift + fake results injection** → `scenario_id: enr_drift_fake_injection`
  - Expected artifact: canonical ENRUpdate digest + guidance for independent verification.
- **S6 — Credential recovery fraud wave** → `scenario_id: credential_recovery_fraud_wave`
  - Expected artifact: advisory that does not amplify phishing, plus support channels + cadence.

### Human-stress starter set (hardest moments)

- **H1 — Conflicting reports / information overload** → `scenario_id: conflicting_reports_overload`
- **H2 — Political pressure to publish unverified claims** → `scenario_id: political_pressure_unverified_claims`
- **H3 — Forged “official statement” circulates (time-to-refute)** → `scenario_id: forged_official_statement_time_to_refute`
- **H4 — Legibility-theater publication drop (exists-but-not-usable)** → `scenario_id: legibility_theater_publication_drop`

These scenarios are designed to test the **human process layer** (triage + comms + legal posture) under overload and adversarial pressure.
Use the registry row as the authoritative pointer to required checklists and playbooks.
For H3/H4, use `artifacts/templates/time-to-refute-test-plan.md` and the refutation packet checklist.


## Templates & schemas
- Exercise plan: `schemas/ExercisePlan.json`
- After action: `schemas/AfterActionReport.json`
- Templates: `artifacts/templates/after-action-report.md`
