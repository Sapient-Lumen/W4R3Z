# 27 — Profile catalog compatibility statements

rev0065 closes FT-0064 by defining a small cross-operator profile compatibility surface.

The problem is not profile distribution. The problem is how a receiver can compare independently operated profile catalogs without inventing a central registry, transport negotiation, or broad catalog manifest exchange.

## Object

A compatibility statement is a signed, expiring policy artifact:

```text
statement_version
issuer_authority
issued_at
expires_at
subject_profile authority/id/version/digest
related_profile authority/id/version/digest
relation
evidence_policy_relation
applicability_mapping
binding
```

The schema is `schema/profile-compatibility-statement.schema.json`.

## Relations

```text
exact_equivalent  the normative profile-rule digest values are identical
compatible_with   the issuer asserts local-policy compatibility despite different identities or digests
supersedes        the subject profile replaces the related profile for the issuer's policy scope
alias_for         one authority asserts an alias relation between two profile references
```

`exact_equivalent` is deterministic and requires identical digest values.

Other relations are assertions. A receiver may accept, reject, or accept with conditions under local policy.

## Evidence policy relation

```text
identical
stricter_or_equal
weaker
unknown
```

`stricter_or_equal` means the subject profile's evidence policy is asserted not to weaken the related profile's review/evidence requirements. The statement does not prove that by itself; it declares the relation for local policy evaluation.

## Applicability mapping

Applicability labels remain profile-local. Compatibility therefore needs a mapping posture:

```text
identity
explicit_profile_local_map
not_asserted
```

An explicit map carries a digest over the mapping statement. The map is not a global applicability registry.

## Non-negotiation rule

A compatibility statement does not:

```text
update a profile catalog
bind a transport adapter
negotiate a profile
upgrade an operator alias into a profile reference
substitute for local policy acceptance
```

It is a detached artifact that can be used by a receiver's local policy layer.

## Validator rules

The validator checks that:

```text
subject and related profiles carry authority and digest
subject digest matches the local catalog when the subject resolves
exact_equivalent uses identical normative profile-rule digests
alias_for is signed by the subject or related profile authority
expires_at is after issued_at
```

The positive example is `profiles/compatibility/p3-exact-equivalent-self.json`. Negative fixtures cover digest mismatch, third-party alias assertion, and missing digest.

## rev0071 workflow caveat for challenge-result portability

A compatibility statement may optionally include:

```text
compatible_workflows:
  - authorized_verifier_challenge_result_portability
```

This does not negotiate a workflow and does not authorize disclosure. It only says that the issuer's compatibility assertion is intended to cover portable replay of authorized-verifier challenge results as commitment-verification receipts.

When this workflow is named, `evidence_policy_relation` must be `identical` or `stricter_or_equal`. A statement that weakens evidence policy cannot be used to carry challenge-result portability across profile/operator boundaries.
