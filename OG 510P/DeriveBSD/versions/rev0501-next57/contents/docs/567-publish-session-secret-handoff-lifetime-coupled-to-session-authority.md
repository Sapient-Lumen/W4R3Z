# Publish-session secret-handoff lifetime coupled to session authority

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already fixed five expensive ambiguities:

- temporary sharing is a separate relay-backed lane,
- the audience/publicness posture is explicit,
- the session is reboot-cleared with no auto-resume,
- public/org/support locators stay session-scoped,
- and secret-gated locators stay redacted with a separate secret handoff.

One quieter loophole still remained:

> if the usable share secret travels separately, can it quietly outlive the publish session that created it?

If the archive leaves that open, a revoked or expired publish session can still leave behind the real authority object.
See `adrs/ADR-0157-publish-session-secret-lifetime-coupled-to-session-authority.md`.

## The hard decision

Secret-gated publish sessions keep a **separate secret handoff**, but that handoff is now also **session-authority-bounded**.

When `published_endpoint.audience.authn_mode` is `single-use-secret` or `shared-secret`,
`published_endpoint.secret_handoff` must carry:

- `delivery = separate-secret-receipt`
- `secret_receipt_digest`
- `lifetime_binding = session-authority-bounded`
- `expires_at`

`secret_handoff.expires_at` must not outlive `authority.expires_at`.
The secret may live on the secret lane, but it does not become a longer-lived shadow grant.

## Required bindings

### Secret lifetime must stay inside session authority

For secret-gated publish sessions:

- the usable secret must expire no later than the publish-session authority,
- manual revoke of the session is also revoke of the secret handoff posture,
- and a reboot-cleared / no-auto-resume session does not get to leave behind a still-valid wrapped link or shared secret.

This keeps the authority story coherent even when the delivery mechanism is provider-specific.

### Separate handoff stays separate

This decision does **not** move the secret back into `net.publish.session`.
The receipt still carries only the digest join plus the bounded expiry summary.
The actual bearer material stays off the receipt/log/support-bundle surface. The follow-on
consumption rule in `docs/568-publish-session-secret-consumption-semantics-boundary.md` then says
whether the handoff was `single-successful-admission` or `reusable-until-expiry`.

## Why this matters operationally

ADR-0156 solved the *where does the secret go?* problem.
This doc solves the *how long does it stay valid?* problem.
Without it, the archive still teaches an incoherent pattern:

- the temporary share looks expired,
- the evidence says the session ended,
- but an old copied unwrap token or shared secret still works somewhere else.

That is exactly the kind of quiet drift that turns a temporary-sharing lane into accidental standing authority.

## Product-shape posture

### A — fleet host

If breakglass/support uses a temporary share secret at all, the secret must die with the session authority.
No separate longer-lived support token folklore.

### B — workstation

Trusted UI can still make secret-gated sharing ergonomic, but it must present the secret as co-temporary with the share.
“Share ended” and “secret still valid” cannot be two different truths.

### C — general OS

Admin/developer temporary sharing keeps the same boundary.
A copied secret from an earlier share must not survive the authority window that justified the share.

### D — appliance factory / regulatory

This keeps maintenance and audit stories coherent: evidence exports can prove the share ended without leaving behind a secret that effectively says otherwise.

## Schema surface

See:

- schema: `spec/net.publish.session.schema.json`
- example: `spec/examples/net.publish.session.json`
- joined secret evidence: `spec/secret.receipt.schema.json`

The schema now requires the following for secret-gated publish sessions:

- `published_endpoint.secret_handoff.lifetime_binding = session-authority-bounded`
- `published_endpoint.secret_handoff.expires_at`

The guardrail then enforces the cross-object rule that the secret handoff expiry must not outlive `authority.expires_at` in the canonical example and archive wording.

## Related docs

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md`
- `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`
- `docs/286-inbound-listen-broker-and-firewall-leases.md`
- `docs/460-inbound-listen-posture-by-profile.md`
- `docs/223-secrets-and-key-management-as-evidence.md`
- `docs/568-publish-session-secret-consumption-semantics-boundary.md`

Last updated: 2026-03-19r298
