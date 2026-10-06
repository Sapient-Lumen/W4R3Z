# ADR-0158: Publish-session secret consumption semantics

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
ADR-0157 then kept that handoff lifetime `session-authority-bounded` so the secret cannot outlive
the publish-session authority.

One expensive ambiguity still remained:

**what exactly does `single-use-secret` mean, and how is that different from `shared-secret`?**

Current systems already make the pressure visible:
- Vault response wrapping uses a single-use wrapping token,
- S3 presigned URLs can be reused until expiration,
- and many relay/share products leave the distinction buried in provider UX rather than the
  evidence object.

If DeriveBSD leaves that implicit, the archive pays for it later in retries, support, and policy:
operators cannot tell whether a copied secret should survive one successful admission, multiple
retries before success, or arbitrary reuse until expiry.

The archive needs one small answer that preserves secret-gated temporary sharing without inventing a
new secret session family.

## Decision

1. `published_endpoint.secret_handoff` now also records `consumption_posture`.

2. For `published_endpoint.audience.authn_mode = single-use-secret`:
   - `secret_handoff.consumption_posture = single-successful-admission`
   - the handoff secret is consumed by the first **successful admission**,
   - and failed or abandoned attempts before successful admission do not count as consumption.

3. For `published_endpoint.audience.authn_mode = shared-secret`:
   - `secret_handoff.consumption_posture = reusable-until-expiry`
   - the handoff secret may be reused until the earlier of expiry or revoke,
   - and it remains bounded by ADR-0157's `session-authority-bounded` lifetime rule.

4. This means the archive now distinguishes two secret-gated temporary-share stories:
   - **single-use recipient handoff**: one successful admission, then reissue if more access is needed
   - **reusable temporary secret**: multiple admissions allowed, but only inside the same bounded
     session authority window

5. Product-shape posture is fixed as follows:
   - **B (`workstation`)** and **C (`general_os`)** may use either posture explicitly, but the
     trusted UI and receipts must say which one was issued.
   - **A (`fleet_host`)** and **D (`appliance_factory`)** do not get to hide reusable access behind
     something labeled `single-use-secret`.

## Consequences

- Receipts, support bundles, and explain surfaces can answer whether a copied secret should still be
  expected to work after one successful admission.
- Retry and support flows become smaller: if the secret was `single-successful-admission`, any extra
  access needs a new publish session or a reissued handoff.
- `shared-secret` stays viable for webhook/callback style temporary sharing, but the archive no
  longer blurs it together with one-time recipient handoff.
- Implementations still have freedom on exact provider mechanics, but the evidence contract now
  says whether the handoff is consumed-on-success or reusable-until-expiry.

## Why this is narrow enough

This ADR does **not** define:
- the exact state machine for every relay provider,
- the exact event emitted when a secret is consumed,
- a universal retry ledger,
- or a new secret rotation subsystem.

It only fixes the missing semantics boundary: `single-use-secret` means one successful admission,
while `shared-secret` remains reusable only until the bounded session authority expires or is
revoked.
