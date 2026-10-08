# Migration map — rev0069 to rev0070

## New files

```text
schema/authorized-verifier-challenge.schema.json
spec/33-authorized-verifier-challenge-boundary.md
examples/evaluator/authorized-verifier-challenge-result-p3-redacted.json
examples/negative/authorized-verifier-challenge-expired-response-invalid.json
examples/negative/authorized-verifier-challenge-target-mismatch-invalid.json
examples/negative/authorized-verifier-challenge-preimage-export-invalid.json
examples/negative/evidence-summary-authorized-verifier-disclosure-obligation-invalid.json
examples/negative/discovery-authorized-verifier-challenge-malformed-invalid.json
archive/FT-0069-CLOSURE.md
archive/REV0069-TO-REV0070-MIGRATION-MAP.md
```

## Normative changes

```text
added evidence class authorized_verifier_disclosure
added forbidden class to every profile evidence_policy
regenerated every profile normative_rules_digest
added detached challenge-result schema and semantic checks
```

## Compatibility note

Existing rev0069 evidence summaries remain structurally close, but any profile reference digest must be updated because the profile evidence policy now includes the additional non-satisfying evidence class.

Challenge results are detached review artifacts. They are not TimeState, not profile assessment conclusions, and not ordinary evidence-summary inputs.
