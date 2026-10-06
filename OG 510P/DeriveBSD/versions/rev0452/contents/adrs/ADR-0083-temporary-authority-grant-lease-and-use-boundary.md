# ADR-0083: Temporary authority grant / lease / use boundary

- Status: Accepted
- Date: 2026-03-07

## Context

DeriveBSD already had the pieces for temporary authority:

- lane-specific grant / lease / session objects (`portal-grant`, `secret-grant`, `breakglass-grant`, `workload-identity-lease`, ...)
- cross-lane join metadata (`lease.envelope`)
- issuance / renewal / denial evidence (`lease.issue.receipt`)
- exercise evidence (`lease.use.receipt`)
- inventory / revocation evidence (`lease-snapshot`, `lease-revoke-event`)

But the archive still left one expensive ambiguity unresolved:

1. Did `lease.envelope.target` / `lease.issue.receipt.target` point at the object that actually grants temporary authority, or at some later action receipt?
2. Was a lease-issue receipt itself an authority object, or only evidence that authority was minted?
3. Was a lease-use receipt itself an action authorization, or only evidence that some already-issued authority was exercised?

That ambiguity is especially costly because it spreads across many lanes without looking like a “big subsystem”.

## Decision

1. The authoritative temporary-authority object remains lane-specific:
   - a grant,
   - a lease,
   - or a session object that actually confers temporary power.

2. `lease.envelope` is metadata only.
   Its `target` must point at the authoritative grant / lease / session object.
   It must **not** point at a later action receipt.

3. `lease.issue.receipt` is issuance evidence only.
   It records that a broker issued / renewed / denied temporary authority, but it does not become the authority object itself.
   The schema carries `authority_semantics = lease-issue-evidence-only`.

4. `lease.use.receipt` is use evidence only.
   It records that already-issued temporary authority was exercised or denied, but it does not become the operation's authoritative result.
   The schema carries `authority_semantics = lease-use-evidence-only`.

5. If a later operation emits its own authoritative or lane-specific receipt (`export.receipt`, `secret-receipt`, `breakglass-receipt`, ...), that later object belongs under `lease.use.receipt.related`.
   It must not be substituted into `lease.envelope.target` or `lease.issue.receipt.target`.

## Consequences

- temporary authority becomes easier to explain across lanes:
  grant/lease/session = authority,
  issue receipt = issuance evidence,
  use receipt = exercise evidence,
  revoke event = revocation evidence.
- incident and support tooling get one stable answer to “what authority existed?” without confusing it with “what operation later happened?”.
- future lanes can adopt the pattern without inventing new one-off terminology.

## Why this is narrow enough

This does not redesign portals, secrets, breakglass, export, or workload identity.
It only fixes the generic boundary between:

- the object that grants temporary power,
- the evidence that it was issued,
- and the evidence that it was used.

That is a small, high-leverage revision with low churn and high anti-drift value.
