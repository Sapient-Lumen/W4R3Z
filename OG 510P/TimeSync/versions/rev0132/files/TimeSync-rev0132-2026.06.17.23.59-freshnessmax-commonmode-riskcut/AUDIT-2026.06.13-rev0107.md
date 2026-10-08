# TimeSync rev0107 audit — discovery current-use binding

rev0107 continues FT-0090 without widening the TimeState core. The highest-risk remaining executable gap found in this pass was not another timestamp edge; it was a current-use discovery binding bypass.

## Finding

Current-use discovery result interpretation had three pieces that were individually checked but not required to agree:

```text
version_negotiation.current_use_allowed
freshness.freshness_status = fresh_for_current_use
digest_binding.current_use_allowed / digest coverage
```

rev0094 made current discovery freshness executable, and rev0092 made digest canonicalization safer, but rev0106 still allowed a returned result to set `version_negotiation.current_use_allowed: true` and omit `digest_binding` entirely. The freshness helper would treat the result as current and verify a freshness timestamp, but nothing forced the returned object onto a digest-bound interpretation path.

That was a real integrity gap: freshness could answer “is this recent enough?” without proving “is this the object/version semantics that current use is allowed to interpret?”

## Change

rev0107 adds `tools/discovery_binding_semantics.py` and moves discovery result version/digest binding checks out of the monolithic validator. The new helper now rejects:

```text
current-use discovery result without digest_binding metadata
version_negotiation.current_use_allowed=true while digest_binding.current_use_allowed=false
digest_binding.current_use_allowed=true while version_negotiation.current_use_allowed is false or absent
current-use result under require_digest_binding_policy without digest_binding_policy_digest, except the policy object itself
```

The helper retains downgrade-proof and semantic-version checks previously inline in `tools/validate_archive.py`.

## Why this is not registry growth

This revision does not add a discovery registry, credential system, transport verifier, or new profile authority surface. It only makes already-declared current-use metadata agree before discovery results can be interpreted as current.

## Refactor result

The validator loses another concern family:

```text
digest_binds
parse_semver
check_downgrade_proof_metadata
check_result_version_negotiation
check_digest_binding_metadata
current discovery binding agreement
```

Those now live in `tools/discovery_binding_semantics.py` and have local self-tests.

## Regression material

New derivation-checked negative fixtures:

```text
examples/negative/discovery-current-result-missing-digest-binding-invalid.json
examples/negative/discovery-current-result-digest-not-current-invalid.json
examples/negative/discovery-current-result-version-not-current-invalid.json
examples/negative/discovery-current-result-missing-version-current-invalid.json
```

New semantic vectors:

```text
TV-N288
TV-N289
TV-N290
TV-N291
```

## Remaining risk

FT-0090 remains open, but the unresolved work is now mostly maintainability and fixture-family scale. The next useful pass is likely a narrow extraction of digest-binding policy / semantic-version policy checks, or a selective derivation cleanup of bulky discovery and aggregate fixtures.
