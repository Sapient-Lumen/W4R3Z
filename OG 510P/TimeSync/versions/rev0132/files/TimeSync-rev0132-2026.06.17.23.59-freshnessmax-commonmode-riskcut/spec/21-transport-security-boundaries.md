# 21 — Transport security boundaries

## Separation of proofs

TimeSync distinguishes at least four proof surfaces:

```text
source identity or authentication proof in a wire claim
transport authentication supplied by a carrier
payload integrity over an envelope or semantic payload
profile-reference digest or signed profile binding
```

They are not interchangeable.

## Envelope integrity

Envelope integrity can say:

```text
this envelope or payload was not changed after it was protected
this producer key or transport identity was involved
this export package is complete under the stated protection scope
```

Envelope integrity cannot say:

```text
the clock was correct
the profile was satisfied
the source was traceable
the profile reference was independently bound by the right authority
the local assessment is currently accepted by policy
```

## Transport authentication

Transport authentication is useful for access control and tamper resistance. It does not by itself establish `traceability_posture.evidence_posture = traceable`.

A profile may require both transport authentication and traceability evidence, but those remain different obligations.

## Signed payload versus signed profile binding

A signed payload protects a payload.

A signed profile binding states who bound a profile reference, digest, version, or normative rule set. That binding belongs in `assessed_profile.binding` when the boundary requires it.

A payload signature does not fill in a missing `assessed_profile.digest` or `assessed_profile.binding`.

## Replay and retention

The envelope may help detect replay or stale export packages if the carrier or integrity scheme supports that. But replay detection does not update TimeState freshness. The assessed state's freshness is still the freshness expressed inside the nested semantic payload.

## Validator stance

The validator rejects fixtures that try to use envelope integrity as `signed_profile_binding` or as a replacement for required nested profile-reference strength.
