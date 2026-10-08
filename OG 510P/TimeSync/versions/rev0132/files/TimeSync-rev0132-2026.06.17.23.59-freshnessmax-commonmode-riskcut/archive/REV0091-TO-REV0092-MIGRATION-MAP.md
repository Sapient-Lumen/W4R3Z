# Migration map — rev0091 to rev0092

## Baseline

rev0091 added date-time format assertion, duplicate semantic-vector ID checks, and two temporal-coherence freshness fixes. It left FT-0090 open, especially the digest canonicalization half.

## rev0092 movement

rev0092 closes the most operationally risky digest gap by adding an executable TimeSync JCS subset module and wiring profile-rule digest validation through it.

## Files added

```text
tools/jcs.py
AUDIT-2026.06.12-rev0092.md
archive/REV0092-AUDIT-JCS-DIGEST-REFACTOR.md
examples/negative/digest-binding-policy-codepoint-order-invalid.json
examples/negative/profile-catalog-unsafe-digest-number-invalid.json
examples/negative/jcs-duplicate-member-invalid.json
```

## Files changed

```text
tools/validate_archive.py
schema/digest-binding-policy.schema.json
spec/28-profile-digest-canonicalization.md
spec/54-portable-canonicalization-and-byte-envelope-bindings.md
examples/digest-binding-policy-rev0086.json
examples/discovery-request-with-version-negotiation.json
related negative discovery/digest-policy fixtures
tests/semantic-test-vectors.yaml
tests/acceptance-tests.yaml
current-facing README/index/report files
```

## Compatibility impact

Profile digests did not need to change because the existing normative profile objects already fit the new safe-integer/I-JSON subset and use ASCII member names. The important change is that future drift into unsafe numeric or duplicate-member territory now fails closed.

## Remaining FT-0090 scope

The digest half is materially reduced. The remaining FT-0090 work is temporal-coherence generalization and validator decomposition.
