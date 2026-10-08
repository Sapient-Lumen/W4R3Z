# 700 — Pilot scenario harness, maturity labels, and evaluator path

**Track:** Shared / Track A pilot readiness

## Purpose

This pass turns the v824 proof-closure work into a tighter rehearsal path. It does not add live deployment evidence. It makes the archive easier to evaluate by binding the synthetic Example County packets into one scenario, labeling component maturity, and adding a release-gate check that the smallest pilot path stays wired.

## What changed

- Added `artifacts/examples/example_county_2026_municipal_pilot/scenario.json` as the canonical synthetic pilot harness.
- Added `tools/example_county_pilot_smoke.py` so operators can verify every packet referenced by that scenario without browsing the full archive.
- Added `artifacts/registries/component-maturity.csv` to separate operational and pilot-ready Track A components from research and speculative material.
- Added `scripts/check_component_maturity.py` so evidence claims cannot be enabled for research, speculative, deprecated, or quarantined components.
- Added `artifacts/registries/evaluation-scenarios.csv` with eight bounded evaluator scenarios: forged notice screenshot, missing publication, split-view surface, key compromise, AI-assisted public error, intimidation, non-voting technology outage, and legacy result export drift.
- Added `scripts/check_pilot_readiness.py` so the synthetic scenario, public summary, adopter smoke-test row, turnout-oracle risk row, and pilot-data ledger cannot silently drift.
- Populated `artifacts/registries/adopter-path-smoke-tests.csv` and `artifacts/registries/turnout-oracle-risk-assessments.csv` with bounded synthetic/pre-pilot rows instead of leaving them empty.

## Maturity labels

Component maturity is now explicit:

| Label | Meaning | Track A evidence claims allowed? |
|---|---|---|
| `operational` | Core machinery that can be checked by release-gate and verifier tools. | Yes, when proof obligations and examples exist. |
| `pilot_ready` | Ready for a bounded local pilot after jurisdiction configuration. | Yes, but only for the configured pilot scope. |
| `research` | Useful design or analysis support; not a deployment claim. | No. |
| `speculative` | Future or hard-mode direction; not a near-term pilot path. | No. |
| `deprecated` | Superseded or retained only for historical continuity. | No. |
| `quarantined` | Unsafe, incomplete, or intentionally isolated. | No. |

The registry is intentionally small. It labels components, not every file.

## Scenario harness

The synthetic Example County scenario is a phase map, not a new legal or operational authority. Its phases are:

1. setup official channels,
2. election parameters and witnesses,
3. notice publication,
4. public-surface monitoring,
5. results and closeout,
6. incident and recovery,
7. verifier outputs.

Each phase lists packet directories and a public sentence. The smoke tool verifies every referenced packet with the offline observer verifier and returns a compact JSON report.

## Evaluator path

The new evaluator scenarios are designed to answer one question: can a reviewer tell what the packet proves, what it does not prove, and what public sentence is safe? The expected output is a digest-bound packet, a missingness/parity/incident record where appropriate, a public-language sentence, and a stable verifier result.

This makes the cube more testable. A future live pilot should measure:

- MAPT: whether adversarial publication tests find the expected failure modes,
- TTR: time to refute a forged or misleading public artifact,
- witness health: whether independent witnesses remain diverse and live,
- public comprehension: whether non-expert reviewers understand the packet's non-claims.

## External alignment posture

The harness remains aligned around, not formally conformant to, current external guidance and assurance lanes: NIST election-infrastructure cybersecurity profile (`xref:nist_nistpubs_vts_nist_vts_200_1`), EAC AI election-administration guidance (`xref:eac_ai_and_election_administration_page`, `xref:eac_ai_case_studies_2026_pdf`), CIS RABET-V non-voting technology assessment (`xref:cis_rabet_v_page`), and CISA election-security resource posture (`xref:cisa_security`).

## Non-claims

- The synthetic scenario is not live deployment evidence.
- The smoke tool does not validate cryptographic signatures.
- The scenario does not prove that any election outcome is correct.
- Missingness, parity divergence, or incident evidence does not prove intent or fraud.
- Track B remains a research lane, not a deployment roadmap.
