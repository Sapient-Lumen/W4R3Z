# Example County trust-recovery bulletin

**Synthetic example only. This is not live election evidence.**

Scenario: `EXAMPLE-COUNTY-2026-MUNI-v900`  
Archive version: `v900`  
Failure modes covered: `11`

## Boundary

This bulletin describes what the synthetic verifier/public handoff should say when evidence is missing, divergent, stale, compromised, or unverifiable. It does not prove that an election outcome is correct, does not replace canvass, audit, certification, recount, or court procedure, and does not turn failure evidence into proof of intent or fraud.

## Public failure language

- `TRP-001` / `verification_failed_preserve_packet`: This packet did not pass the listed verifier checks; preserve the packet and use the problem codes before drawing conclusions.
- `TRP-002` / `expected_artifact_not_found`: The expected artifact was not found by the stated deadline on the named surface; this records publication state only.
- `TRP-003` / `divergent_public_views_recorded`: Different public views of the named surface produced different bytes or status; the divergence is recorded for correction and review.
- `TRP-004` / `trust_boundary_changed`: The signing trust boundary changed; use the signed explanation and witness-set change before trusting later artifacts.
- `TRP-005` / `ai_assisted_output_corrected`: A human authority corrected or approved this AI-assisted public artifact; voters should use the current official artifact.
- `TRP-006` / `derivative_not_authority`: The official digest-bound artifact is the authority; an image or forwarded copy is not enough to verify the notice.
- `TRP-007` / `supporting_technology_incident_recorded`: The supporting election technology incident and recovery evidence are recorded in bounded packets.
- `TRP-008` / `witness_governance_review_opened`: A witness governance issue is recorded; use the witness-set change and dissent records to interpret later attestations.
- `TRP-009` / `safe_escalation_route_published`: This is the safe official route for reporting intimidation, obstruction, or unsafe conduct without exposing private voter information.
- `TRP-010` / `source_review_needed_before_reliance`: This external reference needs current review or a pinned digest before it is used as a live authority.
- `TRP-011` / `review_disagreement_preserved`: The reviewer disagreement and redaction basis are preserved before the public language is treated as settled.

## Operator command

```bash
python3 tools/trust_recovery_output_pack.py --json
```
