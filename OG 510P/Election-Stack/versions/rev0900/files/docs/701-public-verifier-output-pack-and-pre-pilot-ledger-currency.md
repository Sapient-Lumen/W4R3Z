# 701 — Public verifier output pack and pre-pilot ledger currency

**Track:** Shared / Track A pilot readiness

## Purpose

This pass closes a quieter readiness gap: the synthetic Example County scenario could verify packets, but it did not yet ship a single derived output pack for public readers, observer/verifier readers, and evidence-preservation readers. Some pre-pilot ledgers also still carried older placeholder version rows. That is easy to miss in a large datacube, so v826 makes both conditions machine-checkable.

## What changed

- Added `tools/example_county_output_pack.py` to derive output files from `scenario.json` instead of maintaining them by hand.
- Added `artifacts/examples/example_county_2026_municipal_pilot/evidence-map.json` with phase, packet, manifest digest, status, and verifier command mapping.
- Added `artifacts/examples/example_county_2026_municipal_pilot/smoke-report.json` as a stored synthetic verifier run.
- Added `artifacts/examples/example_county_2026_municipal_pilot/court-packet-index.csv` as a preservation-oriented index with explicit non-claims.
- Added `artifacts/examples/example_county_2026_municipal_pilot/public-verifier-quickstart.md` as the shortest public/operator path through the synthetic harness.
- Added `artifacts/registries/pilot-operational-invariants.csv` as the machine-readable rulebook for the smallest useful pilot path.
- Added `scripts/check_example_county_output_pack.py`, `scripts/check_prep_evidence_ledgers.py`, and `scripts/check_pilot_operational_invariants.py` to the release gate.
- Added current-version pre-pilot rows for drill, external review, MAPT, witness-health, adopter smoke, and pilot-data ledgers.

## Operational invariant

The new rule is:

> A synthetic pilot is not ready merely because packets verify. It must also ship public/verifier/court-facing outputs, preserve non-claims, and keep its pre-pilot ledgers current for the release that claims readiness.

The output pack remains synthetic-only. It is not a court filing, legal opinion, official canvass record, audit result, certification record, recount record, or proof of fraud/intent. It is a rehearsal of how digest-bound evidence can be indexed and explained.

## External alignment posture

The pass remains an alignment layer rather than a conformance claim. It keeps the Track A pilot path compatible with risk-based election infrastructure cybersecurity framing (`xref:nist_nistpubs_vts_nist_vts_200_1`), non-voting election-technology assurance lanes (`xref:cis_rabet_v_page`), election-office AI human-review posture (`xref:eac_ai_case_studies_2026_pdf`), election-security resource posture (`xref:cisa_security`), and election-official safety/reporting posture (`xref:eac_officials_official_security`).

## Non-claims

- The output pack does not prove any election outcome.
- The court-packet index is not legal advice.
- Missingness, parity divergence, or incident evidence does not prove intent or fraud.
- Current-version pre-pilot ledger rows do not fabricate live deployment evidence.
- Track B remains research and is not promoted by this pass.
