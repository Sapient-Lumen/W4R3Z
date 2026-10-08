# Example County evaluator scorecard

**Synthetic example only. This is not live election evidence and not certification.**

Scenario: `EXAMPLE-COUNTY-2026-MUNI-v900`  
Archive version: `v900`  
Status: `PASS`  
Score: `100/100`

## Boundary

Synthetic rehearsal scorecard only; not certification, not live election evidence, not outcome proof, not proof of intent or fraud, and not legal advice.

## Metrics

- `ESR-001` / `version_currency`: `PASS` (10/10) — All core generated JSON outputs carry the current version and scenario id.
- `ESR-002` / `synthetic_boundary`: `PASS` (10/10) — Synthetic/live-evidence boundary is present in JSON and public markdown.
- `ESR-003` / `packet_verification`: `PASS` (10/10) — 20 packet verifier result(s) passed.
- `ESR-004` / `evidence_map_closure`: `PASS` (10/10) — Evidence map and court index close over all scenario packets.
- `ESR-005` / `scenario_recovery_coverage`: `PASS` (10/10) — 10 scenario(s) crosswalked to 11 recovery mode(s).
- `ESR-006` / `human_review_handoff`: `PASS` (10/10) — 20 worksheet row(s) route scenarios to reviewers.
- `ESR-007` / `retention_redaction_floor`: `PASS` (10/10) — 8 retention disposition(s) include preservation and redaction floors.
- `ESR-008` / `public_language_nonclaims`: `PASS` (10/10) — Public-facing files carry bounded non-claims and avoid prohibited inferences.
- `ESR-009` / `external_alignment_boundary`: `PASS` (5/5) — External standards remain crosswalk/alignment references, and the scorecard component is maturity-labeled.
- `ESR-010` / `pre_pilot_ledger_boundary`: `PASS` (5/5) — Pilot-data ledger records both current pre-pilot absence and synthetic rehearsal status.
- `ESR-011` / `negative_control_fixture_rejection`: `PASS` (10/10) — 8 expected-failure fixture(s) rejected by the verifier.

## Operator command

```bash
python3 tools/example_county_evaluator_scorecard.py --json
```

A passing scorecard means the synthetic rehearsal outputs are internally closed under the current release gates. It does not prove outcome correctness, does not replace canvass, audit, certification, recount, or court procedure, and does not turn failure evidence into proof of intent or fraud.
