# 16 — Threat and misuse model

This file names failures the model is designed to make visible. It is not a cryptographic threat model for any particular transport.

## Misuse: authenticated but wrong

A signed or authenticated source claim can still be inaccurate, stale, misconfigured, or outside its claimed applicability.

Mitigation in TimeSync:

```text
wire claim is not local assessed state
identity/auth proof is not profile_conformance
receiver computes freshness, regime, source_posture, applicability
```

## Misuse: bare fallback

A system exports `profile_conformance: fallback` without saying what the state remains usable for.

Mitigation:

```text
fallback requires explicit profile-local applicability
fallback target must be non-stronger inside the profile map
```

## Misuse: label laundering

A weak local label is mapped into a stronger-looking label in another profile.

Mitigation:

```text
applicability is profile-local
multiple profile assessments remain scoped
no global downgrade table exists
```

## Misuse: historical rewrite

A retained assessment is silently edited after the assessed profile is superseded or revoked.

Mitigation:

```text
historical profile_conformance is preserved
current policy acceptance is a separate overlay
reassessment creates a new entry
```

## Misuse: digest over the wrong thing

A digest is treated as a hash of a packet, PDF, certificate, source roster, or whole standards catalog.

Mitigation:

```text
profile reference digest binds normative_profile_rules only
```

## Misuse: relay upgrade

A relay or aggregator restates time and unintentionally upgrades trust or applicability.

Mitigation:

```text
boundary_context.action = restate or downgrade where relevant
non-upgrade rule applies after relay boundaries
```

## Misuse: optional absence confused with profile failure

A requested optional item is absent and the system treats that as universal profile failure.

Mitigation:

```text
optional request absence is item-level result accounting
profile-required/default absence is conformance logic
```
