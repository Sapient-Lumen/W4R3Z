# Public audit report (template)

**Track:** Shared (cross-cutting)

This is a **public-facing** report. Treat it as a claim/evidence artifact:
- For any load-bearing statement, use epistemic tags (`DOC:docs/218-epistemic-status-tags-and-confidence-rubric.md`) and avoid hedge-language.
- Prefer digest pointers (packet manifest / checkpoint IDs) so third parties can replay verification offline (`DOC:docs/177-observer-kit-offline-verification-walkthrough.md`).
- If you need a digest-first public summary, publish it as a signed `PublicNotice` with `notice_type=audit_result` and link forward to the report packet.

Evidence pointers (fill these first):
- Audit scope packet manifest digest(s):
- Latest witness-quorum checkpoint ID + digest (if applicable):
- Related PublicNotice feed digest (window):


## Executive summary
- [OBSERVED|HIGH] election scope, dates, jurisdiction
- [MEASURED|HIGH] verification outcomes (log consistency, tally proofs, paper audits)

## Cryptographic verification
- [ATTESTED|HIGH] checkpoint policy (witness quorum)
- [MEASURED|HIGH] number of ballots recorded/final
- [DISPUTED|CONF] anomalies (fork proofs / missing checkpoints)
- [MEASURED|HIGH] tally proof verification results

## Paper audit (if applicable)
- [OBSERVED|HIGH] audit type (RLA / compliance / recount)
- [MEASURED|HIGH] sample sizes and outcomes
- [OBSERVED|CONF] discrepancies and resolution

## Incidents
- [OBSERVED|CONF] outages, DDoS, partitions
- [REPORTED|CONF] client malware/coercion reports (aggregate)
- [OBSERVED|CONF] mitigations and impact

## Recommendations
- operational improvements
- protocol/UX improvements
