# rev0114 audit — policy authority digest refactor

## Extracted concern

`tools/policy_authority_digest_semantics.py` owns artifact-class binding checks for compact policy lifecycle-authority references and recovery attestations.

## New executable checks

```text
policy lifecycle authority reference authority_digest -> transparency_trust_policy_lifecycle_authority
policy lifecycle authority reference policy_digest -> transparency_trust_policy_rules
discovery authority_binding_digest -> transparency_trust_policy_lifecycle_status
anti_rollback_sequence.status_record_digest -> transparency_trust_policy_lifecycle_status
rotation_statement_digest -> transparency_trust_policy_lifecycle_authority_rotation
successor_authority_digest -> transparency_trust_policy_lifecycle_authority
delegation_digest -> transparency_trust_policy_lifecycle_authority_delegation
compromise response_digest -> transparency_trust_policy_lifecycle_authority_compromise_response
recovery attestation digest fields -> their named policy lifecycle-authority artifact classes
```

## New tests

```text
TV-N311 / DF-0114-001 — sequence status digest wrong bind
TV-N312 / DF-0114-002 — rotation statement digest wrong bind
TV-N313 / DF-0114-003 — successor authority digest wrong bind
```

## Non-goals

No repository topology, external verifier, trust-anchor roster, credential chain, or rotation-protocol semantics were added. rev0114 keeps TimeSync at the compact evidence-summary boundary.
