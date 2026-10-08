# Audit note — rev0099 profile compatibility temporal/refactor pass

rev0099 intentionally avoids another registry or broad doctrinal expansion. The deep-read target was the remaining maintainability frontier plus one still-executable stale/future artifact seam.

## Finding

Profile compatibility statements are portable artifacts. They can authorize workflow reuse such as challenge-result portability or compatibility-drift review, but rev0098 only checked `issued_at < expires_at`. It did not make the signature/expiry boundary executable, and it did not ensure that drift evidence embedded in a signed compatibility statement existed by the statement signature time.

That left two bad shapes possible:

```text
binding.signed_at > expires_at
compatibility_drift.evaluated_at > binding.signed_at
```

Both are compact-artifact timing errors. They do not require a new registry. They require executable artifact-time ordering.

## Change

rev0099 adds `tools/profile_compatibility_temporal.py` and wires it into `check_profile_compatibility_statement`.

The helper now enforces:

```text
issued_at <= binding.signed_at
binding.signed_at <= expires_at
compatibility_drift.evaluated_at <= binding.signed_at
compatibility_drift.evaluated_at <= expires_at
```

The older inline `issued_at < expires_at` check was moved into the helper.

## Fixture/refactor work

rev0099 adds two new negative fixtures:

```text
examples/negative/profile-compatibility-binding-after-expiry-invalid.json
examples/negative/profile-compatibility-drift-after-signature-invalid.json
```

It also adds derivations for those fixtures and retrofits one older copied profile-compatibility negative:

```text
DF-0099-001 -> profile-compatibility-challenge-workflow-weaker-invalid.json
DF-0099-002 -> profile-compatibility-binding-after-expiry-invalid.json
DF-0099-003 -> profile-compatibility-drift-after-signature-invalid.json
```

This is the desired direction: rendered JSON remains present for audit review, but the copied fixture family is mechanically tied to a positive base plus explicit patch operations.

## Boundary retained

Compatibility statement timing still does not update:

```text
TimeState freshness
profile assessment
current actionability
transport authentication
profile evidence obligations
authority registry state
```

It only prevents incoherent portable compatibility artifacts from being accepted as current supporting material.

## Remaining risk

FT-0090 remains open. The riskiest remaining work is not another specific timestamp field; it is continued validator decomposition and selective derivation of copied fixture families where that materially reduces drift.
