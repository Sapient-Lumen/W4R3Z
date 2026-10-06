# ADR-0157: Publish-session secret lifetime coupled to session authority

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0152 moved temporary sharing onto `net.publish.session` so B/C users no longer had to
normalize shadow tunnels or casual public listeners.
ADR-0153 then made audience/publicness explicit.
ADR-0154 then made the session explicitly reboot-cleared and `new-session-with-fresh-authority`.
ADR-0155 then kept public/org/support locators session-scoped instead of durable.
ADR-0156 then kept secret-gated shares redacted by moving usable secret material onto a separate
`secret.receipt` handoff lane.

One expensive ambiguity still remained:

**can the secret handoff outlive the publish-session authority that justified the share?**

Current systems already make the pressure visible:
- Vault response wrapping lets callers set a separate TTL for a single-use wrapping token,
- pre-signed URL ecosystems embed explicit expiration into the signed artifact,
- and many service-token or relay products happily let credentials live longer than the UI flow that created them.

If DeriveBSD leaves that implicit, the archive regresses in a quieter way than bearer URLs:
`net.publish.session` may say the share ended, but the joined handoff secret can still survive as the
real authority object. That breaks the whole point of a temporary share lane.

The archive needs one small answer that preserves secret-gated B/C sharing without inventing a new
secret-lease subsystem.

## Decision

1. Secret-gated publish sessions remain redacted and continue to join usable secret material through
   `published_endpoint.secret_handoff`.

2. `published_endpoint.secret_handoff` now also records:
   - `lifetime_binding = session-authority-bounded`
   - `expires_at`

3. For `published_endpoint.audience.authn_mode` values `single-use-secret` and `shared-secret`:
   - `secret_handoff` is required,
   - `secret_handoff.expires_at` must not outlive `authority.expires_at`,
   - and session end/revocation is also the revocation boundary for the usable secret.

4. This means secret-gated temporary sharing stays one authority story:
   the session authority and the usable secret may travel on different lanes,
   but the secret does not become a longer-lived shadow grant.

5. Product-shape posture is fixed as follows:
   - **B (`workstation`)** and **C (`general_os`)** may still use secret-gated temporary sharing,
     but the secret must be visibly temporary in the same window as the publish session itself.
   - **A (`fleet_host`)** and **D (`appliance_factory`)** do not get to normalize “revoked share,
     still-valid secret” as an operational pattern.

## Consequences

- Receipts, support bundles, and explain surfaces can answer both *where the share was* and *when the
  usable secret stopped being valid* without opening the raw secret object.
- Secret-gated shares are less likely to decay into support folklore where the relay session expires
  but an old copied secret still works.
- The archive keeps using the existing secret lane instead of inventing a publish-specific token store.
- Implementations still have freedom on exact provider mechanics, but the evidence contract now says
  the secret lifetime cannot drift past the session authority.

## Why this is narrow enough

This ADR does **not** define:
- the exact revoke API for every relay provider,
- whether the secret is checked by the relay edge or the origin service,
- a universal unwrap UX,
- or a broader renewable-secret session family.

It only fixes the missing lifetime boundary: temporary publish-session secrets stay temporary in the
same authority window as the session that created them.
